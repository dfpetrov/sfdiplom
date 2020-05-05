from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .models import Task, TaskFavourites, TaskLike, TaskRatings
from .forms import FavouriteFormPOST, AddLikeForm, SetRatingForm

@require_POST
def task_favourite_update(request, task_id):
    
    """
    Добавить или удалить задачу из избранного
    """

    # получаем данные формы
    form = FavouriteFormPOST(request.POST)
    
    result = False

    # проверяем валидность данных
    if form.is_valid():
        
        # получаем задачу по ID из параметров
        task = get_object_or_404(Task, id=task_id)

        # ищем запись в избранных
        task_records = TaskFavourites.objects.filter(task=task, user=request.user)
        if task_records:
            # если у пользователя в избранных есть эта задача - удаляем ее            
            task_record = task_records[0]
            task_record.delete()
            result = False
        else:
            # если у пользователя в избранных нет этой задачи - добавляем ее
            task_record = TaskFavourites.objects.create(task=task, user=request.user)
            task_record.save()
            result = True
        
    return JsonResponse({'is_favourite': result})

@require_POST
def task_like_update(request):
    
    """
    Добавить или удалить задачу из лайков
    """

    # получаем данные формы
    form = AddLikeForm(request.POST)
    
    result = False

    # проверяем валидность данных
    if form.is_valid():
        
        # получаем задачу по ID из параметров
        # task = get_object_or_404(Task, id=task_id)

        cd = form.cleaned_data
        task = cd['task']

        # ищем запись в избранных
        task_records = TaskLike.objects.filter(task=task, user=request.user)
        if task_records:
            # если у пользователя в избранных есть эта задача - удаляем ее            
            task_record = task_records[0]
            task_record.delete()
            result = False
        else:
            # если у пользователя в избранных нет этой задачи - добавляем ее
            task_record = TaskLike.objects.create(task=task, user=request.user)
            task_record.save()
            result = True
        
    return JsonResponse({'is_like': result})

@require_POST
def task_set_rating(request):
    
    """
    Добавить или удалить задачу из избранного
    """

    # получаем данные формы
    form = SetRatingForm(request.POST)

    task_rating = 0
    
    # проверяем валидность данных
    if form.is_valid():

        value = int(request.POST.get('value', 0))
        if value > 0:

            cd = form.cleaned_data
            task = cd['task']
            
            # ищем запись в рейтингах
            task_records = TaskRatings.objects.filter(task=task, user=request.user)
            if task_records:
                # если пользователь уже ставил рейтинг этой задаче
                task_record = task_records[0]
                task_record.value = value
                task_record.save()
            else:
                # если пользователь еще не ставил рейтинг этой задаче
                task_record = TaskRatings.objects.create(task=task, user=request.user, value=value)
                task_record.save()

            task_rating = task.get_rating()
        
    return JsonResponse({'rating': round(task_rating, 1)})

@require_POST
def task_update_check(request, task_id=None):
    
    """
    Проверка корректности заполнения полей задачи
    """

    response = {
        'title': '',
        'description': True,
    }

    text_len = len(request.POST.get('text', ''))
    if text_len < settings.TASK_DESCRIPTION_LEN_MIN:
        part1 = _('Текст задачи должен быть более')
        part2 = _('символов. Сейчас')
        response['description'] = f'{part1} {settings.TASK_DESCRIPTION_LEN_MIN} {part2} {text_len}'
    elif text_len > settings.TASK_DESCRIPTION_LEN_MAX:
        part1 = _('Текст задачи должно быть менее')
        part2 = _('символов. Сейчас')
        response['description'] = f'{part1} {settings.TASK_DESCRIPTION_LEN_MAX} {part2} {text_len}'
            
    return JsonResponse(response)