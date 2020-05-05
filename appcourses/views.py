import json
import re
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.http import JsonResponse, Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_POST
from django.views.generic.base import ContextMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.utils.translation import gettext_lazy as _

from appaccounts.decorators import login_user_from_session
from .functions import enrolled, enroll_user_to_course, \
    get_context_from_question, get_completed_lessons, add_lesson_to_complete, update_exam_progress, \
    update_queryset_from_course_content, get_current_lesson, get_estimate_stars_list
from .models import Course, Module, Lesson, Content, Text, LessonQuiz, Video, File, Quiz, Question, QuizResult, Review
from .forms import LessonUpdateForm, ContentUpdateForm, CourseEnrollForm, QuizUpdateForm, \
    QuestionUpdateForm, CourseCreationForm, CourseUpdateForm, ModuleUpdateForm, CompleteLessonForm, \
    QuizCreationForm, QuizProgressForm
from .decorators import add_quiz_results, add_filter_pk_or_slug, add_module_content, add_course_content

from apppermission.functions import check_object_permission
from apppermission.decorators import check_user_group_for_view, object_permission_required
from PumpSkill.abstract_models import BreadCrumbType, BreadCrumb
from PumpSkill.functions import get_html_from_form_errors

from .models import BLANK_TRIGGER_START, BLANK_TRIGGER_END


class BaseContextData(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super(BaseContextData, self).get_context_data(**kwargs)
        context['base_css_path'] = settings.BASE_CSS_COURSE_PATH
        context['base_js_path'] = settings.BASE_JS_COURSE_PATH
        context['is_authenticated'] = self.request.user.is_authenticated
        if context['is_authenticated']:
            context['home_url'] = reverse_lazy('appmain:dashboard')
        else:
            context['home_url'] = reverse_lazy('appmain:index')
        return context


class LibraryListView(BaseContextData, ListView):
    model = Course
    template_name = 'appcourses/course/library.html'

    def get_context_data(self, **kwargs):
        context = super(LibraryListView, self).get_context_data(**kwargs)

        # context['hide_main_menu'] = True
        context['background_img'] = Course.background_img
        context['breadcrumbs'] = [BreadCrumb(BreadCrumbType.DASHBOARD, self.request.user),
                                  BreadCrumb(title='Библиотека курсов')]

        for course in self.object_list:
            course.estimate_stars = get_estimate_stars_list(course.total_estimate)
            if self.request.user.is_authenticated and course.user_lessons:
                course.user_current_lesson = course.user_lessons[0].lesson

        return context

    @add_course_content(add_modules=False, add_lessons=False, add_estimate=True, add_user_progress=True)
    def get_queryset(self):
        return super(LibraryListView, self).get_queryset()


class CourseDetailView(BaseContextData, DetailView):
    model = Course
    template_name = 'appcourses/course/overview.html'

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)

        # context['hide_main_menu'] = True
        context['enroll_form'] = CourseEnrollForm(initial={'course': self.object})
        context['user_enrolled'] = enrolled(user=self.request.user, course=self.object)
        context['background_img'] = Course.background_img
        current_lesson = get_current_lesson(self.request.user, self.object)
        if current_lesson:
            context['current_lesson'] = current_lesson
        else:
            context['first_lesson'] = self.object.module_list[0].lesson_list[0]#get_first_lesson()

        total_estimate = float(self.object.total_estimate or 0)
        context['total_estimate'] = round(total_estimate, 1)
        context['estimate_stars'] = get_estimate_stars_list(total_estimate)
        context['estimate_list'] = get_estimate_stars_list(total_estimate, True, self.object)
        for review_item in self.object.review_list:
            review_item.estimate_stars = get_estimate_stars_list(review_item.estimate)

        context['breadcrumbs'] = [BreadCrumb(BreadCrumbType.DASHBOARD, self.request.user), BreadCrumb(BreadCrumbType.COURSE_LIBRARY),
                                  BreadCrumb(title=self.object.title)]

        other_courses_id = Course.objects.filter(active=True).exclude(id=self.object.id).values('id')[:3]
        other_courses_qs = Course.objects.select_related('subject').filter(id__in=other_courses_id)
        other_courses = update_queryset_from_course_content(other_courses_qs, add_lessons=False, add_estimate=True)
        for other_course in other_courses:
            other_course.estimate_stars = get_estimate_stars_list(other_course.total_estimate)
        context['courses'] = other_courses

        return context

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.first()

    @add_course_content(add_estimate=True, add_detail_estimate=True, all_users_estimate=True)
    @add_filter_pk_or_slug
    def get_queryset(self):
        return super(CourseDetailView, self).get_queryset()


@require_POST
@login_user_from_session
@login_required
def enroll_to_course(request):
    form = CourseEnrollForm(request.POST)
    current_lesson = None
    if form.is_valid():
        current_lesson = enroll_user_to_course(request.user, form.cleaned_data['course'])
    if current_lesson:
        return redirect(current_lesson.get_absolute_url())
    else:
        return redirect('appcourses:library')


class LessonDetailView(BaseContextData, DetailView):
    model = Lesson
    template_name = 'appcourses/course/lesson_detail.html'

    def get_context_data(self, **kwargs):
        context = super(LessonDetailView, self).get_context_data(**kwargs)
        context['style'] = settings.STYLE_LESSON
        context['header'] = self.object.title

        if self.object.type == Lesson.QUIZ:
            context['type_quiz'] = True
            if not self.request.user.is_authenticated:
                context['block_message_header'] = self.object.title
                context['block_message'] = _('Прохождение тестов доступно только зарегистрированным пользователям')
            else:
                context['reset_url'] = self.object.get_absolute_url()
                context['quiz'] = self.object.quiz
                context['show_correct'] = True

                first_result = self.request.user.quiz_results.select_related('question').filter(
                    quiz=self.object.quiz).first()
                quiz_completed = False
                current_question = None

                if first_result:
                    current_question = first_result.question
                    quiz_completed = first_result.status == QuizResult.COMPLETED
                if not current_question:
                    current_question = self.object.quiz.get_first_question(not quiz_completed)

                context['quiz_completed'] = quiz_completed

                context.update(get_context_from_question(
                    **{'question': current_question, 'is_result': quiz_completed, 'user': self.request.user,
                       'quiz_completed': quiz_completed}))

        current_module = self.object.module
        course_queryset = Course.objects.filter(id=self.object.module.course.id)
        course_queryset = update_queryset_from_course_content(course_queryset, self.request.user)
        course_content = course_queryset.first()
        number_of_lesson = 1
        previous_lesson_url = ''
        next_lesson_url = ''
        previous_module = ''
        next_module = ''
        is_last_lesson = False
        is_last_module = False
        if current_module in course_content.module_list:
            index_module = course_content.module_list.index(current_module)
            current_module = course_content.module_list[index_module]
            if len(course_content.module_list) > index_module + 1:
                next_module = course_content.module_list[index_module + 1]
            if index_module > 0:
                previous_module = course_content.module_list[index_module - 1]
        is_last_module = not next_module
        if self.object in current_module.lesson_list:
            index_lesson = current_module.lesson_list.index(self.object)
            number_of_lesson = index_lesson + 1
            if len(current_module.lesson_list) > index_lesson + 1:
                next_lesson_url = current_module.lesson_list[index_lesson + 1].get_absolute_url()
                next_module = ''
            if index_lesson > 0:
                previous_lesson_url = current_module.lesson_list[index_lesson - 1].get_absolute_url()
                previous_module = ''
        if not next_lesson_url:
            is_last_lesson = True
            if next_module and len(next_module.lesson_list) > 0:
                next_lesson_url = next_module.lesson_list[0].get_absolute_url()
        if not previous_lesson_url and previous_module:
            if len(previous_module.lesson_list) > 0:
                previous_lesson_url = previous_module.lesson_list[0].get_absolute_url()

        context['course_content'] = course_content
        context['current_module'] = current_module
        context['module_lesson_count'] = current_module.lesson_count
        context['number_of_lesson'] = number_of_lesson
        context['previous_lesson_url'] = previous_lesson_url
        context['next_lesson_url'] = next_lesson_url
        context['previous_module'] = previous_module
        context['next_module'] = next_module
        context['completed_lessons'] = get_completed_lessons(self.request.user, course=current_module.course)
        if self.object.type != Lesson.QUIZ:
            lesson_contents = self.object.get_contents()
            if lesson_contents:
                context['contents'] = lesson_contents[0]
            else:
                context['contents'] = ''

        review_url = current_module.get_review_url()
        context['review_url'] = review_url
        context['review_course_url'] = current_module.course.get_review_url()

        context['complete_lesson_form'] = CompleteLessonForm(initial={'lesson': self.object})
        context['title'] = _('Курс') + ' ' + current_module.course.title + ' Урок ' + self.object.title

        context['is_lesson'] = True
        context['is_last_lesson'] = is_last_lesson
        context['is_module_review'] = False
        context['is_last_module'] = is_last_module
        context['next_post_url'] = reverse('appcourses:complete_lesson')
        if is_last_lesson and review_url:
            context['next_url'] = review_url
            context['next_post_url'] += f'?next={review_url}'
        elif next_lesson_url:
            context['next_url'] = next_lesson_url
            context['next_post_url'] += f'?next={next_lesson_url}'
        # else:
        #     context['next_post_url'] += f'?next={current_module.course.get_review_url()}'

        return context

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        lesson = queryset.select_related('quiz', 'module', 'module__course').first()

        if self.request.method == 'GET':
            if self.request.user.is_authenticated and lesson.type == Lesson.QUIZ:
                if not self.request.user.quiz_results.filter(quiz=lesson.quiz):
                    update_exam_progress(
                        **{'user': self.request.user, 'quiz': lesson.quiz, 'request': self.request,
                           'status': QuizResult.PROGRESS,
                           'question': lesson.quiz.get_first_question(random=True), })

        return lesson

    @add_filter_pk_or_slug
    def get_queryset(self):
        return super(LessonDetailView, self).get_queryset()


class ModuleReviewView(BaseContextData, DetailView):
    model = Module
    template_name = 'appcourses/course/lesson_detail.html'

    def post(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated:
            user_review = request.user.reviews.filter(module=self.get_object()).first()
            if not user_review:
                user_review = Review(user=request.user, module=self.get_object())
            user_review.text = request.POST.get('comment', '').strip()
            user_review.estimate = int(request.POST.get('estimate', 0))
            user_review.save()
            messages.info(self.request, _('Спасибо! Твой отзыв принят'))
            return super(ModuleReviewView, self).get(request, *args, **kwargs)
        else:
            raise Http404(_('Такой страницы не существует'))

    def get_context_data(self, **kwargs):
        context = super(ModuleReviewView, self).get_context_data(**kwargs)

        context['style'] = settings.STYLE_LESSON
        context['title'] = _('Отзыв о курсе') + ' ' + self.object.course.title + '/' + self.object.title
        context['header'] = _('Как тебе модуль') + ' ' + self.object.title + '?'
        context['review_url'] = self.object.get_review_url()
        context['is_review'] = True
        if not self.request.user.is_authenticated:
            context['block_message_header'] = _('Отзыв о модуле')
            context['block_message'] = _('Отзывы могут оставлять только зарегистрированные пользователи')
        else:
            context['user_review'] = self.request.user.reviews.filter(module=self.object).first()

        course_queryset = Course.objects.filter(id=self.object.course.id)
        course_queryset = update_queryset_from_course_content(course_queryset, self.request.user)
        course_content = course_queryset.first()

        context['course_content'] = course_content
        context['current_module'] = self.object
        context['completed_lessons'] = get_completed_lessons(self.request.user, course=self.object.course)
        previous_lesson = self.object.get_last_lesson()
        if previous_lesson:
            context['previous_lesson_url'] = previous_lesson.get_absolute_url()
        next_lesson = self.object.get_first_lesson_next_module()
        if next_lesson:
            context['next_lesson_url'] = next_lesson.get_absolute_url()
            context['next_module'] = True
        else:
            context['next_lesson_url'] = self.object.course.get_review_url()

        context['is_last_module'] = len(course_content.module_list) == course_content.module_list.index(self.object) + 1
        context['review_course_url'] = self.object.course.get_review_url()
        context['avatar_estimate_1'] = Review.avatar_estimate_1
        context['avatar_estimate_2'] = Review.avatar_estimate_2
        context['avatar_estimate_3'] = Review.avatar_estimate_3

        return context

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.first()

    @add_module_content()
    @add_filter_pk_or_slug
    def get_queryset(self):
        return super(ModuleReviewView, self).get_queryset()


class CourseReviewView(BaseContextData, DetailView):
    model = Course
    template_name = 'appcourses/course/lesson_detail.html'

    def post(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated:
            user_review = request.user.reviews.filter(course=self.get_object()).first()
            if not user_review:
                user_review = Review(user=request.user, course=self.get_object())
            user_review.module = None
            user_review.text = request.POST.get('comment', '').strip()
            user_review.estimate = int(request.POST.get('estimate', 0))
            user_review.save()
            messages.info(self.request, _('Спасибо! Твой отзыв принят'))
            return super(CourseReviewView, self).get(request, *args, **kwargs)
        else:
            raise Http404(_('Такой страницы не существует'))

    def get_context_data(self, **kwargs):
        context = super(CourseReviewView, self).get_context_data(**kwargs)
        context['style'] = settings.STYLE_LESSON
        context['title'] = _('Отзыв о курсе') + ' ' + self.object.title
        context['header'] = _('Курс') + ' ' + self.object.title
        context['is_review'] = False
        context['is_course_review'] = True

        if not self.request.user.is_authenticated:
            context['block_message_header'] = _('Отзыв о курсе')
            context['block_message'] = _('Отзывы могут оставлять только зарегистрированные пользователи')
        else:
            user_review = self.request.user.reviews.filter(course=self.object).first()
            if user_review:
                context['user_review'] = user_review
                context['user_estimate_stars'] = get_estimate_stars_list(user_review.estimate)

        current_module = self.object.module_list[len(self.object.module_list) - 1]
        context['course_content'] = self.object
        context['current_module'] = current_module
        context['completed_lessons'] = get_completed_lessons(self.request.user, course=self.object)
        context['previous_lesson_url'] = current_module.get_review_url()
        context['review_url'] = context['previous_lesson_url']
        context['review_course_url'] = self.object.get_review_url()
        context['is_last_module'] = True
        total_estimate = float(self.object.total_estimate or 0)
        context['total_estimate'] = round(total_estimate, 1)
        context['avatar_star'] = Review.avatar_star
        context['avatar_star_outline'] = Review.avatar_star_outline
        context['estimate_stars'] = get_estimate_stars_list(total_estimate)
        context['estimate_list'] = get_estimate_stars_list(total_estimate, True, self.object)

        return context

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.first()

    @add_course_content(add_estimate=True, add_detail_estimate=True, estimate_only_active=False)
    @add_filter_pk_or_slug
    def get_queryset(self):
        return super(CourseReviewView, self).get_queryset()


@login_required
@require_POST
def complete_lesson(request):
    result = False
    form = CompleteLessonForm(request.POST)
    if form.is_valid():
        result = add_lesson_to_complete(request.user, form.cleaned_data['lesson'])
    next = request.GET.get('next')
    if next:
        return redirect(next)
    return JsonResponse({'result': result})


class ExamOverview(BaseContextData, DetailView):
    model = Quiz
    template_name = 'appcourses/quiz/exam_overview.html'

    def get_context_data(self, **kwargs):
        context = super(ExamOverview, self).get_context_data(**kwargs)
        context['form'] = QuizProgressForm(initial={'quiz_id': self.object.id})
        context['breadcrumbs'] = [BreadCrumb(BreadCrumbType.DASHBOARD, self.request.user),
                                  BreadCrumb(BreadCrumbType.COURSE_LIBRARY),
                                  BreadCrumb(title=self.object.title)]
        return context

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.first()

    @add_quiz_results(add_result_description=True)
    @add_filter_pk_or_slug
    def get_queryset(self):
        return super(ExamOverview, self).get_queryset()


class ExamProgress(LoginRequiredMixin, DetailView):
    model = Quiz
    template_name = 'appcourses/quiz/exam_progress.html'

    def post(self, request, *args, **kwargs):
        quiz = self.get_object()
        if update_exam_progress(**{'user': self.request.user,
                                   'quiz': quiz,
                                   'request': request,
                                   'status': QuizResult.PROGRESS,
                                   'question': quiz.get_first_question(random=True),
                                   }):
            return redirect(quiz.get_progress_url())
        else:
            return redirect(quiz.get_absolute_url())

    def get(self, request, *args, **kwargs):
        first_result = self.request.user.quiz_results.filter(quiz=self.get_object()).first()
        if not first_result or first_result.status == QuizResult.COMPLETED:
            return redirect(self.get_object().get_results_url())
        return super(ExamProgress, self).get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ExamProgress, self).get_context_data(**kwargs)
        context['base_css_path'] = settings.BASE_CSS_COURSE_PATH
        context['base_js_path'] = settings.BASE_JS_COURSE_PATH
        context['hide_main_menu'] = True
        context['hide_footer'] = True
        context['question_number'] = 0
        context['next_question'] = None
        context['quiz_questions_count'] = self.object.questions.filter(active=True).count()
        context['check_url'] = reverse_lazy('appcourses:check_answer')
        context['reset_url'] = self.object.get_progress_url()
        context['exit_url'] = self.object.get_absolute_url()
        context['quiz'] = self.object
        context['show_correct'] = True
        first_result = self.request.user.quiz_results.select_related('question').filter(quiz=self.object).first()
        quiz_completed = False
        current_question = None

        if first_result:
            current_question = first_result.question
            quiz_completed = first_result.status == QuizResult.COMPLETED
        if not current_question:
            current_question = self.object.get_first_question(not quiz_completed)

        context['quiz_completed'] = quiz_completed

        context.update(get_context_from_question(
            **{'question': current_question, 'is_result': quiz_completed, 'user': self.request.user,
               'quiz_completed': quiz_completed}))

        return context

    @add_filter_pk_or_slug
    def get_queryset(self):
        return super(ExamProgress, self).get_queryset()


class ManageCourseCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'appcourses.add_course'
    model = Course
    form_class = CourseCreationForm
    template_name = 'appcourses/manage/course/create_update.html'

    @check_user_group_for_view(settings.GROUP_MANAGER)
    def get(self, request, *args, **kwargs):
        return super(ManageCourseCreateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ManageCourseCreateView, self).get_context_data(**kwargs)

        context['base_css_path'] = settings.BASE_CSS_COURSE_PATH
        context['base_js_path'] = settings.BASE_JS_COURSE_PATH
        context['profile'] = self.request.user.profile
        context['is_manager'] = self.request.user.profile.is_manager
        context['active'] = False
        context['creation'] = True
        context['model'] = 'course'
        context['post_url'] = reverse_lazy('appcourses:manage_course_create')
        context['title'] = 'Создание нового курса'
        context['subtitle'] = ''
        context['breadcrumbs'] = [BreadCrumb(title='Новый курс')]

        return context

    def form_valid(self, form):
        super(ManageCourseCreateView, self).form_valid(form)
        messages.success(self.request, "Курс создан. Можно создавать модули")
        return JsonResponse({'response': reverse('appmain:dashboard_manage')})

    def form_invalid(self, form):
        errors = get_html_from_form_errors(form)
        return JsonResponse({'response': 'error', 'errors': errors})


class ManageUpdate(PermissionRequiredMixin, UpdateView):
    template_name = 'appcourses/manage/course/create_update.html'

    @check_user_group_for_view(settings.GROUP_MANAGER)
    def get(self, request, *args, **kwargs):
        return super(ManageUpdate, self).get(request, *args, **kwargs)

    @object_permission_required()
    @check_user_group_for_view(settings.GROUP_MANAGER)
    def post(self, request, *args, **kwargs):
        return super(ManageUpdate, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ManageUpdate, self).get_context_data(**kwargs)

        context['section'] = 'courses'
        context['model'] = self.object._meta.model_name
        context['base_css_path'] = settings.BASE_CSS_COURSE_PATH
        context['base_js_path'] = settings.BASE_JS_COURSE_PATH
        context['profile'] = self.request.user.profile
        context['is_manager'] = self.request.user.profile.is_manager
        context['creation'] = False
        context['active'] = self.object.active
        if not isinstance(self.object, Question):
            context['slug'] = self.object.slug
        context['post_url'] = self.object.get_manage_url()
        context['public_url'] = self.object.get_change_public_url()

        return context

    def form_invalid(self, form):
        errors = get_html_from_form_errors(form)
        return JsonResponse({'response': 'error', 'errors': errors})


class ManageCourseUpdateView(ManageUpdate):
    permission_required = 'appcourses.change_course'
    model = Course
    form_class = CourseUpdateForm

    def get_context_data(self, **kwargs):
        context = super(ManageCourseUpdateView, self).get_context_data(**kwargs)

        context['contents'] = self.object.modules.all()
        context['title'] = self.object.title
        context['subtitle'] = 'редактирование курса'
        context['breadcrumbs'] = [BreadCrumb(BreadCrumbType.DASHBOARD_MANAGE),
                                  BreadCrumb(title=self.object.title)]

        return context

    def form_valid(self, form):
        json_contents = self.request.POST.get('contents')
        if json_contents:
            contents = json.loads(json_contents)
            for content in contents:
                content_id = content['id']
                new_content = None
                deleted = False
                if content_id:
                    if 'new' in content['id']:
                        content_qs = None
                    else:
                        content_qs = Module.objects.filter(id=content['id'], course=self.object)
                    if not content_qs:
                        if not content['remove']:
                            new_content = Module()
                        else:
                            deleted = True
                    else:
                        new_content = content_qs[0]
                        if content['remove']:
                            deleted = True
                if not deleted:
                    new_content.course = self.object
                    new_content.title = content['title']
                    new_content.order = content['order']
                    new_content.save()

        super(ManageCourseUpdateView, self).form_valid(form)
        messages.success(self.request, "Данные успешно сохранены")
        return JsonResponse({'response': self.object.get_manage_url()})


class ManageModuleUpdateView(ManageUpdate):
    permission_required = 'appcourses.change_module'
    model = Module
    form_class = ModuleUpdateForm

    def get_context_data(self, **kwargs):
        context = super(ManageModuleUpdateView, self).get_context_data(**kwargs)

        context['contents'] = self.object.lessons.all()
        context['course'] = self.object.course
        context['title'] = f'Модуль {self.object.title}'
        context['subtitle'] = f'курс {self.object.course}'
        context['breadcrumbs'] = [BreadCrumb(BreadCrumbType.DASHBOARD_MANAGE),
                                  BreadCrumb(object=self.object.course, mode='admin'),
                                  BreadCrumb(title=self.object.title)]

        return context

    def form_valid(self, form):
        json_contents = self.request.POST.get('contents')
        if json_contents:
            contents = json.loads(json_contents)
            for content in contents:
                content_id = content['id']
                new_content = None
                deleted = False
                if content_id:
                    if 'new' in content['id']:
                        content_qs = None
                    else:
                        content_qs = Lesson.objects.filter(id=content['id'], module=self.object)
                    if not content_qs:
                        if not content['remove']:
                            new_content = Lesson()
                        else:
                            deleted = True
                    else:
                        new_content = content_qs[0]
                        if content['remove']:
                            deleted = True
                if not deleted:
                    new_content.module = self.object
                    new_content.title = content['title']
                    new_content.order = content['order']
                    if 'new' in content['id']:
                        content_type = Lesson.LESSON
                        if str(content['type']) == '2':
                            content_type = Lesson.QUIZ
                        new_content.type = content_type
                    new_content.save()

        super(ManageModuleUpdateView, self).form_valid(form)
        messages.success(self.request, "Данные успешно сохранены")
        return JsonResponse({'response': self.object.get_manage_url()})


class ManageLessonUpdateView(ManageUpdate):
    permission_required = 'appcourses.change_lesson'
    model = Lesson
    form_class = LessonUpdateForm

    def get_context_data(self, **kwargs):
        context = super(ManageLessonUpdateView, self).get_context_data(**kwargs)

        context['contents'] = self.object.contents.all()
        context['module'] = self.object.module
        context['title'] = f'Урок {self.object.title}'
        context['subtitle'] = f'модуль {self.object.module}'
        context['breadcrumbs'] = [BreadCrumb(BreadCrumbType.DASHBOARD_MANAGE),
                                  BreadCrumb(object=self.object.module.course, mode='admin'),
                                  BreadCrumb(object=self.object.module, mode='admin'),
                                  BreadCrumb(title=self.object.title)]

        return context

    def form_valid(self, form):
        json_contents = self.request.POST.get('contents')
        if json_contents:
            contents = json.loads(json_contents)
            for content in contents:
                content_id = content['id']
                new_content = None
                new_content_item = None
                deleted = False
                if content_id:
                    if 'new' in content['id']:
                        content_qs = None
                    else:
                        content_qs = Content.objects.filter(id=content['id'], lesson=self.object)
                    if not content_qs:
                        if not content['remove']:
                            new_content = Content()
                        else:
                            deleted = True
                    else:
                        new_content = content_qs[0]
                        if content['remove']:
                            deleted = True
                if not deleted:
                    new_content.lesson = self.object
                    new_content.order = content['order']
                    if 'new' in content['id']:
                        content_model = Text
                        if str(content['type']) == '2':
                            content_model = LessonQuiz
                        elif str(content['type']) == '3':
                            content_model = Video
                        elif str(content['type']) == '4':
                            content_model = File
                        new_content_item = content_model.objects.create(owner=self.request.user, title=content['title'])
                        new_content_item.save()
                        new_content.item = new_content_item
                    new_content.save()

        super(ManageLessonUpdateView, self).form_valid(form)
        messages.success(self.request, "Данные успешно сохранены")
        return JsonResponse({'response': self.object.get_manage_url()})


class ManageContentUpdateView(ManageUpdate):
    permission_required = 'appcourses.change_content'
    model = Content
    form_class = ContentUpdateForm
    template_name = 'appcourses/manage/course/content_update.html'

    def get_context_data(self, **kwargs):
        context = super(ManageContentUpdateView, self).get_context_data(**kwargs)

        context['lesson'] = self.object.lesson
        context['title'] = f'Контент {self.object.item.title}'
        context['subtitle'] = f'урок {self.object.lesson}'
        context['description_HTML_JSON'] = self.object.get_description_html()
        context['type_text'] = self.object.item._meta.model_name == 'text'
        context['type_video'] = self.object.item._meta.model_name == 'video'
        context['type_quiz'] = self.object.item._meta.model_name == 'lessonquiz'
        context['breadcrumbs'] = [BreadCrumb(BreadCrumbType.DASHBOARD_MANAGE),
                                  BreadCrumb(object=self.object.lesson.module.course, mode='admin'),
                                  BreadCrumb(object=self.object.lesson.module, mode='admin'),
                                  BreadCrumb(object=self.object.lesson, mode='admin'),
                                  BreadCrumb(title=self.object.item.title)]

        return context

    def form_valid(self, form):
        self.object.item.title = self.request.POST.get('title')
        if self.object.item._meta.model_name == 'text':
            self.object.item.description_HTML = self.request.POST.get('text_format')
        if self.object.item._meta.model_name == 'video':
            self.object.item.url = self.request.POST.get('video_url')
        if self.object.item._meta.model_name == 'lessonquiz':
            quiz_id = self.request.POST.get('quiz', '')
            if quiz_id:
                self.object.item.quiz = Quiz.objects.get(id=quiz_id)
        self.object.item.save()
        super(ManageContentUpdateView, self).form_valid(form)
        messages.success(self.request, "Данные успешно сохранены")
        return JsonResponse({'response': self.object.get_manage_url()})


class ManagePublic(PermissionRequiredMixin, UpdateView):
    http_method_names = ['post']

    @object_permission_required('public')
    @check_user_group_for_view(settings.GROUP_MANAGER)
    def post(self, request, *args, **kwargs):
        object = self.get_object()
        object.active = not object.active
        object.save()
        if object.active:
            messages.success(self.request, "Объект опубликован и доступен на сайте!")
        else:
            messages.success(self.request, "Объект снят с публикации!")
        if check_object_permission(request.user, object):
            return redirect(object.get_manage_url())
        else:
            return redirect(reverse('appmain:dashboard_manage'))


class ManageCoursePublicView(ManagePublic):
    model = Course
    permission_required = 'appcourses.change_course'


class ManageModulePublicView(ManagePublic):
    model = Module
    permission_required = 'appcourses.change_module'


class ManageLessonPublicView(ManagePublic):
    model = Lesson
    permission_required = 'appcourses.change_lesson'


class ManageContentPublicView(ManagePublic):
    model = Content
    permission_required = 'appcourses.change_lesson'


class ManageQuizCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'appcourses.add_quiz'
    model = Quiz
    form_class = QuizCreationForm
    template_name = 'appcourses/manage/course/create_update.html'

    @check_user_group_for_view(settings.GROUP_MANAGER)
    def get(self, request, *args, **kwargs):
        return super(ManageQuizCreateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ManageQuizCreateView, self).get_context_data(**kwargs)

        context['section'] = 'quizzes'
        context['base_css_path'] = settings.BASE_CSS_COURSE_PATH
        context['base_js_path'] = settings.BASE_JS_COURSE_PATH
        context['profile'] = self.request.user.profile
        context['is_manager'] = self.request.user.profile.is_manager
        context['active'] = False
        context['creation'] = True
        context['model'] = 'quiz'
        context['post_url'] = reverse_lazy('appcourses:manage_quiz_create')
        context['title'] = 'Создание нового теста'
        context['subtitle'] = ''
        context['breadcrumbs'] = [BreadCrumb(BreadCrumbType.DASHBOARD_MANAGE), BreadCrumb(title='Новый тест')]

        return context

    def form_valid(self, form):
        super(ManageQuizCreateView, self).form_valid(form)
        messages.success(self.request, "Тест создан. Можно создавать вопросы")
        return JsonResponse({'response': reverse('appmain:dashboard_manage_section', args=['quizzes'])})

    def form_invalid(self, form):
        errors = get_html_from_form_errors(form)
        return JsonResponse({'response': 'error', 'errors': errors})


class ManageQuizUpdateView(ManageUpdate):
    permission_required = 'appcourses.change_quiz'
    model = Quiz
    form_class = QuizUpdateForm

    def get_context_data(self, **kwargs):
        context = super(ManageQuizUpdateView, self).get_context_data(**kwargs)

        context['section'] = 'quizzes'
        context['contents'] = self.object.questions.all()
        context['title'] = f'Тест {self.object.title}'
        context['subtitle'] = 'редактирование теста'
        context['breadcrumbs'] = [BreadCrumb(BreadCrumbType.DASHBOARD_MANAGE),
                                  BreadCrumb(BreadCrumbType.QUIZZES_MANAGE),
                                  BreadCrumb(title=self.object.title)]

        return context

    def form_valid(self, form):
        json_contents = self.request.POST.get('contents')
        if json_contents:
            contents = json.loads(json_contents)
            for content in contents:
                content_id = content['id']
                new_content = None
                deleted = False
                if content_id:
                    if 'new' in content['id']:
                        content_qs = None
                    else:
                        content_qs = Question.objects.filter(id=content['id'], quiz=self.object)
                    if not content_qs:
                        if not content['remove']:
                            new_content = Question()
                        else:
                            deleted = True
                    else:
                        new_content = content_qs[0]
                        if content['remove']:
                            deleted = True
                if not deleted:
                    new_content.order = content['order']
                    if 'new' in content['id']:
                        content_type = Question.SINGLE
                        if str(content['type']) == '2':
                            content_type = Question.MULTIPLE
                        elif str(content['type']) == '3':
                            content_type = Question.CODE
                        new_content.owner = self.request.user
                        new_content.quiz = self.object
                        new_content.title = content['title']
                        new_content.type = content_type
                    new_content.save()

        super(ManageQuizUpdateView, self).form_valid(form)
        messages.success(self.request, "Данные успешно сохранены")
        return JsonResponse({'response': self.object.get_manage_url()})


class ManageQuestionUpdateView(ManageUpdate):
    permission_required = 'appcourses.change_quiz'
    model = Question
    form_class = QuestionUpdateForm

    def get_context_data(self, **kwargs):
        context = super(ManageQuestionUpdateView, self).get_context_data(**kwargs)

        variants = self.object.variants
        contents = []
        if variants:
            variants_list = json.loads(self.object.variants)
            for variant in variants_list:
                contents.append({'title': variant['title'], 'active': variant['correct']})
        context['contents'] = contents
        context['section'] = 'quizzes'
        context['title'] = f'Вопрос {self.object.title}'
        context['subtitle'] = f'Тест {self.object.quiz.title}'
        context['code_HTML_JSON'] = self.object.code
        context['expected_result_HTML_JSON'] = self.object.expected_result
        context['blank_trigger_start'] = BLANK_TRIGGER_START
        context['blank_trigger_end'] = BLANK_TRIGGER_END
        context['need_expected_result'] = self.object.need_expected_result
        context['breadcrumbs'] = [BreadCrumb(BreadCrumbType.DASHBOARD_MANAGE),
                                  BreadCrumb(object=self.object.quiz, mode='admin'),
                                  BreadCrumb(title=self.object.title)]

        return context

    def form_valid(self, form):

        variants = []

        if self.object.type == Question.CODE:
            # len_trigger_start = len(BLANK_TRIGGER_START)
            # code_format = self.request.POST.get('code_format')
            # expected_result = self.request.POST.get('expected_result_format')
            # need_expected_result = self.request.POST.get('need_expected_result')
            # if not code_format:
            #     code_format = self.get_object().code
            # if not expected_result:
            #     expected_result = self.get_object().expected_result
            # if not need_expected_result:
            #     need_expected_result = self.get_object().need_expected_result
            # else:
            #     need_expected_result = True if str(need_expected_result) == '1' else False
            # if code_format:
            #     code_format_dict = json.loads(code_format)
            #     if 'ops' in code_format_dict:
            #         ops = code_format_dict['ops']
            #         for item in ops:
            #             if 'insert' in item:
            #                 insert_text = item['insert']
            #                 positions = (m.start() for m in re.finditer(BLANK_TRIGGER_START, insert_text))
            #                 if positions:
            #                     for position in positions:
            #                         position_start = insert_text.find(BLANK_TRIGGER_START, position)
            #                         position_end = insert_text.find(BLANK_TRIGGER_END, position + len_trigger_start)
            #                         if position_start != -1 and position_end != -1:
            #                             blank_value = insert_text[position_start + len_trigger_start:position_end]
            #                             variants.append({'title': blank_value, 'correct': True})
            len_trigger_start = len(BLANK_TRIGGER_START)
            code_format = form.cleaned_data['code']
            expected_result = form.cleaned_data['expected_result']
            need_expected_result = self.request.POST.get('need_expected_result')
            if not code_format:
                code_format = self.get_object().code
            if not expected_result:
                expected_result = self.get_object().expected_result
            if not need_expected_result:
                need_expected_result = self.get_object().need_expected_result
            else:
                need_expected_result = True if str(need_expected_result) == '1' else False
            if code_format:
                positions = (m.start() for m in re.finditer(BLANK_TRIGGER_START, code_format))
                if positions:
                    for position in positions:
                        position_start = code_format.find(BLANK_TRIGGER_START, position)
                        position_end = code_format.find(BLANK_TRIGGER_END, position + len_trigger_start)
                        if position_start != -1 and position_end != -1:
                            blank_value = code_format[position_start + len_trigger_start:position_end]
                            variants.append({'title': blank_value.strip(), 'correct': True})
            self.object.code = code_format
            self.object.expected_result = expected_result
            self.object.need_expected_result = need_expected_result
        else:
            json_contents = self.request.POST.get('contents')
            if json_contents:
                contents = json.loads(json_contents)
                correct_is_there = False
                for content in contents:
                    if not content['remove']:
                        correct = False
                        if str(content['type']) == '1':
                            correct = True
                            if self.object.type == Question.SINGLE and correct_is_there:
                                correct = False
                            correct_is_there = True
                        variants.append({'title': content['title'], 'correct': correct})

        self.object.variants = json.dumps(variants)
        self.object.save()

        super(ManageQuestionUpdateView, self).form_valid(form)
        messages.success(self.request, "Данные успешно сохранены")
        return JsonResponse({'response': self.object.get_manage_url()})


class ManageQuizPublicView(ManagePublic):
    model = Quiz
    permission_required = 'appcourses.change_quiz'


class ManageQuestionPublicView(ManagePublic):
    model = Question
    permission_required = 'appcourses.change_quiz'
