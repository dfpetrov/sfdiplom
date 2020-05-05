from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Skill(models.Model):

    title = models.CharField(max_length=250, verbose_name=_('Навык'))
    avatar = models.ImageField(null=True, blank=True, upload_to='apptasks/images/skills/', verbose_name=_('Аватар'))
    description = models.TextField(null=True, blank=True, verbose_name='Описание', default='')
    description_min = models.CharField(null=True, blank=True, max_length=250, verbose_name=_('Краткое описание'), default='')

    class Meta:
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('apptasks:skill_detail', args=[str(self.id)])

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        else:
            return ''


class Task(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    CODE_STORAGE_CHOICES = (
        ('1', 'Github'),
        ('2', 'Cloud'),
        ('3', 'Comment'),
    )
    BUILD_STORAGE_CHOICES = (
        ('1', 'None'),
        ('2', 'Github'),
        ('3', 'Heroku'),
        ('4', 'Github_Heroku'),
    )

    title = models.CharField(max_length=150, verbose_name='Название задачи')
    description = models.TextField(max_length=settings.TASK_DESCRIPTION_LEN_MAX, verbose_name='Описание задачи')
    description_short = models.CharField(max_length=settings.TASK_DESCRIPTION_LEN_SHORT, verbose_name='Краткое описание', default='')
    description_HTML = models.TextField(verbose_name='Форматированное описание', default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='inactive')
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='author')
    skill = models.ForeignKey(Skill, null=True, on_delete=models.SET_NULL, related_name='skill')
    extra_skill1 = models.ForeignKey(Skill, null=True, blank=True, on_delete=models.SET_NULL, related_name='extra_skill1')
    extra_skill2 = models.ForeignKey(Skill, null=True, blank=True, on_delete=models.SET_NULL, related_name='extra_skill2')
    extra_skill3 = models.ForeignKey(Skill, null=True, blank=True, on_delete=models.SET_NULL, related_name='extra_skill3')
    code_storage = models.CharField(max_length=50, null=True, blank=True, choices=CODE_STORAGE_CHOICES, default='1')
    build_storage = models.CharField(max_length=50, null=True, blank=True, choices=BUILD_STORAGE_CHOICES, default='1')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.description:
            self.description_short=self.description[0:settings.TASK_DESCRIPTION_LEN_SHORT]
        super(Task, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('apptasks:task_detail', args=[str(self.id)])

    def get_update_url(self):
        return reverse('apptasks:task_update', args=[str(self.id)])

    def need_code(self):
        if self.code_storage and int(self.code_storage) < 3:
            return True
        else:
            return False

    def need_build(self):
        if self.build_storage and int(self.build_storage) > 1:
            return True
        else:
            return False

    def get_rating(self):
        task_ratings = TaskRatings.objects.filter(task=self)
        task_rate = 0
        if task_ratings:
            count = task_ratings.count()
            value = 0
            for rate in task_ratings:
                value += rate.value
            task_rate = value / count
        return task_rate

    def get_extra_skill_count(self):
        count = 0
        if self.extra_skill1:
            count += 1
        if self.extra_skill2:
            count += 1
        if self.extra_skill3:
            count += 1
        return count

    def is_favorite(self, user):
        result = False
        if user and user.is_authenticated:
            result = TaskFavourites.objects.filter(task=self, user=user).exists()
        return result

    def is_like(self, user):
        result = False
        if user and user.is_authenticated:
            result = TaskLike.objects.filter(task=self, user=user).exists()
        return result

    def get_favourite_count(self):
        return TaskFavourites.objects.filter(task=self).count()

    def get_like_count(self):
        return TaskLike.objects.filter(task=self).count()


class CheckPoint(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=250, verbose_name='Checkpoint')
    order = models.IntegerField(null=True, blank=True, default=1, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Checkpoint'
        verbose_name_plural = 'Checkpoints'

    def __str__(self):
        return self.title


class TaskRatings(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='task_rating')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='user')
    value = models.IntegerField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Рейтинг задачи'
        verbose_name_plural = 'Рейтинги задач'

    def __str__(self):
        return f'{self.task}::{self.user}={self.value}'


class TaskFavourites(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='task_favourites', related_query_name='task_favourites')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Избранная задачи'
        verbose_name_plural = 'Избранные задач'

    def __str__(self):
        return f'{self.task}::{self.user}'


class TaskLike(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='task_like')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Лайк задачи'
        verbose_name_plural = 'Лайки задач'

    def __str__(self):
        return f'{self.task}::{self.user}'
