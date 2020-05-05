from django.contrib import admin

from appcourses.models import Course, Module, Lesson
from .models import CoursePermission, LessonPermission, ModulePermission, AccessType, QuizPermission


@admin.register(AccessType)
class CourseAccessType(admin.ModelAdmin):
    list_display = ['type']


@admin.register(CoursePermission)
class CoursePermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'course']
    list_filter = ('user', 'course')


class ModuleFilter(admin.SimpleListFilter):

    title = 'Фильтр по Модулю'
    parameter_name = 'module_id'
    field_name = 'lesson__module_id'

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        course_id = request.GET.get('course_id')
        if course_id:
            modules = Module.objects.filter(course__id=course_id).order_by('order').distinct()
        else:
            modules = Module.objects.filter(lessons__in=[item.lesson for item in queryset]).order_by('order').distinct()
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
    field_name = 'lesson__module__course_id'

    def lookups(self, request, model_admin):
        courses = Course.objects.all().order_by('title').distinct()
        for course in courses:
            yield (course.id, course.title)

    def queryset(self, request, queryset):
        course_id = self.value()
        if course_id:
            return queryset.filter(**{self.field_name: course_id})
        return queryset


class LessonFilter(admin.SimpleListFilter):

    title = 'Фильтр по Уроку'
    parameter_name = 'lesson_id'
    field_name = 'lesson_id'

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        lesson_qs = Lesson.objects
        filtered = False
        if queryset:
            lesson_qs = lesson_qs.filter(id=[item.lesson.id for item in queryset])
            filtered = True
        course_id = request.GET.get('course_id')
        if course_id:
            lesson_qs = lesson_qs.filter(module__course_id=course_id)
            filtered = True
        module_id = request.GET.get('module_id')
        if module_id:
            lesson_qs = lesson_qs.filter(module_id=module_id)
            filtered = True
        if not filtered:
            lesson_qs = lesson_qs.all()
        lesson_qs = lesson_qs.order_by('title').distinct()
        for lesson in lesson_qs:
            yield (lesson.id, lesson.title)

    def queryset(self, request, queryset):
        lesson_id = self.value()
        if lesson_id:
            return queryset.filter(**{self.field_name: lesson_id})
        return queryset


@admin.register(LessonPermission)
class LessonPermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson']
    list_filter = ('user', CourseFilter, ModuleFilter, LessonFilter)


class ModuleCourseFilter(admin.SimpleListFilter):

    title = 'Фильтр по Курсу'
    parameter_name = 'course_id'
    field_name = 'module__course_id'

    def lookups(self, request, model_admin):
        courses = Course.objects.all().order_by('title').distinct()
        for course in courses:
            yield (course.id, course.title)

    def queryset(self, request, queryset):
        course_id = self.value()
        if course_id:
            return queryset.filter(**{self.field_name: course_id})
        return queryset


class ModuleModuleFilter(admin.SimpleListFilter):

    title = 'Фильтр по Модулю'
    parameter_name = 'module_id'
    field_name = 'module_id'

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        qs = Module.objects
        filtered = False
        if queryset:
            qs = qs.filter(id=[item.module.id for item in queryset])
            filtered = True
        course_id = request.GET.get('course_id')
        if course_id:
            qs = qs.filter(course_id=course_id)
            filtered = True
        if not filtered:
            qs = qs.all()
        qs = qs.order_by('title').distinct()
        for module in qs:
            yield (module.id, module.title)

    def queryset(self, request, queryset):
        module_id = self.value()
        if module_id:
            return queryset.filter(**{self.field_name: module_id})
        return queryset


@admin.register(ModulePermission)
class ModulePermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'module']
    list_filter = ('user', ModuleCourseFilter, ModuleModuleFilter)


@admin.register(QuizPermission)
class QuizPermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz']
    list_filter = ('user', 'quiz')
