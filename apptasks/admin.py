from django.contrib import admin
from .models import Task, Skill, CheckPoint, TaskRatings, TaskFavourites, TaskLike

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'skill', 'status', 'author', 'updated',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    pass

@admin.register(CheckPoint)
class CheckPointAdmin(admin.ModelAdmin):
     list_display = ('id', 'title', 'task')

@admin.register(TaskRatings)
class TaskRatingsAdmin(admin.ModelAdmin):
     list_display = ('task', 'user', 'value', 'updated')

@admin.register(TaskFavourites)
class TaskFavouritesAdmin(admin.ModelAdmin):
     list_display = ('task', 'user', 'created')


@admin.register(TaskLike)
class TaskLikeAdmin(admin.ModelAdmin):
     list_display = ('task', 'user', 'created')