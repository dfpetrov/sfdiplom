import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from .models import Question, QuizResult, QuestionResult, Quiz, BLANK_TRIGGER_START, BLANK_TRIGGER_END
from .functions import update_exam_progress, get_format_code, get_context_from_question


@login_required
@require_POST
def check_answer(request):
    result_check = {'result': False, 'correct_variants': '', 'next_question_id': ''}
    user_answers_json = request.POST.get('user_answers', '')
    mode_exit = request.POST.get('mode_exit', False)
    question_id = request.POST.get('question_id', '')
    time_left = json.loads(request.POST.get('time_left', ''))
    reset_url = request.POST.get('reset_url', '')
    exit_url = request.POST.get('exit_url', '')
    if not time_left:
        time_left = 0
    question = get_object_or_404(Question, id=question_id)
    user_answers = []
    next_question = None
    answer_code = ''
    user_answer_is_correct = True
    if request.user and request.user.is_authenticated and not mode_exit:
        if user_answers_json:
            user_answers = json.loads(user_answers_json)
        if user_answers:
            for user_answer in user_answers:
                user_answer['correct'] = False
        score = 0
        if question:
            variants_json = question.variants
            if variants_json:
                variants = json.loads(variants_json)
                if variants:
                    correct_variants = []
                    variant_index = 0
                    for variant in variants:
                        variant_index += 1
                        if variant['correct']:
                            correct_variants.append(variant['title'])
                        user_answer_index = 0
                        for user_answer in user_answers:
                            user_answer_index += 1
                            user_answer['title'] = user_answer['title'].replace(BLANK_TRIGGER_START, '')
                            user_answer['title'] = user_answer['title'].replace(BLANK_TRIGGER_END, '')
                            if user_answer['title'].strip() == variant['title'].strip():
                                if question.type == Question.CODE:
                                    user_answer['correct'] = variant['correct'] == user_answer['checked'] \
                                                             and variant_index == user_answer_index
                                else:
                                    user_answer['correct'] = variant['correct'] == user_answer['checked']

                    for user_answer in user_answers:
                        user_answer_is_correct = user_answer_is_correct and user_answer['correct']
                    if user_answer_is_correct:
                        score = question.score
                    result_check['result'] = user_answer_is_correct
                    result_check['correct_variants'] = correct_variants

                    quiz_results = request.user.quiz_results.filter(quiz=question.quiz, status=QuizResult.PROGRESS)
                    if not quiz_results.exists():
                        raise Http404('Такой страницы не существует')
                    else:
                        records = request.user.user_question_results.filter(question=question)
                        if records.exists():
                            record = records.first()
                        else:
                            record = QuestionResult(user=request.user, question=question)
                        record.answer = json.dumps(user_answers)
                        answer_code = get_format_code(code=question.code, need_safe=True, blank_list=user_answers)
                        record.answer_code = answer_code
                        record.score = score
                        record.correct = result_check['result']
                        record.save()

                        if question.quiz.time_type == Quiz.TIME_TYPE_QUIZ and time_left <= 0:
                            exists_results = list(
                                request.user.user_question_results.filter(question__quiz=question.quiz).values_list(
                                    'question', flat=True))
                            exists_results.append(question.id)
                            quiz_questions = question.quiz.questions.filter(active=True).exclude(id__in=exists_results)
                            for quiz_question in quiz_questions:
                                record = QuestionResult(user=request.user, question=quiz_question)
                                question_variants = json.loads(quiz_question.variants)
                                for question_variant in question_variants:
                                    question_variant['checked'] = False
                                    question_variant['correct'] = False
                                    if quiz_question.type == Question.CODE:
                                        question_variant['title'] = ''
                                record.answer = json.dumps(question_variants)
                                record.save()

            next_question_id = request.POST.get('next_question_id', '')
            if next_question_id:
                next_question = get_object_or_404(Question, id=next_question_id)
            else:
                next_question = question.get_next_question(True, True, request.user)

            if next_question:
                result_check['next_question_id'] = next_question.id

            params = {
                'user': request.user,
                'quiz': question.quiz,
                'request': request,
                'status': QuizResult.PROGRESS if next_question else QuizResult.COMPLETED,
                'question': next_question,
                'time_spent': json.loads(request.POST.get('time_spent', '')),
                'time_left': time_left if next_question else 0,
                'del_user_question_results': False,
            }
            update_exam_progress(**params)
    elif mode_exit == '1':
        records = request.user.user_question_results.filter(question__quiz=question.quiz)
        for record in records:
            record.delete()
        records = request.user.quiz_results.filter(quiz=question.quiz)
        for record in records:
            record.delete()

    if question:
        template_name = 'appcourses/quiz/_quiz_question.html'
        show_correct = True if request.POST.get('show_correct', '') == '1' else False
        # common
        context = {'lesson_url': request.POST.get('lesson_url', '')}
        context['quiz'] = question.quiz
        context['quiz_completed'] = False if next_question else True
        context['show_correct'] = show_correct
        context['reset_url'] = reset_url
        context['exit_url'] = exit_url

        # result
        context.update(get_context_from_question(
            **{'question': question, 'is_result': True, 'user_answers': user_answers,
               'user_answer_is_correct': user_answer_is_correct, 'answer_code': answer_code, 'user': request.user,
               'show_correct': request.POST.get('show_correct', ''), 'quiz_completed': context['quiz_completed'],
               'time_left': time_left}))

        result_check['html_current_question_result'] = render_to_string(template_name, context, request)

        # next question
        if next_question:
            context.update(
                get_context_from_question(**{'question': next_question, 'is_result': False, 'user': request.user,
                                             'quiz_completed': context['quiz_completed'], 'quiz': question.quiz}))

        result_check['html_next_question'] = render_to_string(template_name, context, request)

    return JsonResponse(result_check)


@login_required
@require_POST
def quiz_restart(request):
    question_id = request.POST.get('question_id', '')
    quiz_id = request.POST.get('quiz_id', '')
    if request.user and request.user.is_authenticated and (question_id or quiz_id):
        quiz = None
        if quiz_id:
            quiz = get_object_or_404(Quiz, quiz_id)
            request.user.quiz_results.filter(quiz__id=quiz_id).delete()
            request.user.user_question_results.filter(question__quiz__id=quiz_id).delete()
        elif question_id:
            question = get_object_or_404(Question, id=question_id)
            quiz = question.quiz
            request.user.quiz_results.filter(quiz__id=question.quiz.id).delete()
            request.user.user_question_results.filter(question__quiz__id=question.quiz.id).delete()
        if quiz:
            update_exam_progress(
                **{'user': request.user, 'quiz': quiz, 'request': request, 'status': QuizResult.PROGRESS,
                   'question': quiz.get_first_question(random=True)})

    return JsonResponse({'next': request.POST.get('next', '')})
