from django.db import models
from django.contrib.auth.models import User

from appcourses.models import Course, Lesson, Module, Quiz


class AccessType(models.Model):
    EDIT_NON_ACTIVE = 'n'
    EDIT_ACTIVE = 'a'
    SET_PUBLIC = 'p'
    REMOVE_PUBLIC = 'r'
    TYPE_CHOICES = (
        (EDIT_NON_ACTIVE, 'Редактирование не опубликованных'),
        (EDIT_ACTIVE, 'Редактирование опубликованных'),
        (SET_PUBLIC, 'Публикация объектов'),
        (REMOVE_PUBLIC, 'Снятие с публикации'),
    )
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=EDIT_NON_ACTIVE, verbose_name='Тип доступа',
                            unique=True)

    class Meta:
        verbose_name = 'Типы доступа'
        verbose_name_plural = 'Тип доступа'

    def __str__(self):
        return f'{self.get_type_display()}'


class CoursePermission(models.Model):
    user = models.ForeignKey(User, related_name='course_permissions', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='permissions', on_delete=models.CASCADE)
    access_type = models.ManyToManyField(AccessType, verbose_name='Тип доступа')

    class Meta:
        verbose_name = 'Разрешение на курс'
        verbose_name_plural = 'Разрешения на курсы'

    def __str__(self):
        return f'{self.user} - {self.course}'


class ModulePermission(models.Model):
    user = models.ForeignKey(User, related_name='module_permissions', on_delete=models.CASCADE)
    module = models.ForeignKey(Module, related_name='permissions', on_delete=models.CASCADE)
    access_type = models.ManyToManyField(AccessType, verbose_name='Тип доступа')

    class Meta:
        verbose_name = 'Разрешение на модуль'
        verbose_name_plural = 'Разрешения на модули'

    def __str__(self):
        return f'{self.user} - {self.module}'


class LessonPermission(models.Model):
    user = models.ForeignKey(User, related_name='lesson_permissions', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='permissions', on_delete=models.CASCADE)
    access_type = models.ManyToManyField(AccessType, verbose_name='Тип доступа')

    class Meta:
        verbose_name = 'Разрешение на урок'
        verbose_name_plural = 'Разрешения на уроки'

    def __str__(self):
        return f'{self.user} - {self.lesson}'


class QuizPermission(models.Model):
    user = models.ForeignKey(User, related_name='quiz_permissions', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, related_name='permissions', on_delete=models.CASCADE)
    access_type = models.ManyToManyField(AccessType, verbose_name='Тип доступа')

    class Meta:
        verbose_name = 'Разрешение на тест'
        verbose_name_plural = 'Разрешения на тесты'

    def __str__(self):
        return f'{self.user} - {self.quiz}'
