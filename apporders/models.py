from django.conf import settings
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from appaccounts import functions as AccountsFunctions
from apptasks.models import Task, CheckPoint


class Order(models.Model):
    
    STATUS_CHOICES = (
        ('inprogress', 'in progress'),
        ('done', 'done'),
        ('for_check', 'on check'),
        ('disabled', 'disabled'),
    )
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, null=False, on_delete=models.CASCADE, related_name='order_task')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='inprogress')
    comment = models.TextField(max_length=5000, null=True, blank=True, verbose_name='Комментарий', default='')
    comment_HTML = models.TextField(verbose_name='Форматированный комментарий', default='')
    code_url = models.URLField(null=True, blank=True, verbose_name='Ссылка на исходниик', default='')
    build_url = models.URLField(null=True, blank=True, verbose_name='Ссылка на решение', default='')
    

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Задача в работе'
        verbose_name_plural = 'Задачи в работе'

    def __str__(self):
        return f'{self.task}'

    def get_absolute_url(self):
        return reverse('apporders:order_update', args=[str(self.id)])

    def get_code_url(self):
        if self.code_url:
            return self.code_url
        else:
            return ''

    def get_build_url(self):
        if self.build_url:
            return self.build_url
        else:
            return ''

    def is_favorite(self, user):
        result = False
        if user and user.is_authenticated:
            result = OrderFavourites.objects.filter(order=self, user=user).exists()
        return result

    def is_like(self, user):
        result = False
        if user and user.is_authenticated:
            result = OrderLike.objects.filter(order=self, user=user).exists()
        return result

    def get_view_url(self):
        return reverse('apporders:order_view', args=[str(self.id)])

    def get_rate(self):
        
        # найдем все проверки данного заказа
        # ищем записи в таблице OrderInCheck по текущему ордеру со статусом 'done'
        task = self.task
        total_score = 0
        check_count = 0
        # check_count_all = 0
        check_result_list = OrderInCheck.objects.filter(order=self)
        for order_in_check in check_result_list:
            # check_count_all += 1
            if order_in_check.status == 'done':
                check_count += 1
            
                # найдем все проверенные чекпоинты и получим по ним оценки
                check_rate = 0
                checkpoints_count = 0
                checkpoint_list = CheckPoint.objects.filter(task=task)
                for checkpoint in checkpoint_list:
                    try:
                        chp = CheckPointOrderItem.objects.get(check_point=checkpoint, order_in_check=order_in_check)
                        check_rate += chp.rate
                        checkpoints_count += 1
                    except:
                        pass

                check_rate = round(0 if checkpoints_count == 0 else check_rate / checkpoints_count, 1)
                    
                total_score += check_rate

        # if check_count_all == 0:
        if check_count == 0:
            total_rate = 0
        else:
            total_rate = round(0 if check_count == 0 else total_score / check_count, 1)

        total_extra_rate = 0
        total_extra_rate_dispay = '--'
        extra_skill_count = task.get_extra_skill_count()
        if extra_skill_count:
            total_extra_rate = round(total_rate * 30 / 100 * extra_skill_count, 1)
            total_extra_rate_dispay = str(total_extra_rate)

        # total_rate += total_extra_rate
        if total_rate:
            rate_display = str(round(total_rate, 1))
        else:
            rate_display = '--'

        return {
            'rate': round(total_rate, 1),
            'rate_display': rate_display,
            'extra_rate': total_extra_rate, 
            'extra_rate_dispay': total_extra_rate_dispay, 
            'check_count': check_count,
            }

class OrderInCheck(models.Model):
    
    '''
    Взятые на проверку заказы
    '''

    STATUS_CHOICES = (
        ('incheck', 'in check'),
        ('done', 'done'),
        # ('canceled', 'Проверка отменена'),
    )
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, null=False, on_delete=models.CASCADE, related_name='order_order_in_check')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='incheck')
    comment = models.TextField(max_length=1500, null=True, blank=True, verbose_name='Комментарий', default='')

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Проверяемый заказ'
        verbose_name_plural = 'Проверяемые заказы'

    def __str__(self):
        return f'{self.order}'

    # def get_absolute_url(self):
    #     # return reverse('apporders:order-in-chek-detail', args=[str(self.id)])
    #     return reverse('apptasks:task_list')

class CheckPointOrderItem(models.Model):
    
    created = models.DateTimeField(auto_now_add=True)
    order_in_check = models.ForeignKey(OrderInCheck, null=True, on_delete=models.CASCADE, related_name='order_in_check_checkpoint')
    check_point = models.ForeignKey(CheckPoint, null=True, on_delete=models.CASCADE, related_name='task_checkpoint')
    rate = models.IntegerField(null=True, default=0)
    comment = models.TextField(max_length=1000, null=True, verbose_name='Комментарий', default='')

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Проверенный чекпоит'
        verbose_name_plural = 'Проверенные чекпоиты'

    def __str__(self):
        return f'{self.check_point} :: {self.order_in_check} [{self.rate}]'

    def get_absolute_url(self):
        pass
        # return reverse('apporders:order-in-chek-detail', args=[str(self.id)])

class OrderFavourites(models.Model):
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, related_name='order_favourites')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Избранное решение'
        verbose_name_plural = 'Избранные решения'

    def __str__(self):
        return f'{self.order}::{self.user}'

class OrderLike(models.Model):
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, related_name='order_like')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Лайк решения'
        verbose_name_plural = 'Лайки решений'

    def __str__(self):
        return f'{self.order}::{self.user}'