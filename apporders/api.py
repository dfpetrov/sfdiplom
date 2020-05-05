from django.conf import settings
from django.shortcuts import get_object_or_404, get_list_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from apptasks.models import Task, CheckPoint

from .models import Order, OrderInCheck, CheckPointOrderItem
from .forms import OrderCreationForm, OrderInCheckCreationForm


# @require_POST
# def order_in_check_create(request, order_for_check_id):
    
#     # создаем заказ на проверку
    
#     # получаем данные формы
#     form = OrderInCheckCreationForm(request.POST)
    
#     # проверяем валидность данных и создаем заказ на задачу
#     if form.is_valid():
        
#         # получаем решенный заказ пользователя по ID из параметров
#         user_order = get_object_or_404(Order, id=order_for_check_id)

#         # если у текущего пользователя уже есть на проверке данное решение, то ничего не делаем
#         # иначе создаем новый заказ на проверку
#         orders_in_check = OrderInCheck.objects.filter(user=request.user, order=user_order)
#         if orders_in_check:
#             new_order_in_check = orders_in_check[0]
#             new_order_in_check.status = 'incheck'
#         else:
#             new_order_in_check = OrderInCheck.objects.create(user=request.user, order=user_order, status='incheck')
#         new_order_in_check.save()
#         return HttpResponseRedirect(reverse_lazy('apporders:order_in_check_detail', kwargs={'pk': new_order_in_check.id}))

#     else:
#         pass
#         # print('Какая то ошибка')
#         # return redirect('appmain:dashboard')

@require_POST
def order_update_check(request, task_id=None):
    
    """
    Проверка корректности заполнения полей
    """

    response = {
        'title': '',
        'description': True,
    }

    text_len = len(request.POST.get('text', ''))
    if text_len > settings.ORDER_COMMENT_LEN_MAX:
        part1 = _('Текст комментария должен быть менее')
        part2 = _('символов. Сейчас')
        response['description'] = f'{part1} {settings.ORDER_COMMENT_LEN_MAX} {part2} {text_len}'
            
    return JsonResponse(response)