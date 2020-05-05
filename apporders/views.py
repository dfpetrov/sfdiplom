from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.utils.translation import gettext_lazy as _

from .models import Order, OrderInCheck, CheckPointOrderItem, OrderFavourites, OrderLike
from .forms import OrderCreationForm, OrderUpdateForm, OrderStatusUpdateForm, OrderInCheckCreationForm, OrderInCheckUpdateForm, FavouriteUpdateForm, LikeUpdateForm
from . import functions as OrderFunctions

from apptasks.models import Task, CheckPoint
from apptasks import functions as TaskFunctions
from appaccounts import functions as AccountFunctions

# from allauth.account.decorators import verified_email_required
from appaccounts.decorators import verified_email_required

TASK_HREF_TITLE_PREFIX = settings.TASK_HREF_TITLE_PREFIX
SKILL_HREF_TITLE_PREFIX = settings.SKILL_HREF_TITLE_PREFIX
PROFILE_HREF_TITLE_PREFIX = settings.PROFILE_HREF_TITLE_PREFIX

@verified_email_required
@require_POST
def order_create(request):
    
    # create new order

    # get data from form
    form = OrderCreationForm(request.POST)

    # validation form and create order
    if form.is_valid():
        
        new_order = form.save(commit=False)
        new_order.save()
        return HttpResponseRedirect(reverse_lazy('apporders:order_update', kwargs={'pk': new_order.id}))

    else:
        errors = ''
        for value in form.errors.values():
            for item in value:
                errors += f"{item}\n"
        raise Http404(errors)


@verified_email_required
@require_POST
def order_in_check_create(request, order_for_check_id):
    
    # create new order in check

    order_for_check = get_object_or_404(Order, pk = order_for_check_id)
    
    # get data from form
    form = OrderInCheckCreationForm(request.POST)
    
    # validation form and create order in check
    if form.is_valid():
        
        orders_in_check = OrderInCheck.objects.filter(user=request.user, order=order_for_check)
        if orders_in_check:
            # if request.user has OrderInCheck for order_for_check_id then update status for it
            new_order_in_check = orders_in_check[0]
            new_order_in_check.status = 'incheck'
        else:
            # else create new OrderInCheck
            new_order_in_check = OrderInCheck.objects.create(user=request.user, order=order_for_check)
        new_order_in_check.save()
        return HttpResponseRedirect(reverse_lazy('apporders:order_in_check_update', kwargs={'pk': new_order_in_check.id}))

    else:
        raise Http404("Такой страницы не существует")


@verified_email_required
@require_POST
def order_status_update(request, pk):
    """
    set new status for order
    """

    order_inst = get_object_or_404(Order, pk = pk)

    if order_inst.user != request.user:
        raise Http404("Такой страницы не существует")
    
    form = OrderStatusUpdateForm(request.POST)
    
    # проверяем валидность данных
    if form.is_valid():
        
        # устанавливаем новый статус заказу
        # status = form.cleaned_data['status']
        status = order_inst.status
        if status == 'inprogress':
            order_inst.status = 'for_check'
        elif status == 'done':
            order_inst.status = 'for_check'
        elif status == 'for_check':
            order_inst.status = 'done'
        elif status == 'disabled':
            order_inst.status = 'inprogress'

        order_inst.save()
        
        # переходим к заказу
        if bool(request.POST.get('return_json_url', False)):
            # print('return_url = True******************')
            # return reverse_lazy('apporders:order_update', kwargs={'pk': order_inst.id})
            return JsonResponse({'response': order_inst.get_absolute_url()})
        else:
            return HttpResponseRedirect(reverse_lazy('apporders:order_update', kwargs={'pk': order_inst.id}))

    else:
        raise Http404("Такой страницы не существует")


class OrderInChekUpdateView(generic.UpdateView):
    form_class = OrderInCheckUpdateForm
    model = OrderInCheck
    template_name = 'apporders/order_in_check_detail.html'

    # def get(self, request, *args, **kwargs):
    #     return super().get(request, *args, **kwargs)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        
        request_post = self.request.POST
        order_in_check = self.object
        order_in_check.status='done'
        
        # get all checkpoints of the task of the order
        task_checkpoints = CheckPoint.objects.filter(task=order_in_check.order.task)

        for task_checkpoint in task_checkpoints:
            
            task_checkpoint_id = str(task_checkpoint.id)
            
            # get CheckPointOrderItem
            checkpoint_order_items = CheckPointOrderItem.objects.filter(order_in_check=order_in_check, check_point=task_checkpoint)
            if checkpoint_order_items.exists():
                # if CheckPointOrderItem exists then update comment and rate for it
                checkpoint_order_item = checkpoint_order_items[0]
            else:
                # if CheckPointOrderItem not exists then create a new instance
                checkpoint_order_item = CheckPointOrderItem.objects.create()
                
            checkpoint_order_item.order_in_check=order_in_check
            checkpoint_order_item.check_point=task_checkpoint
            checkpoint_order_item.rate=int(request_post.get('rate'+task_checkpoint_id, 0))
            checkpoint_order_item.comment=request_post.get('comment'+task_checkpoint_id, '')
            checkpoint_order_item.save()

        return super().form_valid(form)

    def get_success_url(self):
        if self.success_url:
            url = self.success_url.format(**self.object.__dict__)
        else:
            url = reverse_lazy('apporders:order_view', kwargs={'pk': self.object.order.id})
            # url = reverse_lazy('apptasks:task_list')
        return url
    

    def get_context_data(self, **kwargs):
        
        context = super(OrderInChekUpdateView, self).get_context_data(**kwargs)

        # найдем все проверенные чекпоинты и получим по ним заполненные комменты и оценки
        checkpoints = []
        
        checkpoint_list = CheckPoint.objects.filter(task=self.object.order.task)
        for checkpoint in checkpoint_list:
            data = {'title': checkpoint, 'id': checkpoint.id}
            try:
                chp = CheckPointOrderItem.objects.get(check_point=checkpoint, order_in_check=self.object)
                data['comment'] = chp.comment
                data['rate'] = chp.rate
            except:
                data['comment'] = ''
                data['rate'] = ''
            checkpoints.append(data)        

        context['checkpoints'] = checkpoints
        context['checkpoints_count'] = checkpoint_list.count()

        context.update(AccountFunctions.get_profile_description(self.object.order.user))

        return context
    

@verified_email_required
def order_update(request, pk):
    
    order_inst = get_object_or_404(Order, pk = pk)

    if order_inst.user != request.user:
        raise Http404(_("Такой страницы не существует"))

    if request.method == 'POST':
        
        order_update_form = OrderUpdateForm(request.POST)
        
        if order_update_form.is_valid():
            
            # Обновляем данные заказа
            # order_inst.comment = order_update_form.cleaned_data['comment']

            order_inst.comment = request.POST.get('comment', '')
            order_inst.comment_HTML = request.POST.get('comment_format', '')

            order_inst.code_url = order_update_form.cleaned_data['code_url'] if order_update_form.cleaned_data['code_url'] else ''
            order_inst.build_url = order_update_form.cleaned_data['build_url']

            # Проверяем корректность доменных имен
            error_data = []

            import re

            regex = r"(?:[\w-]+\.)+[\w-]+"

            if order_inst.task.code_storage:
                available_domains = ()
                if order_inst.task.code_storage == '1' or order_inst.task.code_storage == '3':
                    available_domains = ('github.com',)
                elif order_inst.task.code_storage == '2':
                    pass
                    # available_domains = (
                    #     'github.com', 
                    #     'drive.google.com',
                    #     'yadi.sk',
                    #     'dl.dropboxusercontent.com',
                    #     'dropbox.com',
                    #     'jsfiddle.net',
                    #     'codepen.io',
                    #     'plnkr.co',
                    #     )

                if order_inst.task.code_storage == '1' or (order_inst.task.code_storage == '3' and order_inst.code_url.strip()):
                    matches = re.finditer(regex, order_inst.code_url.lower().replace('www.', ''))
                    for match in matches:
                        domen = match.group()
                        if domen not in available_domains:
                            error_data.append('code_url')

            if order_inst.task.build_storage != '1':
                available_domains = ()
                if order_inst.task.build_storage == '2':
                    available_domains = ('github.com', 'pages.github.com')
                elif order_inst.task.build_storage == '3':
                    available_domains = ('heroku.com')
                elif order_inst.task.build_storage == '4':
                    available_domains = ('github.com', 'pages.github.com', 'heroku.com')

                matches = re.finditer(regex, order_inst.build_url.lower().replace('www.', ''))
                for match in matches:
                    domen = match.group()
                    if domen not in available_domains:
                        error_data.append('build_url')

            if error_data:
                return JsonResponse({'response': 'error', 'error_data': error_data})
            else:
                if order_inst.status == 'inprogress':
                    order_inst.status = 'for_check'
                order_inst.save()
                return JsonResponse({'response': order_inst.get_absolute_url()})

        else:
            error_data = []
            for error in order_update_form.errors:
                error_data.append(error)
            return JsonResponse({'response': 'error', 'error_data': error_data})

    elif request.method == 'GET':
        
        task = Task.objects.select_related('skill', 'author', 'author__profile').get(pk=order_inst.task.id)

        context = {
            'order_update_form': OrderUpdateForm(instance=order_inst),
            'order_id': order_inst.id,
        }

        context['task'] = task
        context['task_short'] = task.title[0:40]
        context['task_url'] = task.get_absolute_url()
        context['task_href_title_prefix'] = TASK_HREF_TITLE_PREFIX
        context['profile_href_title_prefix'] = PROFILE_HREF_TITLE_PREFIX
        context['skill'] = task.skill.title
        context['task_description'] = task.description
        context['author'] = task.author
        context['author_url'] = task.author.profile.get_absolute_url()
        context['code_storage'] = task.code_storage
        context['build_storage'] = task.build_storage
        
        context['updated'] = order_inst.updated
        context['status'] = order_inst.status
        context['status_display'] = order_inst.get_status_display()
        context['comment_HTML_JSON'] = order_inst.comment_HTML
        context['check_url'] = reverse('apporders:order_update_check')
        
        context['btn_action_display'] = _('Завершить')
        
        if order_inst.status == 'inprogress':
            context['btn_action_display'] = _('Завершить')
        elif order_inst.status == 'for_check':
            context['btn_action_display'] = _('Сохранить ответ')
        elif order_inst.status == 'disabled':
            context['btn_action_display'] = _('Вернуть в работу')

        context['skill_title'] = task.skill.title
        
        if task.skill.avatar:
            context['skill_avatar'] = task.skill.avatar.url
        else:
            context['skill_avatar'] = ''

        context['skill_url'] = task.skill.get_absolute_url()

        params = {
            'order': order_inst,
            'add_checkpoints': True,
        }
        # context['order_in_check_list'] = OrderFunctions.get_order_in_check_list(**params)
        
        # найдем все проверки данного заказа
        # ищем записи в таблице OrderInCheck по текущему ордеру
        check_count = 0
        check_count_all = 0
        check_results = []
        check_result_list = OrderInCheck.objects.select_related('user', 'user__profile').filter(order=order_inst)
        checkpoint_task_list = CheckPoint.objects.filter(task=task)
        for order_in_check in check_result_list:
            
            check_count_all += 1
            
            data = {
                'order_in_check': order_in_check,
                'user': order_in_check.user,
                'user_avatar': order_in_check.user.profile.get_avatar_url(),
                'user_url': order_in_check.user.profile.get_absolute_url(),
                'updated': order_in_check.updated,
                'status_display': order_in_check.get_status_display(),
                'status': order_in_check.status,
                'check_rate': '--',
            }
            

            if order_in_check.status == 'done':
                check_count += 1
                # найдем все проверенные чекпоинты и получим по ним заполненные комменты и оценки
                check_rate = 0
                checkpoints_count = 0
                checkpoints = []
                for checkpoint in checkpoint_task_list:
                    checkpoint_data = {'title': checkpoint.title, 'id': checkpoint.id}
                    try:
                        chp = CheckPointOrderItem.objects.get(check_point=checkpoint, order_in_check=order_in_check)
                        checkpoint_data['comment'] = chp.comment
                        checkpoint_data['rate'] = chp.rate
                        check_rate += chp.rate
                        checkpoints_count += 1
                    except:
                        checkpoint_data['comment'] = ''
                        checkpoint_data['rate'] = ''

                    checkpoints.append(checkpoint_data)

                data['checkpoints'] = checkpoints
                check_rate = round(0 if checkpoints_count == 0 else check_rate / checkpoints_count, 1)
                data['check_rate'] = check_rate
                        
            check_results.append(data)

        context['check_count_all'] = check_count_all
        context['check_results'] = check_results
        total_score = order_inst.get_rate()
        context['total_score_display'] = total_score['rate_display']
        context['total_extra_score'] = total_score['extra_rate']
        context['total_extra_score_display'] = total_score['extra_rate_dispay']
        total_score_value = total_score['rate']
        star_class = {}
        for i in range(1,6):
            if total_score_value >= i:
                star_class[i] = 'star'
            elif total_score_value > i-1:
                star_class[i] = 'star_half'
            else:
                star_class[i] = 'star_border'
        context['star_class'] = star_class
        context['check_count'] = check_count

        return render(request, 'apporders/order_update.html', context)

    return JsonResponse({'response': '*response*'})


class OrderView(generic.DetailView):
    model = Order
    template_name = 'apporders/order_view.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super(OrderView, self).get_context_data(**kwargs)

        kwargs = {
            'pk': self.object.task.id,
            'user': self.request.user,
            'add_author_data': True,
            'add_skill_data': True,
            'add_order_data': True,
            'add_is_my_task': True,
            # 'add_fl_count': True,
            # 'add_is_my_task': True,
            # 'add_rating': True,
            'count': 1,
        }
        context['task'] = TaskFunctions.get_task_list(**kwargs)[0]

        if self.request.user.is_authenticated:
            order_in_check_list = OrderInCheck.objects.filter(user=self.request.user, order=self.object)
            if order_in_check_list.exists():
                context['order_in_check'] = order_in_check_list[0]

            user_request_order_list = Order.objects.filter(user=self.request.user, task=self.object.task)
            if user_request_order_list:
                context['user_request_order'] = user_request_order_list[0]

            # context.update(AccountFunctions.get_profile_description(self.object.user))

            context['is_favorite'] = self.object.is_favorite(user=self.request.user)
            context['is_like'] = self.object.is_like(user=self.request.user)
            context['answers_available'] = TaskFunctions.get_answers_available(context['task'], self.request.user)
        else:
            context['answers_available'] = False

        # forms
        context['order_in_check_creation_form'] = OrderInCheckCreationForm
        context['order_create_form'] = OrderCreationForm(initial={'user': self.request.user, 'task': self.object.task})
        context['favourite_update_form'] = FavouriteUpdateForm(initial={'order': self.object})
        context['like_update_form'] = LikeUpdateForm(initial={'order': self.object})

        return context


class FavouriteOrderListView(generic.ListView):
    model = Order
    template_name = 'apporders/favourite_order_list.html'
    paginate_by = 50

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """
        Декорируем диспетчер функцией login_required, чтобы запретить просмотр отображения неавторизованными
        пользователями
        """
        return super(FavouriteOrderListView, self).dispatch(request, *args, **kwargs)
        
    def get_paginate_by(self, queryset):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        return self.paginate_by
        
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)

        objects_list = OrderFunctions.get_favourites_order_list(user=self.request.user)

        # пагинация
        page_size = self.get_paginate_by(objects_list)
        if page_size:
            paginator, page, objects_list, is_paginated = self.paginate_queryset(
                objects_list, page_size)
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': objects_list
            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': objects_list
            }

        context['order_count'] = len(objects_list)
        context['orders'] = objects_list

        return context


@require_POST
def order_favourite_update(request):
    
    """
    add or del record in OrderFavourites
    """

    form = FavouriteUpdateForm(request.POST)
    
    result = False

    if form.is_valid():
        
        cd = form.cleaned_data
        order = cd['order']

        records = OrderFavourites.objects.filter(order=order, user=request.user)
        if records.exists():
            # if user has this order in his favourites then del this record
            record = records[0]
            record.delete()
            result = False
        else:
            # if user doesn't have this order in his favourites then add record
            record = OrderFavourites.objects.create(order=order, user=request.user)
            record.save()
            result = True
        
    return JsonResponse({'is_favourite': result})


@require_POST
def order_like_update(request):
    
    """
    add or del record in OrderLike
    """

    form = LikeUpdateForm(request.POST)
    
    result = False

    if form.is_valid():
        
        cd = form.cleaned_data
        order = cd['order']

        records = OrderLike.objects.filter(order=order, user=request.user)
        if records.exists():
            # if user has this order in his likes then del this record
            record = records[0]
            record.delete()
            result = False
        else:
            # if user doesn't have this order in his likes then add record
            record = OrderLike.objects.create(order=order, user=request.user)
            record.save()
            result = True
        
    return JsonResponse({'is_like': result})

