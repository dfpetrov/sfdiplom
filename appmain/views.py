from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.base import ContextMixin, TemplateResponseMixin, View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.utils.translation import gettext_lazy as _

from appcourses.models import Course, Quiz, Review
from apporders.models import Order
from apptasks.models import Skill

from apptasks import functions as TaskFunctions
from apporders import functions as OrderFunctions

from appaccounts.functions import create_user
from apppermission.decorators import check_user_group_for_view
from appcourses.functions import get_format_code, update_queryset_from_user_results, \
    update_queryset_from_course_content, get_estimate_stars_list, get_current_lesson, get_courses_enroll, \
    get_quiz_results, get_user_power
from appcourses.decorators import add_quiz_results, filter_user_quizzes, add_filter_pk_or_slug

from PumpSkill.abstract_models import BreadCrumbType, BreadCrumb


@login_required
def dashboard(request, *args, **kwargs):
    section = 'main'

    if 'section' not in kwargs:
        return redirect('appmain:dashboard_section', section='main')
    else:
        section = kwargs['section']

    section_template_name = f'appmain/dashboard_sections/{section}.html'

    # section: current course
    first_course = None
    course_in_progress = None
    current_lesson = get_current_lesson(request.user)
    courses_enroll_id = get_courses_enroll(request.user, flat_id=True)
    if not courses_enroll_id:
        if current_lesson:
            first_course = current_lesson.module.course
        else:
            first_course = Course.objects.filter(active=True).first()
        if first_course:
            courses_enroll_id = [first_course.id]
    courses_enroll = update_queryset_from_course_content(Course.objects.filter(id__in=courses_enroll_id),
                                                         user=request.user, only_active=True, add_modules=False,
                                                         add_lessons=False, add_user_progress=True, add_estimate=True)

    for course_enroll in courses_enroll:
        course_enroll.estimate_stars = get_estimate_stars_list(course_enroll.total_estimate)

    if not first_course:
        if not current_lesson:
            if not courses_enroll:
                first_course = Course.objects.filter(active=True).first()
            else:
                first_course = courses_enroll.first()
        else:
            first_course = current_lesson.module.course

    if first_course:
        course_in_progress = update_queryset_from_course_content(Course.objects.filter(id=first_course.id),
                                                                 user=request.user, add_user_progress=True,
                                                                 add_estimate=True).select_related('subject').first()

    if not current_lesson and first_course:
        current_lesson = first_course.get_first_lesson()

    # section: my achievements
    quiz_list = get_quiz_results(request.user, quiz_type=Quiz.EXAM, flat_id=True)
    if quiz_list:
        quiz_queryset = Quiz.objects.filter(id__in=quiz_list)
    else:
        quiz_queryset = Quiz.objects.filter(active=True, type=Quiz.EXAM)
    quizzes_results = update_queryset_from_user_results(quiz_queryset, request.user, add_result_description=True)

    power = get_user_power(request.user)
    if not power:
        power = _('в начале пути')

    context = {'base_css_path': settings.BASE_CSS_COURSE_PATH, 'base_js_path': settings.BASE_JS_COURSE_PATH,
               'section': section, 'section_template_name': section_template_name,
               'course_in_progress': course_in_progress, 'current_lesson': current_lesson,
               'courses_enroll': courses_enroll,
               'enroll': course_in_progress in courses_enroll,
               'quizzes_results': quizzes_results,
               'quizzes_results_count': quizzes_results.count(), 'power': power}

    return render(request, section_template_name, context)


@login_required
def dashboard_task(request):
    request_user = request.user

    context = {
        'order_href_title_prefix': settings.ORDER_HREF_TITLE_PREFIX,
        'task_href_title_prefix': settings.TASK_HREF_TITLE_PREFIX,
        'skill_href_title_prefix': settings.SKILL_HREF_TITLE_PREFIX,
    }

    # list of new task:
    kwargs = {
        'filter_author': '!=',
        'author': request_user,
        'filter_order': '-',
        'add_author_data': True,
        'add_skill_data': True,
        'add_fl_count': True,
        'count': 5,
    }
    context['new_tasks'] = TaskFunctions.get_task_list(**kwargs)

    # list of user's tasks:
    kwargs['filter_author'] = '=='
    kwargs['filter_order'] = None
    context['my_tasks'] = TaskFunctions.get_task_list(**kwargs)

    # lis of user's orders
    kwargs = {
        'filter_user': '==',
        'user': request_user,
        'add_skill_data': True,
        'count': 5,
    }
    context['user_orders'] = OrderFunctions.get_order_list(**kwargs)

    # list of favourite tasks
    context['task_favourites'] = TaskFunctions.get_favourites_task_list(user=request_user, count=5)

    # list of favourite orders
    context['order_favourites'] = OrderFunctions.get_favourites_order_list(user=request_user, count=5)

    return render(request, 'appmain/dashboard.html', context)


class DashboardManage(LoginRequiredMixin, TemplateResponseMixin, View):
    http_method_names = ['get']
    template_name = 'appmain/dashboard_manage.html'

    @check_user_group_for_view(settings.GROUP_MANAGER)
    def get(self, request, *args, **kwargs):

        profile = request.user.profile
        is_manager = profile.is_manager

        if not is_manager:
            raise PermissionDenied

        section = 'courses'

        if 'section' in kwargs:
            section = kwargs['section']
        else:
            return redirect('appmain:dashboard_manage_section', section=section)

        section_template_name = f'appmain/dashboard_sections/manage/{section}.html'

        all_courses = Course.objects.all()

        context = {
            'base_css_path': settings.BASE_CSS_COURSE_PATH,
            'base_js_path': settings.BASE_JS_COURSE_PATH,
            'profile': profile,
            'section': section,
            'section_template_name': section_template_name,
            'all_courses': all_courses,
            'is_manager': is_manager,
        }

        if section == 'quizzes':
            context['design_version'] = 'v2'
            context['base_css_path'] = 'v2/_base_css_v2.html'
            context['base_js_path'] = 'v2/_base_js_v2.html'
            context['preloader_path'] = 'v2/_preloader.html'
            context['page_head'] = 'Управление тестами'
            context['quizzes_exam'] = Quiz.objects.filter(type=Quiz.EXAM).all()
            context['quizzes_lesson'] = Quiz.objects.filter(type=Quiz.LESSON).all()
            context['quizzes_common'] = Quiz.objects.filter(type=Quiz.COMMON).all()
            context['breadcrumbs'] = [BreadCrumb(BreadCrumbType.DASHBOARD_MANAGE), BreadCrumb(title='Тесты')]

        return self.render_to_response(context)


def main_page(request):
    context = {
        'base_css_path': settings.BASE_CSS_COURSE_PATH,
        'base_js_path': settings.BASE_JS_COURSE_PATH,
        'style_index': True,
    }

    courses_qs = Course.objects.select_related('subject').filter(active=True)
    courses = update_queryset_from_course_content(courses_qs, add_lessons=False, add_modules=False, add_estimate=True)
    for course in courses:
        course.estimate_stars = get_estimate_stars_list(course.total_estimate)
    context['courses'] = courses
    reviews = Review.objects.filter(active=True, module=None).exclude(course=None).select_related('user__profile')[:6]
    for review in reviews:
        review.estimate_stars = get_estimate_stars_list(review.estimate)
    context['review_list'] = reviews

    continue_learning_text = ''
    continue_learning_url = ''
    if request.user.is_authenticated:
        context['is_authenticated'] = True
        continue_learning_text = _('Продолжить обучение')
        continue_learning_url = reverse_lazy('appmain:dashboard')
    else:
        context['is_authenticated'] = False
        username_from_session = request.session.get(settings.SESSION_USERNAME_KEY, '')
        if username_from_session:
            continue_learning_text = _('Продолжить обучение')
            continue_learning_url = reverse_lazy('appaccounts:login_user', args=[str(username_from_session)])
        else:
            continue_learning_text = _('Начать обучение')
            continue_learning_url = reverse_lazy('appaccounts:create_new_user')
    context['continue_learning_text'] = continue_learning_text
    context['continue_learning_url'] = continue_learning_url

    return render(request, 'appmain/index.html', context)


class SkillList(ListView):
    model = Skill
    template_name = 'appmain/skill_list.html'
    paginate_by = 50

    def get_paginate_by(self, queryset):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        return self.paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        skills = []
        skill_list = Skill.objects.all()
        for skill in skill_list:
            data = {
                'title': skill.title,
                'description': skill.description,
                'description_min': skill.description_min,
                'url': skill.get_absolute_url
            }
            if skill.avatar:
                data['avatar'] = skill.avatar.url
            else:
                data['avatar'] = ''
            skills.append(data)

        # пагинация
        page_size = self.get_paginate_by(skills)
        if page_size:
            paginator, page, skills, is_paginated = self.paginate_queryset(
                skills, page_size)
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': skills
            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': skills
            }

        context['skills'] = skills

        return context


class MyOrderListView(ListView):
    model = Order
    template_name = 'appmain/myorder_list.html'
    paginate_by = 50

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """
        Декорируем диспетчер функцией login_required, чтобы запретить просмотр отображения неавторизованными
        пользователями
        """
        return super(MyOrderListView, self).dispatch(request, *args, **kwargs)

    def get_paginate_by(self, queryset):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        return self.paginate_by

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # lis of user's orders
        kwargs = {
            'filter_user': '==',
            'user': self.request.user,
            'add_task_data': True,
            'add_skill_data': True,
        }
        order_list = OrderFunctions.get_order_list(**kwargs)

        # пагинация
        page_size = self.get_paginate_by(order_list)
        if page_size:
            paginator, page, order_list, is_paginated = self.paginate_queryset(
                order_list, page_size)
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': order_list
            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': order_list
            }

        context['order_count'] = len(order_list)
        context['orders'] = order_list

        return context


class BaseContextData(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super(BaseContextData, self).get_context_data(**kwargs)
        context['base_css_path'] = settings.BASE_CSS_COURSE_PATH
        context['base_js_path'] = settings.BASE_JS_COURSE_PATH
        context['section'] = 'main'
        power = get_user_power(self.request.user)
        if not power:
            power = _('в начале пути')
        context['power'] = power
        return context


class QuizResults(LoginRequiredMixin, BaseContextData, DetailView):
    model = Quiz
    template_name = 'appmain/dashboard_sections/quiz_results.html'

    def get_context_data(self, **kwargs):
        context = super(QuizResults, self).get_context_data(**kwargs)
        context['page_title'] = f'Результаты теста {self.object.title}'
        for active_question in self.object.active_questions:
            if active_question.type_code:
                active_question.code_for_question = get_format_code(code=active_question.code,
                                                                    style='raised',
                                                                    mode='input',
                                                                    answer=True,
                                                                    readonly=1,
                                                                    id_prefix=active_question.id)
                active_question.expected_result_code = get_format_code(code=active_question.expected_result,
                                                                       style='card', language='python-repl',
                                                                       header='Ожидаемый результат')
                active_question.user_answer_code = get_format_code(code=active_question.user_answer_code,
                                                                   style='raised',
                                                                   mode='input',
                                                                   readonly=1,
                                                                   mark_correct=True,
                                                                   blank_list=active_question.user_answer_list,
                                                                   id_prefix=active_question.id)

        context['breadcrumbs'] = [BreadCrumb(BreadCrumbType.DASHBOARD, self.request.user),
                                  BreadCrumb(BreadCrumbType.MY_ACHIEVEMENTS),
                                  BreadCrumb(title=self.object.title)]

        return context

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.first()

    @add_quiz_results(add_question_results=True, add_result_description=True, add_user_answer=True)
    @add_filter_pk_or_slug
    def get_queryset(self):
        return super(QuizResults, self).get_queryset()


class MyAchievements(LoginRequiredMixin, BaseContextData, ListView):
    model = Quiz
    template_name = 'appmain/dashboard_sections/my_achievements.html'

    def get_context_data(self, **kwargs):
        context = super(MyAchievements, self).get_context_data(**kwargs)
        context['page_title'] = 'Мои достижения'
        context['breadcrumbs'] = [BreadCrumb(BreadCrumbType.DASHBOARD, self.request.user),
                                  BreadCrumb(title='Мои достижения')]

        return context

    @add_quiz_results(add_result_description=True, add_question_results=True)
    @filter_user_quizzes
    def get_queryset(self):
        queryset = super(MyAchievements, self).get_queryset()
        return queryset.filter(type=Quiz.EXAM)


class Exams(LoginRequiredMixin, BaseContextData, ListView):
    model = Quiz
    template_name = 'appmain/dashboard_sections/exams.html'

    def get_context_data(self, **kwargs):
        context = super(Exams, self).get_context_data(**kwargs)
        context['page_title'] = 'Все испытания'
        context['breadcrumbs'] = [BreadCrumb(BreadCrumbType.DASHBOARD, self.request.user),
                                  BreadCrumb(BreadCrumbType.MY_ACHIEVEMENTS),
                                  BreadCrumb(title='Испытания')]

        return context

    @add_quiz_results(add_result_description=True)
    def get_queryset(self):
        queryset = super(Exams, self).get_queryset()
        return queryset.filter(type=Quiz.EXAM)
