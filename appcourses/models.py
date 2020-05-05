import math
import json
from random import randrange
from django.conf import settings
from django.db import models
from django.db.models import Sum, Q
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from appmain.functions import generate_unique_slug
from PumpSkill.functions import plural_form

from .fields import OrderField

BLANK_TRIGGER_START = '{--'
BLANK_TRIGGER_END = '--}'


class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=210, unique=True)
    description = models.CharField(null=True, blank=True, max_length=250, verbose_name='Краткое описание', default='')
    avatar = models.ImageField(null=True, blank=True, upload_to='appcourses/images/subjects/', verbose_name='Аватар')

    class Meta:
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        else:
            return ''

    def save(self, *args, **kwargs):
        self.slug = generate_unique_slug(Subject, self.slug, self.title)
        super(Subject, self).save(*args, **kwargs)


class Language(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=210, unique=True)
    description = models.CharField(null=True, blank=True, max_length=250, verbose_name='Краткое описание', default='')
    avatar = models.ImageField(null=True, blank=True, upload_to='appcourses/images/language/', verbose_name='Аватар')

    class Meta:
        verbose_name = 'Язык программирования'
        verbose_name_plural = 'Языки программирования'
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        else:
            return ''

    def save(self, *args, **kwargs):
        self.slug = generate_unique_slug(Language, self.slug, self.title)
        super(Language, self).save(*args, **kwargs)


class Course(models.Model):
    BEGINNER = 'b'
    MIDDLE = 'm'
    ADVANCED = 'a'
    PRO = 'p'
    LEVEL_CHOICES = (
        (BEGINNER, 'Beginner'),
        (MIDDLE, 'Middle'),
        (ADVANCED, 'Advanced'),
        (PRO, 'Pro'),
    )
    owner = models.ForeignKey(User, null=True, blank=True, related_name='courses', on_delete=models.SET_NULL)
    subject = models.ForeignKey(Subject, null=True, related_name='courses', on_delete=models.SET_NULL)
    language = models.ManyToManyField(Language, related_name='courses')
    title = models.CharField(max_length=200, verbose_name='Название курса')
    slug = models.SlugField(max_length=210, null=True, blank=True, unique=True)
    overview = models.CharField(max_length=200, verbose_name='Краткое описание')
    description = models.TextField(max_length=2000, verbose_name='Полное описание', default='')
    profit = models.TextField(max_length=2000, verbose_name='Портрет выпускника', default='')
    created = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(null=True, blank=True, upload_to='appcourses/images/courses/', verbose_name='Аватар')
    level = models.CharField(max_length=1, null=True, blank=True, choices=LEVEL_CHOICES, default=BEGINNER)
    active = models.BooleanField(null=True, blank=True, verbose_name='Активен', default=False)
    new = models.BooleanField(null=True, blank=True, verbose_name='Новый', default=False)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-created']

    def __str__(self):
        return self.title

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        else:
            return ''

    def get_absolute_url(self):
        return reverse('appcourses:course_overview', args=[str(self.slug)])

    def get_manage_url(self):
        return reverse('appcourses:manage_course_update', args=[str(self.slug)])

    def get_change_public_url(self):
        return reverse('appcourses:manage_course_change_public', args=[str(self.pk)])

    def get_review_url(self):
        return reverse('appcourses:course_review', args=[str(self.slug)])

    def save(self, *args, **kwargs):
        self.slug = generate_unique_slug(Course, self.slug, self.title)
        super(Course, self).save(*args, **kwargs)

    def get_first_lesson(self):
        first_module = self.modules.filter(active=True).order_by('order').first()
        if first_module:
            return first_module.lessons.filter(active=True).order_by('order').first()
        return None

    @staticmethod
    def background_img():
        return f'{settings.STATIC_URL}images/background/course.jpg'


class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, verbose_name='Название модуля')
    description = models.TextField(blank=True, max_length=1000, verbose_name='Описание модуля')
    order = OrderField(blank=True, for_fields=['course'])
    slug = models.SlugField(max_length=210, unique=True, default='')
    active = models.BooleanField(null=True, blank=True, verbose_name='Активен', default=False)
    need_review = models.BooleanField(null=True, blank=True, verbose_name='Нужен отзыв', default=False)

    class Meta:
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модули'
        ordering = ['order']

    def __str__(self):
        return '{}. {}'.format(self.order, self.title)

    def save(self, *args, **kwargs):
        self.slug = generate_unique_slug(Module, self.slug, self.title)
        super(Module, self).save(*args, **kwargs)

    def get_absolute_url(self):
        pass

    def get_review_url(self):
        return reverse('appcourses:module_review', args=[str(self.course.slug), str(self.slug)])
        # if self.need_review:
        #     return reverse('appcourses:module_review', args=[str(self.course.slug), str(self.slug)])
        # return ''

    def get_manage_url(self):
        return reverse('appcourses:manage_module_update', args=[str(self.slug)])

    def get_change_public_url(self):
        return reverse('appcourses:manage_module_change_public', args=[str(self.pk)])

    def get_last_lesson(self):
        return self.lessons.filter(active=True).last()

    def get_first_lesson_next_module(self):
        next_module = self.course.modules.filter(Q(active=True) & Q(order__gt=self.order)).first()
        if next_module:
            return next_module.lessons.filter(active=True).first()
        return None


class Quiz(models.Model):
    PERCENT_GOLD = 95
    PERCENT_SILVER = 85
    PERCENT_BRONZE = 75

    COMMON = 'c'
    EXAM = 'e'
    LESSON = 'l'
    TYPE_CHOICES = (
        (COMMON, 'Common'),
        (EXAM, 'Exam'),
        (LESSON, 'Lesson'),
    )

    TIME_TYPE_NONE = 'a'
    TIME_TYPE_QUIZ = 'b'
    TIME_TYPE_QUESTION = 'c'
    TIME_TYPE_CHOICES = (
        (TIME_TYPE_NONE, 'NoneTime'),
        (TIME_TYPE_QUIZ, 'QuizTime'),
        (TIME_TYPE_QUESTION, 'QuestionTime'),
    )

    owner = models.ForeignKey(User, null=True, blank=True, related_name='quizzes', on_delete=models.SET_NULL)
    subject = models.ForeignKey(Subject, null=True, blank=True, related_name='quizzes', on_delete=models.SET_NULL)
    avatar = models.ImageField(null=True, blank=True, upload_to='appcourses/images/quiz/avatars', verbose_name='Аватар')
    index_avatar = models.SmallIntegerField(null=True, blank=True, verbose_name='Номер изображения')
    language = models.ManyToManyField(Language, related_name='quizzes')
    title = models.CharField(max_length=200, null=True, verbose_name='Название теста')
    overview = models.CharField(max_length=200, verbose_name='Краткое описание теста', default='')
    description = models.TextField(max_length=2000, verbose_name='Полное описание теста', default='')
    slug = models.SlugField(max_length=210, null=True, blank=True, unique=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=1, null=True, choices=TYPE_CHOICES, default=COMMON, verbose_name='Тип теста')
    time_type = models.CharField(max_length=1, null=True, choices=TIME_TYPE_CHOICES, default=TIME_TYPE_QUESTION,
                                 verbose_name='Тип времени')
    active = models.BooleanField(null=True, blank=True, verbose_name='Активен', default=False)
    level = models.CharField(max_length=1, null=True, choices=Course.LEVEL_CHOICES, default=Course.BEGINNER,
                             verbose_name='Уровень')
    duration = models.SmallIntegerField(null=True, default=0, verbose_name='Время на тест в секундах')

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'
        ordering = ['-created']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = generate_unique_slug(Quiz, self.slug, self.title)
        if not self.index_avatar:
            self.index_avatar = randrange(6) + 1
        super(Quiz, self).save(*args, **kwargs)

    def get_avatar_url(self):
        if self.index_avatar:
            return settings.STATIC_URL + f'images/courses/quizzes/avatar/{self.index_avatar}.jpg'
        if self.avatar:
            return self.avatar.url
        else:
            return ''

    def get_background_url(self):
        if self.index_avatar:
            return settings.STATIC_URL + f'images/courses/quizzes/background/{self.index_avatar}.jpg'
        if self.avatar:
            return self.avatar.url
        else:
            return ''

    def get_manage_url(self):
        return reverse('appcourses:manage_quiz_update', args=[str(self.slug)])

    def get_change_public_url(self):
        return reverse('appcourses:manage_quiz_change_public', args=[str(self.pk)])

    def get_absolute_url(self):
        if self.type == self.COMMON:
            return reverse('appcourses:exam_overview', args=[str(self.slug)])
        elif self.type == self.EXAM:
            return reverse('appcourses:exam_overview', args=[str(self.slug)])
        else:
            return reverse('appcourses:exam_overview', args=[str(self.slug)])

    def get_progress_url(self):
        return reverse('appcourses:exam_progress', args=[str(self.slug)])

    def get_results_url(self):
        return reverse('appmain:quiz_results', args=[str(self.slug)])

    def get_first_question(self, random=False):
        qs = self.questions.filter(active=True)
        if qs:
            if not random:
                return qs.first()
            else:
                return qs.all()[randrange(qs.count())]
        else:
            return None

    def is_running(self, user):
        if user and user.is_authenticated:
            return self.user_results.filter(user=user).exists()
        return False

    def get_cup_avatar(self, score, total_score=None):
        if not score:
            score = 0

        if not total_score:
            qs = Quiz.objects.filter(id=self.id, questions__active=True).annotate(total_score=Sum('questions__score'))
            if qs.exists():
                total_score = qs.first().total_score

        percent = round(score / total_score * 100)

        if percent >= self.PERCENT_GOLD:
            return self.avatar_gold_cup()
        elif percent >= self.PERCENT_SILVER:
            return self.avatar_silver_cup()
        elif percent >= self.PERCENT_BRONZE:
            return self.avatar_bronze_cup()

        return self.avatar_black_cup()

    def get_result_description(self, score, total_score=None, complete_date=None):
        if not score:
            score = 0
        if not total_score:
            qs = Quiz.objects.filter(id=self.id, questions__active=True).annotate(total_score=Sum('questions__score'))
            if qs.exists():
                total_score = qs.first().total_score
        percent = round(score / total_score * 100)

        class Result:
            def __init__(self, completed, cup_description, cup_avatar, goal_description, goal_avatar):
                self.completed = completed
                self.cup_description = cup_description
                self.cup_avatar = cup_avatar
                self.goal_description = goal_description
                self.goal_avatar = goal_avatar

        def result_dict(cup_description, cup_avatar, goal_description, goal_avatar):
            return {'cup_description': cup_description, 'cup_avatar': cup_avatar,
                    'goal_description': goal_description, 'goal_avatar': goal_avatar}

        if not complete_date:
            return result_dict(str(_('Не пройодено')), Quiz.avatar_black_cup(), str(_('Не пройодено')), '')
        elif percent >= self.PERCENT_GOLD:
            return result_dict(str(_('Золотой кубок')), Quiz.avatar_gold_cup(), '', '')
        elif percent >= self.PERCENT_SILVER:
            need_score_plural = plural_form(math.ceil(total_score * self.PERCENT_GOLD / 100) - score, 'балл', 'балла',
                                            'баллов')
            return result_dict(str(_('Серебряный кубок')), Quiz.avatar_silver_cup(),
                               f'До золотого кубка не хватает {need_score_plural}', Quiz.avatar_gold_cup())
        elif percent >= self.PERCENT_BRONZE:
            need_score_plural = plural_form(math.ceil(total_score * self.PERCENT_SILVER / 100 - score), 'балл', 'балла',
                                            'баллов')
            return result_dict(str(_('Бронзовый кубок')), Quiz.avatar_bronze_cup(),
                               f'До серебрянного кубка не хватает {need_score_plural}', Quiz.avatar_silver_cup())
        else:
            need_score_plural = plural_form(math.ceil(total_score * self.PERCENT_BRONZE / 100 - score), 'балл', 'балла',
                                            'баллов')
            return result_dict('', Quiz.avatar_black_cup(), f'До бронзового кубка не хватает {need_score_plural}',
                               Quiz.avatar_bronze_cup())

    @staticmethod
    def avatar_gold_cup():
        return settings.STATIC_URL + 'images/courses/ico/gold-cup.svg'

    @staticmethod
    def avatar_silver_cup():
        return settings.STATIC_URL + 'images/courses/ico/silver-cup.svg'

    @staticmethod
    def avatar_bronze_cup():
        return settings.STATIC_URL + 'images/courses/ico/bronze-cup.svg'

    @staticmethod
    def avatar_black_cup():
        return settings.STATIC_URL + 'images/courses/ico/black_cup.svg'


class Lesson(models.Model):
    LESSON = 'l'
    QUIZ = 'q'
    TYPE_CHOICES = (
        (LESSON, 'Lesson'),
        (QUIZ, 'Quiz'),
    )
    module = models.ForeignKey(Module, related_name='lessons', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, null=True, blank=True, related_name='quizzes', on_delete=models.SET_NULL)
    title = models.CharField(max_length=200, verbose_name='Название урока')
    description = models.TextField(max_length=1000, null=True, blank=True, verbose_name='Описание урока')
    order = OrderField(blank=True, for_fields=['module'])
    slug = models.SlugField(max_length=210, unique=True, default='')
    active = models.BooleanField(null=True, blank=True, verbose_name='Активна', default=False)
    type = models.CharField(max_length=1, null=True, choices=TYPE_CHOICES, default=LESSON, verbose_name='Тип')

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['order']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = generate_unique_slug(Lesson, self.slug, self.title)
        super(Lesson, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('appcourses:lesson_detail',
                       args=[str(self.module.course.slug),
                             str(self.module.slug),
                             str(self.slug)]
                       )

    def get_manage_url(self):
        return reverse('appcourses:manage_lesson_update', args=[str(self.slug)])

    def get_change_public_url(self):
        return reverse('appcourses:manage_lesson_change_public', args=[str(self.pk)])

    def get_contents(self):
        contents = []
        lesson_active_contents = self.contents.filter(active=True).all()
        for content in lesson_active_contents:
            contents.append(content.get_content())
        return contents

    def get_quiz(self):
        if self.quiz:
            return self.quiz
        if self.type == self.QUIZ:
            content = self.contents.filter(active=True).first()
            if content and content.quiz:
                return content.quiz
        return None

    def get_first_question(self, random=True):
        if self.type == self.QUIZ:
            content = self.contents.filter(active=True).first()
            if content and content.quiz:
                return content.quiz.get_first_question(random)
        return None

    @property
    def next_lesson(self):
        current_module = self.module
        module_list = list(self.module.course.modules.filter(active=True))
        next_lesson = None
        next_module = None
        if current_module in module_list:
            index_module = module_list.index(current_module)
            if len(module_list) > index_module + 1:
                next_module = module_list[index_module + 1]
        lesson_list = list(current_module.lessons.filter(active=True))
        if self in lesson_list:
            index_lesson = lesson_list.index(self)
            if len(lesson_list) > index_lesson + 1:
                next_lesson = lesson_list[index_lesson + 1]
                next_module = ''
        if not next_lesson and next_module:
            next_module_lessons = next_module.lessons.filter(active=True)
            if next_module_lessons.exists():
                next_lesson = next_module_lessons.first()
        return next_lesson


class CourseSkillItem(models.Model):
    course = models.ForeignKey(Course, null=True, related_name='skills', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, verbose_name='Название')

    class Meta:
        verbose_name = 'Компетенция'
        verbose_name_plural = 'Компетенции курса'

    def __str__(self):
        return self.title


class CourseEnroll(models.Model):
    user = models.ForeignKey(User, related_name='courses_enroll', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='courses_enroll', on_delete=models.CASCADE)
    enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Запись на курс'
        verbose_name_plural = 'Записи на курс'
        ordering = ['-enrolled']


class CompletedLesson(models.Model):
    lesson = models.ForeignKey(Lesson, related_name='completed_lessons', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='completed_lessons', on_delete=models.CASCADE)
    completed = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Завершенный урок'
        verbose_name_plural = 'Завершенные уроки'
        ordering = ['-completed']

    def __str__(self):
        return self.lesson.title


class CurrentLesson(models.Model):
    user = models.ForeignKey(User, related_name='current_lessons', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='current_lessons', null=True, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='current_lessons', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Текущий урок'
        verbose_name_plural = 'Текущие уроки'
        ordering = ['-created']

    def save(self, *args, **kwargs):
        if self.course != self.lesson.module.course:
            self.course = self.lesson.module.course
        super(CurrentLesson, self).save(*args, **kwargs)

    def __str__(self):
        return self.lesson.title


class Content(models.Model):
    lesson = models.ForeignKey(Lesson, null=True, related_name='contents', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, null=True, blank=True, related_name='contents', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,
                                     limit_choices_to={'model__in': ('text', 'video', 'image', 'file')},
                                     on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])
    slug = models.SlugField(max_length=210, unique=True, default='')
    active = models.BooleanField(null=True, blank=True, verbose_name='Активен', default=False)

    class Meta:
        verbose_name = 'Контент'
        verbose_name_plural = 'Контент'
        ordering = ['order']

    def __str__(self):
        return self.item.title

    def get_absolute_url(self):
        pass

    def get_manage_url(self):
        return reverse('appcourses:manage_content_update', args=[str(self.pk)])

    def get_change_public_url(self):
        return reverse('appcourses:manage_content_change_public', args=[str(self.pk)])

    def save(self, *args, **kwargs):
        self.slug = generate_unique_slug(Content, self.slug, self.item.title)
        super(Content, self).save(*args, **kwargs)

    def get_content_type_display(self):
        return self.item._meta.model_name

    def get_description_html(self):
        if self.item._meta.model_name == 'text':
            return self.item.description_HTML
        else:
            return ''

    def get_content(self):
        if self.item._meta.model_name == 'text':
            return {'type': 'text', 'content': self.item.description_HTML}
        elif self.item._meta.model_name == 'video':
            return {'type': 'video', 'content': self.item.url}
        elif self.item._meta.model_name == 'lessonquiz':
            return {'type': 'lessonquiz', 'content': self.item.quiz}


class ItemBase(models.Model):
    owner = models.ForeignKey(User, related_name='%(class)s_related', on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def render(self):
        return render_to_string('appcourses/content/{}.html'.format(
            self._meta.model_name), {'item': self})


class Text(ItemBase):
    content = models.TextField()
    description_HTML = models.TextField(verbose_name='Форматированное описание', default='')


class Image(ItemBase):
    file = models.FileField(upload_to='images')


class Video(ItemBase):
    url = models.URLField()


class File(ItemBase):
    file = models.FileField(upload_to='files')


class LessonQuiz(ItemBase):
    quiz = models.ForeignKey(Quiz, null=True, blank=True, related_name='lessons', on_delete=models.SET_NULL)


class ContentQuiz(ItemBase):
    quiz = models.ForeignKey(Quiz, null=True, blank=True, on_delete=models.CASCADE)


class Question(models.Model):
    SINGLE = 's'
    MULTIPLE = 'm'
    CODE = 'c'
    TYPE_CHOICES = (
        (SINGLE, 'Single'),
        (MULTIPLE, 'Multiple'),
        (CODE, 'Code'),
    )

    owner = models.ForeignKey(User, null=True, related_name='questions', on_delete=models.SET_NULL)
    quiz = models.ForeignKey(Quiz, null=True, blank=True, related_name='questions', on_delete=models.SET_NULL)
    title = models.CharField(max_length=200, null=True, blank=True, verbose_name='Название вопроса')
    text = models.TextField(max_length=2000, null=True, blank=True, verbose_name='Текст вопроса', default='')
    code = models.TextField(max_length=2000, null=True, blank=True, verbose_name='Код к вопросу (строка JSON)',
                            default='')
    expected_result = models.TextField(max_length=2000, null=True, blank=True,
                                       verbose_name='Ожидаемый результат (строка JSON)',
                                       default='')
    need_expected_result = models.BooleanField(null=True, blank=True, verbose_name='Требуется ожидаемый результат',
                                               default=False)
    description = models.TextField(max_length=1000, null=True, blank=True, verbose_name='Примечание', default='')
    type = models.CharField(max_length=1, null=True, choices=TYPE_CHOICES, default=SINGLE, verbose_name='Тип')
    duration = models.SmallIntegerField(null=True, default=0, verbose_name='Время на вопрос в секундах')
    created = models.DateTimeField(auto_now_add=True)
    variants = models.TextField(max_length=1000, null=True, blank=True, verbose_name='Варианты ответа (строка JSON)')
    active = models.BooleanField(null=True, blank=True, verbose_name='Активен', default=False)
    score = models.IntegerField(null=True, blank=True, verbose_name='Баллы', default=0)
    order = OrderField(blank=True, for_fields=['quiz'], default=0)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['order']

    def __str__(self):
        return self.title

    def get_manage_url(self):
        return reverse('appcourses:manage_question_update', args=[str(self.pk)])

    def get_change_public_url(self):
        return reverse('appcourses:manage_question_change_public', args=[str(self.pk)])

    def get_absolute_url(self):
        return reverse('appcourses:exam_progress', args=[str(self.quiz.slug)])

    def get_owner_questions(self):

        class Result:

            def __init__(self, questions, count=0):
                self.questions = questions
                self.count = count

        if self.quiz:
            questions = self.quiz.questions.all()
            i = 1
            for item in questions:
                item.number = i
                i += 1
            result = Result(list(questions), count=questions.count())
        else:
            result = Result([], 0)

        return result

    def get_next_question(self, random=False, filter_questions_results=False, user=None):
        if not filter_questions_results:
            question_qs = self.quiz.questions.filter(active=True)
        else:
            exclude_id_list = user.user_question_results.select_related('question').filter(
                question__quiz=self.quiz).values_list('question', flat=True)
            # exclude_id_list = [item.question.id for item in questions_results.all()]
            question_qs = self.quiz.questions.filter(active=True).exclude(id__in=exclude_id_list)
        if random:
            if question_qs:
                question_qs = question_qs.exclude(id=self.id)
                if question_qs:
                    return list(question_qs)[randrange(question_qs.count())]
        else:
            if self in question_qs:
                question_qs_list = list(question_qs)
                index = question_qs_list.index(self)
                if len(question_qs_list) > index + 1:
                    return question_qs_list[index + 1]
        return None

    @staticmethod
    def avatar_hourglass():
        return settings.STATIC_URL + 'images/courses/ico/hourglass.svg'

    @staticmethod
    def avatar_answer_correct():
        return settings.STATIC_URL + 'images/courses/ico/answer_correct.svg'

    @staticmethod
    def avatar_answer_incorrect():
        return settings.STATIC_URL + 'images/courses/ico/answer_incorrect.svg'

    @property
    def description_type(self):
        if self.type == self.SINGLE:
            return _('одиночный выбор')
        elif self.type == self.MULTIPLE:
            return _('множественный выбор')
        elif self.type == self.CODE:
            return _('Заполни пропуски')

    @property
    def variants_list(self):
        if self.variants:
            return json.loads(self.variants)
        else:
            return []

    @property
    def need_countdown(self):
        return self.quiz.time_type in [Quiz.TIME_TYPE_QUESTION, Quiz.TIME_TYPE_QUIZ]


class QuestionResult(models.Model):
    user = models.ForeignKey(User, null=True, related_name='user_question_results', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, null=True, related_name='user_question_results', on_delete=models.CASCADE)
    answer = models.TextField(max_length=2000, null=True, verbose_name='Ответ пользователя JSON', default='')
    answer_code = models.TextField(max_length=2000, null=True, verbose_name='Код ответа пользователя', default='')
    score = models.IntegerField(null=True, blank=True, verbose_name='Баллы', default=0)
    correct = models.BooleanField(null=True, blank=True, verbose_name='Ответ правильный', default=False)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.question}'

    class Meta:
        verbose_name = 'Ответ пользователя'
        verbose_name_plural = 'Ответы на вопросы тестов'


class QuizResult(models.Model):
    COMPLETED = 'c'
    PROGRESS = 'p'
    TYPE_CHOICES = (
        (COMPLETED, 'Completed'),
        (PROGRESS, 'In progress'),
    )

    user = models.ForeignKey(User, null=True, related_name='quiz_results', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, null=True, related_name='user_results', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, null=True, related_name='user_results', on_delete=models.CASCADE)
    status = models.CharField(max_length=1, null=True, choices=TYPE_CHOICES, default=COMPLETED, verbose_name='Статус')
    score = models.IntegerField(null=True, blank=True, verbose_name='Баллы', default=0)
    correct_count = models.SmallIntegerField(null=True, blank=True, default=0,
                                             verbose_name='Количество правильных ответов')
    updated = models.DateTimeField(auto_now=True)
    time_left = models.SmallIntegerField(null=True, blank=True, default=0, verbose_name='Осталось времени на тест')

    def __str__(self):
        return f'{self.user} - {self.quiz}'

    class Meta:
        verbose_name = 'Результат теста'
        verbose_name_plural = 'Результаты тестов'


class Review(models.Model):
    EXPLICIT = 'e'
    NEED_FIX = 'f'
    COMPLIMENT = 'c'
    CATEGORY_CHOICES = (
        (EXPLICIT, 'Explicit'),
        (NEED_FIX, 'Need fix'),
        (COMPLIMENT, 'Complement'),
    )

    user = models.ForeignKey(User, null=True, related_name='reviews', on_delete=models.SET_NULL)
    course = models.ForeignKey(Course, null=True, blank=True, related_name='reviews', on_delete=models.CASCADE)
    module = models.ForeignKey(Module, null=True, blank=True, related_name='reviews', on_delete=models.CASCADE)
    text = models.TextField(max_length=2000, verbose_name='Текст', default='')
    estimate = models.SmallIntegerField(default=0, verbose_name='Оценка')
    created = models.DateTimeField(auto_now=True)
    active = models.BooleanField(null=True, blank=True, verbose_name='Активен', default=False)
    category = models.CharField(max_length=1, null=True, choices=CATEGORY_CHOICES, verbose_name='Категория отзыва')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.user}/{self.created}/{self.course}/{self.module}'

    def save(self, *args, **kwargs):
        self.text = self.text[:2000]
        super(Review, self).save(*args, **kwargs)

    def get_estimate_avatar(self):
        if self.estimate == 3:
            return settings.STATIC_URL + 'images/ico/emotions/smiling.svg'
        elif self.estimate == 2:
            return settings.STATIC_URL + 'images/ico/emotions/smirking.svg'
        elif self.estimate == 1:
            return settings.STATIC_URL + 'images/ico/emotions/crying.svg'

    @staticmethod
    def avatar_estimate_1():
        return settings.STATIC_URL + 'images/ico/emotions/crying.svg'

    @staticmethod
    def avatar_estimate_2():
        return settings.STATIC_URL + 'images/ico/emotions/smirking.svg'

    @staticmethod
    def avatar_estimate_3():
        return settings.STATIC_URL + 'images/ico/emotions/smiling.svg'

    @staticmethod
    def avatar_star():
        return settings.STATIC_URL + 'images/ico/star.svg'

    @staticmethod
    def avatar_star_outline():
        return settings.STATIC_URL + 'images/ico/star_outline.svg'
