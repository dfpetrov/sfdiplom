import json
import random
import re
from django.contrib import messages
from django.db.models import Count, Q, Prefetch, Sum, Max, Subquery, OuterRef, F, FloatField, IntegerField, Value
from django.db.models.functions import Cast
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .forms import QuizProgressForm
from .models import Course, Module, Lesson, CourseEnroll, CurrentLesson, CompletedLesson, Quiz, QuizResult, \
    QuestionResult, Question, Review
from .models import BLANK_TRIGGER_START, BLANK_TRIGGER_END


def enrolled(user, course):
    if not user:
        return False
    if not user.is_authenticated:
        return False
    if not course:
        return False
    return user.courses_enroll.filter(course=course).exists()


def enroll_user_to_course(user, course):
    if not course:
        return None
    if not user:
        return None
    if not user.is_authenticated:
        return None
    if not CourseEnroll.objects.filter(course=course, user=user).exists():
        first_lesson = course.get_first_lesson()
        if first_lesson:
            record = CourseEnroll.objects.create(course=course, user=user)
            record.save()
            user.current_lessons.filter(lesson__module__course=course).delete()
            record = CurrentLesson.objects.create(lesson=first_lesson, user=user)
            record.save()
            return first_lesson
    else:
        current_lessons = user.current_lessons.filter(course=course).first()
        if current_lessons:
            return current_lessons.lesson


def add_lesson_to_complete(user, lesson):
    if not lesson:
        return False
    if not user:
        return False
    if not user.is_authenticated:
        return False

    user_completed_lessons = user.completed_lessons.filter(lesson__module__course=lesson.module.course).values_list(
        'lesson', flat=True)

    if lesson.id not in user_completed_lessons:
        record = CompletedLesson.objects.create(lesson=lesson, user=user)
        record.save()

        next_lesson = lesson.next_lesson
        if next_lesson:
            user.current_lessons.filter(lesson__module__course=lesson.module.course).delete()
            record = CurrentLesson.objects.create(lesson=next_lesson, course=lesson.module.course, user=user)
            record.save()

    return True


def get_course_content(courses=None, meta_list=None, active=True):
    module_count = None
    lesson_count = None
    prefetch = None
    if meta_list:
        if 'module_count' in meta_list:
            if active:
                module_count = Count('modules', distinct=True, filter=Q(modules__active=True))
            else:
                module_count = Count('modules', distinct=True)
        if 'lesson_count' in meta_list:
            if active:
                lesson_count = Count('modules__lessons', distinct=True, filter=Q(modules__lessons__active=True))
            else:
                lesson_count = Count('modules__lessons', distinct=True)
        if 'modules' in meta_list and 'lessons' in meta_list:
            lessons = Lesson.objects
            modules = Module.objects
            if active:
                lessons = lessons.filter(active=True)
                modules = modules.filter(active=True)
            else:
                module_count = Count('modules', distinct=True)
                lesson_count = Count('modules__lessons', distinct=True)
            prefetch_lessons = Prefetch('lessons', queryset=lessons, to_attr='lesson_list')
            modules = modules.prefetch_related(prefetch_lessons)
            prefetch = Prefetch('modules', queryset=modules, to_attr='module_list')
        elif 'modules' in meta_list:
            modules = Module.objects
            if active:
                modules = modules.filter(active=True)
            prefetch = Prefetch('modules', queryset=modules, to_attr='module_list')
        elif 'lessons' in meta_list:
            lessons = Lesson.objects
            if active:
                lessons = lessons.filter(active=True)
            prefetch = Prefetch('modules__lessons', queryset=lessons, to_attr='lesson_list')
    else:
        lessons = Lesson.objects
        modules = Module.objects

        if active:
            module_count = Count('modules', distinct=True, filter=Q(modules__active=True))
            lesson_count = Count('modules__lessons', distinct=True, filter=Q(modules__lessons__active=True))
            modules_lesson_count = Count('lessons', distinct=True, filter=Q(lessons__active=True))
            lessons = lessons.filter(active=True)
            modules = modules.filter(active=True)
        else:
            module_count = Count('modules', distinct=True)
            lesson_count = Count('modules__lessons', distinct=True)
            modules_lesson_count = Count('lessons', distinct=True)

        prefetch_lessons = Prefetch('lessons', queryset=lessons, to_attr='lesson_list')
        modules = modules.prefetch_related(prefetch_lessons).annotate(lesson_count=modules_lesson_count)
        prefetch = Prefetch('modules', queryset=modules, to_attr='module_list')

    qs = Course.objects

    if prefetch:
        qs = qs.prefetch_related(prefetch)

    if courses:
        if isinstance(courses, Course):
            qs = qs.filter(id=courses.id)
        elif type(courses) == list:
            qs = qs.filter(id_in=courses)
        elif type(courses) == str:
            qs = qs.filter(id=courses)
        else:
            qs = qs.filter(id_in=[item.id for item in courses])

    if active:
        qs = qs.filter(active=True)

    if module_count:
        qs = qs.annotate(module_count=module_count)

    if lesson_count:
        qs = qs.annotate(lesson_count=lesson_count)

    if qs.count() == 1:
        return qs[0]
    else:
        return qs


def get_completed_lessons(user, course=None, module=None):
    if (not course and not module) or not user:
        return []
    if not user.is_authenticated:
        return []
    qs = []
    if module:
        qs = user.completed_lessons.select_related('lesson').filter(lesson__module=module)
    if course:
        qs = user.completed_lessons.select_related('lesson').filter(lesson__module__course=course)
    if qs:
        return [item.lesson for item in qs]
    return []


def get_course_completion(user, courses=None):
    if not courses:
        courses_enroll = user.courses_enroll.filter(course__active=True)
        courses_filter = [item.course for item in courses_enroll]
    elif isinstance(courses, Course):
        courses_filter = [courses]
    elif courses.model == CourseEnroll:
        courses_filter = [item.course for item in courses]
    elif type(courses) == list:
        pass
    elif type(courses) == str:
        pass

    qs = Course.objects.filter(pk__in=[item.pk for item in courses_filter]).annotate(
        lesson_count=Count('modules__lessons'))
    if qs:
        completed_lessons = user.completed_lessons.select_related('lesson__module', 'lesson__module__course').filter(
            lesson__module__course__in=courses_filter)
        courses_completed_lessons = []
        for completed_lesson in completed_lessons:
            add = False
            for item in courses_completed_lessons:
                if item['course'] == completed_lesson.lesson.module.course:
                    item['count'] += 1
                    add = True
                    break
            if not add:
                courses_completed_lessons.append({'course': completed_lesson.lesson.module.course, 'count': 1})
        for course in qs:
            course_lesson_count = course.lesson_count
            course_lesson_complete_count = 0

            for item in courses_completed_lessons:
                if item['course'] == course:
                    course_lesson_complete_count = item['count']

            if course_lesson_complete_count == 0:
                course_completion = 0
            else:
                course_completion = round(course_lesson_complete_count / course_lesson_count * 100)

            if course_completion == 100:
                prefix = _('курс пройден')
                course_completion_display = f'{prefix} {course_completion}%'
            elif course_completion == 0:
                course_completion_display = ''
            elif course_completion < 50:
                prefix = _('пройдено')
                course_completion_display = f'{prefix} {course_completion}%'
            else:
                prefix = _('осталось')
                course_completion_display = f'{prefix} {100 - course_completion}%'

            course.completion = course_completion
            course.completion_display = course_completion_display

    if qs:
        return qs
    else:
        return []


# def update_queryset_from_course_results(queryset, user, *args, **kwargs):
#     queryset_updated = queryset
#
#     complete_lesson_count = Count('modules__lessons__completed_lessons', filter=Q(lesson__active=True) & Q(user=user))
#     active_lesson_count = Count('modules__lessons', distinct=True,
#                                 filter=Q(modules__active=True) & Q(modules__lessons__active=True))
#
#     queryset_updated = queryset_updated.annotate(lesson_count=active_lesson_count)
#
#     return queryset_updated


def update_queryset_from_user_results(queryset, user, add_question_results=False, add_result_description=False,
                                      add_user_answer=False):
    queryset_updated = queryset

    active_question_count = Count('questions', distinct=True, filter=Q(questions__active=True))

    if user.is_authenticated:

        correct_question_count = Count('questions__user_question_results', distinct=True,
                                       filter=(Q(questions__user_question_results__user=user)
                                               & Q(questions__active=True)
                                               & Q(questions__user_question_results__correct=True)))

        user_score_sum = Sum('questions__score', filter=(Q(questions__user_question_results__user=user)
                                                         & Q(questions__active=True)
                                                         & Q(questions__user_question_results__correct=True)))

        complete_date = Subquery(QuizResult.objects.filter(
            Q(quiz=OuterRef('pk')) & Q(user=user) & Q(status=QuizResult.COMPLETED)).values(
            'quiz').annotate(complete_date=Max('updated')).values('complete_date')[:1])
    else:
        correct_question_count = Cast(Value(0), IntegerField())
        user_score_sum = Cast(Value(0), IntegerField())
        complete_date = Cast(Value(0), IntegerField())

    active_question_total_score = Subquery(Question.objects.filter(
            Q(quiz=OuterRef('pk')) & Q(active=True)).values(
            'quiz').order_by('quiz').annotate(total_score=Sum('score')).values('total_score')[:1])

    queryset_updated = queryset_updated.filter(active=True, questions__active=True)

    if add_question_results and user.is_authenticated:
        question_results = QuestionResult.objects.filter(Q(user=user))
        prefetch_results = Prefetch('user_question_results', queryset=question_results, to_attr='results')

        active_questions = Question.objects.filter(Q(active=True)).prefetch_related(prefetch_results)
        prefetch_questions = Prefetch('questions', queryset=active_questions, to_attr='active_questions')

        queryset_updated = queryset_updated.prefetch_related(prefetch_questions)

    queryset_updated = queryset_updated.annotate(question_count=active_question_count,
                                                 correct_count=correct_question_count,
                                                 total_score=active_question_total_score,
                                                 user_score=user_score_sum,
                                                 complete_date=complete_date)

    if add_result_description or add_question_results:
        for quiz in queryset_updated:
            if add_result_description:
                quiz.result_description = quiz.get_result_description(quiz.user_score,
                                                                      quiz.total_score,
                                                                      quiz.complete_date)
            if add_question_results:
                for active_question in quiz.active_questions:
                    answer_is_correct = False
                    answer_list = []
                    answer_code = ''
                    if active_question.results:
                        result = active_question.results[0]
                        answer_is_correct = result.correct
                        if add_user_answer and result.answer:
                            answer_list = json.loads(result.answer)
                            answer_code = result.answer_code
                    active_question.correct = bool(answer_is_correct)
                    active_question.type_code = active_question.type == Question.CODE
                    if add_user_answer:
                        active_question.user_answer_list = answer_list
                        active_question.variants_len = len(json.loads(active_question.variants))
                        if active_question.type == Question.CODE:
                            active_question.user_answer_code = answer_code if answer_code else active_question.code

    return queryset_updated


def update_queryset_from_course_content(queryset, user=None, only_active=True, add_modules=True, add_lessons=True,
                                        add_user_progress=False, add_estimate=False, add_detail_estimate=False,
                                        estimate_only_active=True, all_users_estimate=False):
    queryset_updated = queryset
    prefetch_lessons = None
    prefetch_modules = None

    if only_active:
        queryset_updated = queryset.filter(modules__active=True, modules__lessons__active=True)
        module_count = Count('modules', distinct=True, filter=Q(modules__active=True))
        lesson_count = Count('modules__lessons', distinct=True,
                             filter=Q(modules__active=True) & Q(modules__lessons__active=True))
        if add_lessons:
            prefetch_lessons = Prefetch('lessons', queryset=Lesson.objects.filter(active=True), to_attr='lesson_list')
        if add_modules:
            if prefetch_lessons is not None:
                modules_lesson_count = Count('lessons', distinct=True, filter=Q(lessons__active=True))
                prefetch_modules = Prefetch('modules', queryset=Module.objects.filter(active=True).prefetch_related(
                    prefetch_lessons).annotate(lesson_count=modules_lesson_count), to_attr='module_list')
            else:
                prefetch_modules = Prefetch('modules', queryset=Module.objects.filter(active=True),
                                            to_attr='module_list')
    else:
        module_count = Count('modules', distinct=True)
        lesson_count = Count('modules__lessons', distinct=True)
        if add_lessons:
            prefetch_lessons = Prefetch('lessons', queryset=Lesson.objects, to_attr='lesson_list')
        if add_modules:
            if prefetch_lessons is not None:
                modules_lesson_count = Count('lessons', distinct=True)
                prefetch_modules = Prefetch('modules',
                                            queryset=Module.objects.prefetch_related(prefetch_lessons).annotate(
                                                lesson_count=modules_lesson_count), to_attr='module_list')
            else:
                prefetch_modules = Prefetch('modules', queryset=Module.objects, to_attr='module_list')

    if add_modules:
        queryset_updated = queryset_updated.prefetch_related(prefetch_modules)

    queryset_updated = queryset_updated.annotate(module_count=module_count, lesson_count=lesson_count)

    if add_user_progress:
        if user.is_authenticated:
            complete_lesson_count = Count('modules__lessons__completed_lessons', distinct=True,
                                          filter=Q(
                                              modules__lessons__completed_lessons__lesson__module__active=True) & Q(
                                              modules__lessons__completed_lessons__lesson__active=True) & Q(
                                              modules__lessons__completed_lessons__user=user))
        else:
            complete_lesson_count = Cast(Value(0), IntegerField())

        queryset_updated = queryset_updated.annotate(complete_lesson_count=complete_lesson_count).annotate(
            user_progress=F('complete_lesson_count') / F('lesson_count') * 100)

        if user.is_authenticated:
            current_lessons_qs = CurrentLesson.objects.filter(lesson__active=True, user=user).select_related(
                'lesson__module')
            prefetch_current_lessons = Prefetch('current_lessons', queryset=current_lessons_qs, to_attr='user_lessons')
            queryset_updated = queryset_updated.prefetch_related(prefetch_current_lessons)

    if add_estimate:
        filter_review = Q(reviews__module=None)
        filter_subquery = Q(course=OuterRef('pk')) & Q(module=None)

        review_objects = Review.objects.select_related('user__profile')
        if estimate_only_active:
            filter_review = filter_review & Q(reviews__active=True)
            filter_subquery = filter_subquery & Q(active=True)
            prefetch_reviews = Prefetch('reviews', queryset=review_objects.filter(active=True), to_attr='review_list')
        else:
            prefetch_reviews = Prefetch('reviews', queryset=review_objects, to_attr='review_list')

        if all_users_estimate:
            queryset_updated = queryset_updated.prefetch_related(prefetch_reviews)

        estimate_count = Count('reviews', distinct=True, filter=filter_review)
        estimate_sum = Subquery(
            Review.objects.filter(filter_subquery).values(
                'course').annotate(total_estimate=Sum('estimate')).values('total_estimate')[:1])
        queryset_updated = queryset_updated.annotate(estimate_count=estimate_count,
                                                     estimate_sum=estimate_sum).annotate(
            total_estimate=Cast(F('estimate_sum'), FloatField()) / Cast(F('estimate_count'), FloatField()))
        if add_detail_estimate:
            estimate_count1 = Count('reviews', distinct=True,
                                    filter=filter_review & Q(reviews__estimate=1))
            estimate_count2 = Count('reviews', distinct=True,
                                    filter=filter_review & Q(reviews__estimate=2))
            estimate_count3 = Count('reviews', distinct=True,
                                    filter=filter_review & Q(reviews__estimate=3))
            estimate_count4 = Count('reviews', distinct=True,
                                    filter=filter_review & Q(reviews__estimate=4))
            estimate_count5 = Count('reviews', distinct=True,
                                    filter=filter_review & Q(reviews__estimate=5))

            queryset_updated = queryset_updated.annotate(estimate_count1=estimate_count1,
                                                         estimate_count2=estimate_count2,
                                                         estimate_count3=estimate_count3,
                                                         estimate_count4=estimate_count4,
                                                         estimate_count5=estimate_count5)

    return queryset_updated


def update_queryset_from_module_content(queryset, only_active=True):
    queryset_updated = queryset

    if only_active:
        lesson_count = Count('lessons', distinct=True, filter=Q(lessons__active=True))
        prefetch_lessons = Prefetch('lessons', queryset=Lesson.objects.filter(active=True), to_attr='lesson_list')
    else:
        lesson_count = Count('lessons', distinct=True)
        prefetch_lessons = Prefetch('lessons', queryset=Lesson.objects, to_attr='lesson_list')

    return queryset_updated.prefetch_related(prefetch_lessons).annotate(lesson_count=lesson_count)


def pars_queryset_fields(queryset, *args):
    for item in queryset:
        for arg in args:
            item[arg] = json.dumps(item[arg])
    return queryset


def update_exam_progress(**kwargs):
    user = kwargs.get('user', None)
    quiz = kwargs.get('quiz', None)
    request = kwargs.get('request', None)
    status = kwargs.get('status', None)
    question = kwargs.get('question', None)
    time_spent = kwargs.get('time_spent', None)
    time_left = kwargs.get('time_left', None)
    del_user_question_results = kwargs.get('del_user_question_results', True)
    if not user or not user.is_authenticated:
        if request:
            messages.info(request, _('Прохождение тестов доступно только зарегистрированным пользователям'))
        return False
    quiz_results = user.quiz_results.filter(quiz=quiz)
    if not quiz_results.exists():
        record = QuizResult()
    else:
        record = quiz_results.first()
        if del_user_question_results:
            user.user_question_results.filter(question__quiz=quiz).delete()
    record.user = user
    record.quiz = quiz
    record.status = status
    record.question = question
    if time_left:
        record.time_left = time_left
    elif time_spent:
        time_left = record.time_left - time_spent + 1
        record.time_left = time_left if time_left > 0 else 0
    elif quiz.time_type == Quiz.TIME_TYPE_QUIZ:
        record.time_left = quiz.duration
    record.save()
    return True


def get_time_left(user, question):
    if not user or not user.is_authenticated:
        return 0
    first_result = user.quiz_results.filter(quiz=question.quiz).first()
    if first_result:
        if question.quiz.time_type == Quiz.TIME_TYPE_QUIZ:
            return first_result.time_left
        elif question.quiz.time_type == Quiz.TIME_TYPE_QUESTION or question.duration > 0:
            return question.duration
    return 0


def get_format_code(**kwargs):
    mode = kwargs.get('mode', None)
    style = kwargs.get('style', '')
    header = kwargs.get('header', '')
    need_safe = kwargs.get('need_safe', False)
    code = kwargs.get('code', '')
    blank_list = kwargs.get('blank_list', [])
    mark_correct = kwargs.get('mark_correct', False)
    id_prefix = kwargs.get('id_prefix', '')
    language = kwargs.get('language', '')

    prefix = ''
    postfix = ''

    if not code:
        code = ''

    if style == 'pre':
        prefix = f'<pre><code class="{language}">'
        postfix = '</code></pre>'
        need_safe = True
    elif style == 'raised':
        prefix = f'<pre class="card card--raised card--elevated"><code class="p-3 {language}">'
        postfix = '</code></pre>'
        need_safe = True
    elif style == 'card':
        need_safe = True
        prefix = '<div class="card">'
        if header:
            prefix += '<div class="card-header d-flex align-items-center py-2" style="background-color: #f3e2bb; color: #bd7342; border-bottom: none;">'
            prefix += f'<p class="text-monospace my-0">{header}</p>'
            prefix += '</div>'
        prefix += '<div class="card-body m-0 p-0">'
        prefix += '<pre class="my-0" style="border-bottom-left-radius: 0.25rem; border-bottom-right-radius: 0.25rem;">'
        prefix += f'<code class="{language}">'
        postfix = '</code></pre></div></div>'

    if need_safe:
        code = code.replace('<', '&lt;')

    if blank_list or mode == 'input':

        tag_input = ''
        if mode == 'input':
            tag_input = f'<input type="text" id="$blank_id" name="user-answer{id_prefix}" class="form-input my-1 text-monospace $blank_class" $blank_value style="max-width: $mwpx" autocomplete="off" $r $maxlength>'

        if kwargs.get('answer', False):
            tag_input += '<input type="text" id="$answer_id" value="$answer_value" readonly hidden>'

        if kwargs.get('readonly', False):
            tag_input = tag_input.replace('$r', 'readonly')
        else:
            tag_input = tag_input.replace('$r', '')

        len_trigger_start = len(BLANK_TRIGGER_START)
        len_trigger_end = len(BLANK_TRIGGER_END)

        positions = (m.start() for m in re.finditer(BLANK_TRIGGER_START, code))
        i = 0
        if positions:
            position_start = -1
            blank_list_len = len(blank_list)
            for position in positions:
                if blank_list and i >= blank_list_len:
                    break
                position_start = code.find(BLANK_TRIGGER_START, position_start + 1)
                position_end = code.find(BLANK_TRIGGER_END, position_start + 1)
                if position_start != -1 and position_end != -1:
                    if blank_list and i < blank_list_len:
                        blank_value = blank_list[i]['title'].strip()
                    else:
                        blank_value = code[position_start + len_trigger_start:position_end].strip()

                    code_before = code[0:position_start]
                    code_after = code[position_end + len_trigger_end:]

                    if mode == 'input':
                        if mark_correct:
                            extra_id = f'{id_prefix}mc_'
                        else:
                            extra_id = id_prefix
                        tag_value = tag_input.replace('$mw', str(len(blank_value) * 10 + 30))
                        tag_value = tag_value.replace('$maxlength', f'maxlength="{str(len(blank_value) + 10)}"')
                        tag_value = tag_value.replace('$blank_id', f'{extra_id}questionBlank{i}')
                        tag_value = tag_value.replace('$answer_value', blank_value)
                        tag_value = tag_value.replace('$answer_id', f'{extra_id}questionBlank{i}Answer')
                        if mark_correct:
                            tag_value = tag_value.replace('$blank_value', f'value="{blank_value}"')
                            if i < blank_list_len and blank_list[i]['correct']:
                                tag_value = tag_value.replace('$blank_class', 'answer-form-correct')
                            else:
                                tag_value = tag_value.replace('$blank_class', 'answer-form-incorrect')
                        else:
                            tag_value = tag_value.replace('$blank_value', '')
                            tag_value = tag_value.replace('$blank_class', '')
                    else:
                        tag_value = BLANK_TRIGGER_START + blank_value + BLANK_TRIGGER_END

                    code = code_before + tag_value + code_after

                i += 1

    return prefix + code + postfix


def get_context_from_question(**kwargs):
    question = kwargs.get('question', None)
    is_result = kwargs.get('is_result', None)
    user_answers = kwargs.get('user_answers', [])
    user_answer_is_correct = kwargs.get('user_answer_is_correct', None)
    answer_code = kwargs.get('answer_code', None)
    user = kwargs.get('user', None)
    show_correct = kwargs.get('show_correct', '')
    quiz_completed = kwargs.get('quiz_completed', '')
    quiz = kwargs.get('quiz', '')
    reset_url = kwargs.get('reset_url', '')
    time_left = kwargs.get('time_left', '')
    exit_url = kwargs.get('exit_url', '')

    if not quiz and question:
        quiz = question.quiz

    if not show_correct or show_correct == '0':
        show_correct = False
    else:
        show_correct = True

    context = {'question': question, 'variants': [], 'disabled': '',
               'questions_result_avatar': Question.avatar_hourglass(), 'is_result': is_result,
               'check_url': reverse_lazy('appcourses:check_answer')}

    if is_result:
        if question:
            if not user_answers or question.type == Question.code:
                user_answer = user.user_question_results.filter(question=question).first()
                if user_answer:
                    user_answer_is_correct = user_answer.correct
                    user_answers = json.loads(user_answer.answer)
                    if not answer_code and user_answer.answer_code:
                        answer_code = user_answer.answer_code
                    else:
                        answer_code = get_format_code(code=question.code, need_safe=True, blank_list=user_answers)

        context['variants'] = user_answers
        if show_correct:
            for variant in context['variants']:
                if variant['checked']:
                    border = 'border-left-success' if variant['correct'] else 'border-left-danger'
                    variant['extra_class'] = f'border-left-4 {border}'
                # if question.type == Question.SINGLE:
                variant['show_correct_badge'] = variant['correct'] == variant['checked']

        context['code'] = get_format_code(code=answer_code, style='raised', mode='input', readonly=1, mark_correct=True,
                                          blank_list=user_answers)
        context['disabled'] = 'disabled' if question.type != Question.CODE else ''
        if user_answer_is_correct:
            context['questions_result_avatar'] = Question.avatar_answer_correct()
        else:
            context['questions_result_avatar'] = Question.avatar_answer_incorrect()
    elif question:
        question_variants = json.loads(question.variants)
        context['variants'] = random.sample(question_variants, len(question_variants))
        context['code'] = get_format_code(code=question.code, style='raised', mode='input')

    if question:
        context['form'] = QuizProgressForm(initial={'question_id': question.id})
        context['input_type'] = 'radio' if question.type == Question.SINGLE else 'checkbox'
        context['type_code'] = question.type == Question.CODE
        if question.need_expected_result:
            context['expected_result'] = get_format_code(code=question.expected_result, style='card',
                                                         header='Ожидаемый результат', language='python-repl')

        context['quiz_questions_count'] = question.quiz.questions.filter(active=True).count()
        context['question_number'] = user.user_question_results.filter(
            question__quiz=question.quiz).count() + 1
        context['progress'] = round(((context['question_number'] - 1) / context['quiz_questions_count']) * 100)

    context['need_countdown'] = question is not None and question.need_countdown
    if context['need_countdown']:
        context['time_left'] = get_time_left(user, question)

    if quiz_completed and quiz:
        user_result = get_quiz_result_description_for_user(quiz, user)
        context['user_result'] = user_result
        if user_result.result_description['cup_avatar']:
            context['questions_result_avatar'] = user_result.result_description['cup_avatar']

    if reset_url:
        context['reset_url'] = reset_url
    if exit_url:
        context['exit_url'] = exit_url
    if time_left:
        context['time_left'] = int(time_left) + 1

    return context


def get_quiz_result_description_for_user(quiz, user):
    if quiz and user:
        return update_queryset_from_user_results(Quiz.objects.filter(id=quiz.id), user,
                                                 add_result_description=True).first()
    return None


def get_current_lesson(user, course=None):
    if user.is_authenticated:
        if course:
            current_lesson = user.current_lessons.filter(lesson__module__course=course,
                                                         lesson__active=True,
                                                         lesson__module__active=True,
                                                         lesson__module__course__active=True)
        else:
            current_lesson = user.current_lessons.filter(lesson__active=True)
        current_lesson = current_lesson.select_related('lesson', 'lesson__module__course')
        if current_lesson:
            return current_lesson.first().lesson

    return None


def get_courses_enroll(user, **kwargs):
    flat_id = kwargs.get('flat_id', False)
    active = kwargs.get('active', True)
    if user.is_authenticated:
        queryset = user.courses_enroll
        if active:
            queryset = queryset.filter(course__active=True)
        if flat_id:
            queryset = queryset.values('course_id')
        return queryset
    return None


def get_quiz_results(user, **kwargs):
    active = kwargs.get('active', True)
    quiz_type = kwargs.get('quiz_type', None)
    flat_id = kwargs.get('flat_id', False)
    if user.is_authenticated:
        queryset = user.quiz_results.select_related('quiz')
        if active:
            queryset = queryset.filter(quiz__active=True)
        if quiz_type:
            queryset = queryset.filter(quiz__type=quiz_type)
        if flat_id:
            queryset = queryset.values('quiz_id')
        return queryset
    return None


def get_user_power(user):
    if user.is_authenticated:
        # return user.profile.score
        return user.profile.created
    return 0


def get_estimate_stars_list(total_estimate, full_list=False, course=None):
    estimate_list = []
    if full_list:
        estimate_count = course.estimate_count
        if estimate_count:
            estimates = (course.estimate_count5, course.estimate_count4, course.estimate_count3,
                         course.estimate_count2, course.estimate_count1)
            estimate_list = []
            for k, v in enumerate(estimates):
                stars = ['star' if k <= i else 'star_border' for i in range(4, -1, -1)]
                estimate_list.append({'percent': round(v / estimate_count * 100), 'stars': stars})
        else:
            estimate_list = [0, 0, 0, 0, 0]
    else:
        if total_estimate:
            for i in range(5):
                if total_estimate >= i + 1:
                    estimate_list.append('star')
                elif total_estimate > i:
                    estimate_list.append('star_half')
                else:
                    estimate_list.append('star_border')
        else:
            for i in range(5):
                estimate_list.append('star_border')
    return estimate_list
