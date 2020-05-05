from django.contrib.auth.decorators import wraps
from appcourses.functions import update_queryset_from_user_results, update_queryset_from_course_content, \
    update_queryset_from_module_content\
    # , update_queryset_from_course_results


def add_quiz_results(add_question_results=False, add_result_description=False, add_user_answer=False):
    def update_queryset(function):
        @wraps(function)
        def wrapper(view):
            return update_queryset_from_user_results(function(view), view.request.user, add_question_results,
                                                     add_result_description,
                                                     add_user_answer)

        return wrapper

    return update_queryset


def add_module_content(only_active=True):
    def update_queryset(function):
        @wraps(function)
        def wrapper(view):
            return update_queryset_from_module_content(function(view), only_active)
        return wrapper
    return update_queryset


def filter_user_quizzes(func):
    def wrapper(view_def):
        user_results = view_def.request.user.quiz_results.select_related('quiz').all()
        quiz_filter = [item.quiz.id for item in user_results]
        queryset = func(view_def)
        return queryset.filter(id__in=quiz_filter)
    return wrapper


def add_course_content(only_active=True, add_modules=True, add_lessons=True, add_user_progress=False,
                       add_estimate=False, add_detail_estimate=False, estimate_only_active=True,
                       all_users_estimate=False):
    def update_queryset(function):
        @wraps(function)
        def wrapper(view):
            return update_queryset_from_course_content(function(view), view.request.user, only_active,
                                                       add_modules, add_lessons, add_user_progress,
                                                       add_estimate, add_detail_estimate, estimate_only_active,
                                                       all_users_estimate)

        return wrapper

    return update_queryset


def add_filter_pk_or_slug(func):
    def wrapper(view_def):
        queryset = func(view_def)

        # Next, try looking up by primary key.
        pk = view_def.kwargs.get(view_def.pk_url_kwarg)
        slug = view_def.kwargs.get(view_def.slug_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        if slug is not None and (pk is None or view_def.query_pk_and_slug):
            slug_field = view_def.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        return queryset

    return wrapper


def add_filter_active_course_content(func):
    def wrapper(view_def):
        queryset = func(view_def)
        return queryset.filter(modules__active=True, modules__lessons__active=True)
    return wrapper
