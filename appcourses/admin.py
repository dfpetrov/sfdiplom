from django.contrib import admin
from .models import Subject, Course, Module, Content, CourseEnroll, CourseSkillItem, Lesson, CompletedLesson, \
    CurrentLesson, Language, Quiz, Question, QuestionResult, QuizResult, Review


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}


class ModuleFilter(admin.SimpleListFilter):

    title = 'Фильтр по Модулю'
    parameter_name = 'module_id'
    field_name = 'module_id'

    def lookups(self, request, model_admin):
        """Доступныe фильтры по Lesson."""
        queryset = model_admin.get_queryset(request)
        course_id = request.GET.get('course_id')
        if course_id:
            modules = Module.objects.filter(course__id=course_id).order_by('order').distinct()
        else:
            modules = Module.objects.filter(lessons__in=queryset).order_by('order').distinct()
        for module in modules:
            yield (module.id, module.title)

    def queryset(self, request, queryset):
        module_id = self.value()
        if module_id:
            return queryset.filter(**{self.field_name: module_id})
        return queryset


class CourseFilter(admin.SimpleListFilter):

    title = 'Фильтр по Курсу'
    parameter_name = 'course_id'
    field_name = 'module__course_id'

    def lookups(self, request, model_admin):
        """Доступныe фильтры по Lesson."""
        # queryset = model_admin.get_queryset(request)
        # courses = Course.objects.filter(modules__lessons__in=queryset).order_by('title').distinct()
        courses = Course.objects.all().order_by('title').distinct()
        for course in courses:
            yield (course.id, course.title)

    def queryset(self, request, queryset):
        course_id = self.value()
        if course_id:
            return queryset.filter(**{self.field_name: course_id})
        return queryset


class CompletedLessonCourseFilter(admin.SimpleListFilter):

    title = 'Фильтр по Курсу'
    parameter_name = 'course_id'
    field_name = 'lesson__module__course_id'

    def lookups(self, request, model_admin):
        """Доступныe фильтры по Lesson."""
        # queryset = model_admin.get_queryset(request)
        # courses = Course.objects.filter(id__in=[item.lesson.module.course.id for item in queryset]).order_by('title').distinct()
        courses = Course.objects.all().order_by('title')
        for course in courses:
            yield (course.id, course.title)

    def queryset(self, request, queryset):
        course_id = self.value()
        if course_id:
            return queryset.filter(**{self.field_name: course_id})
        return queryset


class CompletedLessonModuleFilter(admin.SimpleListFilter):

    title = 'Фильтр по Модулю'
    parameter_name = 'module_id'
    field_name = 'lesson__module__id'

    def lookups(self, request, model_admin):
        """Доступныe фильтры по Lesson."""
        course_id = request.GET.get('course_id')
        if course_id:
            modules = Module.objects.filter(course__in=course_id).order_by('title').distinct()
        else:
            modules = Module.objects.all().order_by('title').distinct()
        for module in modules:
            yield (module.id, module.title)

    def queryset(self, request, queryset):
        module_id = self.value()
        if module_id:
            return queryset.filter(**{self.field_name: module_id})
        return queryset


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['course', 'title', 'active', 'slug', 'order']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('course',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'type', 'active', 'slug', 'order']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = (CourseFilter, ModuleFilter,)


@admin.register(CompletedLesson)
class CompletedLessonAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'completed']
    list_filter = (CompletedLessonCourseFilter, CompletedLessonModuleFilter, 'user',)


@admin.register(CurrentLesson)
class CurrentLessonAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'lesson', 'created']
    list_filter = ('user', 'course', 'lesson', 'created')


class ContentLessonFilter(admin.SimpleListFilter):

    title = 'Фильтр по Уроку'
    parameter_name = 'lesson_id'
    field_name = 'lesson_id'

    def lookups(self, request, model_admin):
        """Доступныe фильтры по Content."""
        queryset = model_admin.get_queryset(request)
        queryset = queryset.select_related('lesson')
        qs = Lesson.objects
        qs = qs.filter(id__in=[item.lesson_id for item in queryset])
        lesson__module_id = request.GET.get('lesson__module_id')
        if lesson__module_id:
            qs = qs.filter(module_id=lesson__module_id)
        course_id = request.GET.get('course_id')
        if course_id:
            qs = qs.filter(module__course_id=course_id)
        qs = qs.order_by('order').distinct()
        for lesson in qs:
            yield (lesson.id, lesson.title)

    def queryset(self, request, queryset):
        lesson_id = self.value()
        if lesson_id:
            return queryset.filter(**{self.field_name: lesson_id})
        return queryset


class ContentModuleFilter(admin.SimpleListFilter):

    title = 'Фильтр по Модулю'
    parameter_name = 'lesson__module_id'
    field_name = 'lesson__module_id'

    def lookups(self, request, model_admin):
        filter = False
        qs = Module.objects
        lesson_id = request.GET.get('lesson_id')
        if lesson_id:
            module_id = Lesson.objects.get(id=lesson_id).module.id
            qs = qs.filter(id=module_id)
            filter = True
        course_id = request.GET.get('course_id')
        if course_id:
            qs = qs.filter(course_id=course_id)
            filter = True
        if not filter:
            qs = qs.all()
        qs = qs.order_by('order').distinct()
        for module in qs:
            yield (module.id, module.title)

    def queryset(self, request, queryset):
        module_id = self.value()
        if module_id:
            return queryset.filter(**{self.field_name: module_id})
        return queryset


class ContentCourseFilter(admin.SimpleListFilter):

    title = 'Фильтр по Курсу'
    parameter_name = 'course_id'
    field_name = 'lesson__module__course_id'

    def lookups(self, request, model_admin):

        queryset = model_admin.get_queryset(request)
        queryset = queryset.select_related('lesson__module__course')
        qs = Course.objects
        qs = qs.filter(id__in=[item.lesson.module.course.id for item in queryset])
        lesson__module_id = request.GET.get('lesson__module_id')
        if lesson__module_id:
            course_id = Module.objects.get(id=lesson__module_id).course.id
            qs = qs.filter(id=course_id)
        qs = qs.order_by('title').distinct()
        for course in qs:
            yield (course.id, course.title)

    def queryset(self, request, queryset):
        course_id = self.value()
        if course_id:
            return queryset.filter(**{self.field_name: course_id})
        return queryset


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'content_type', 'active', 'item', 'order', 'slug']
    list_filter = (ContentCourseFilter, ContentModuleFilter, ContentLessonFilter, 'content_type',)


@admin.register(CourseEnroll)
class CourseEnrollAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled']
    list_filter = ('course', 'user')


@admin.register(CourseSkillItem)
class CourseSkillItemAdmin(admin.ModelAdmin):
    list_display = ['course', 'title']


class ModuleInline(admin.StackedInline):
    model = Module


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'subject', 'active', 'created']
    list_filter = ['created', 'subject']
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['id', 'active', 'title', 'subject', 'type', 'created', 'slug']
    list_filter = ['created', 'type', 'subject', 'language', 'active']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'active', 'title', 'type', 'score', 'quiz', 'order', 'created']
    list_filter = ('created', 'type', 'quiz')
    search_fields = ['title']


class QuestionResultQuizFilter(admin.SimpleListFilter):
    title = 'Фильтр по Quiz'
    parameter_name = 'quiz_id'
    field_name = 'question__quiz_id'

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        queryset = queryset.select_related('question__quiz')
        quizzes = Quiz.objects.filter(id__in=[item.question.quiz.id for item in queryset]).order_by('title').distinct()
        for quiz in quizzes:
            yield (quiz.id, quiz.title)

    def queryset(self, request, queryset):
        quiz_id = self.value()
        if quiz_id:
            return queryset.filter(**{self.field_name: quiz_id})
        return queryset


@admin.register(QuestionResult)
class QuestionResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'score', 'correct', 'created']
    list_filter = ('created', 'user', QuestionResultQuizFilter, 'question')


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'status', 'question', 'score', 'updated']
    list_filter = ('user', 'quiz', 'status', 'updated')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'module', 'estimate', 'active', 'category', 'created']
    list_filter = ('user', 'course', 'module', 'category', 'created')
