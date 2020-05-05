from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.decorators.http import require_POST
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

# from allauth.account.decorators import verified_email_required
from appaccounts.decorators import verified_email_required

from . import functions as TaskFunctions
from .models import Task, CheckPoint, Skill, TaskRatings, TaskFavourites, TaskLike
from .forms import FavouriteFormPOST, AddLikeForm, SetRatingForm, TaskUpdateForm

from apporders import functions as OrderFunctions
from apporders.models import Order, OrderInCheck
from apporders.forms import OrderCreationForm, OrderInCheckCreationForm, OrderStatusUpdateForm


class TaskListView(generic.ListView):
    model = Task
    template_name = 'apptasks/task_list.html'
    paginate_by = 25

    def get_queryset(self):
        return Task.objects.all()

    def get_paginate_by(self, queryset):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        return self.paginate_by    

    def get_context_data(self, **kwargs):
        
        if kwargs and 'skill' in kwargs:
            skill = kwargs['skill']
        else:
            skill = None

        self_request = self.request
        request_user = self_request.user
        
        filter_list = {
            'filter_author': 0,
            'filter_status': 0,
        }        
        
        if self_request.method == 'GET':
            filter_list['filter_status'] = str(self_request.GET.get('filterStatus', 0))
            filter_list['filter_author'] = str(self_request.GET.get('filterAuthor', 0))
            
        kwargs = {
            'add_author_data': True,
            'add_skill_data': True,
            'add_fl_count': True,
            'add_rating': True,
            'skill': skill,
        }
        
        if self.request.user.is_authenticated:
            
            kwargs['user'] = self.request.user
            kwargs['add_order_data'] = True
            
            if filter_list['filter_status'] == '1':
                kwargs['filter_status'] = '-'
                kwargs['user'] = request_user
            if filter_list['filter_status'] == '2':
                kwargs['filter_status'] = '*'
                kwargs['user'] = request_user
            if filter_list['filter_author'] == '1':
                kwargs['filter_author'] = '!='
                kwargs['author'] = request_user
            if filter_list['filter_author'] == '2':
                kwargs['filter_author'] = '=='
                kwargs['author'] = request_user
        
        task_list = TaskFunctions.get_task_list(**kwargs)

        # пагинация
        page_size = self.get_paginate_by(task_list)
        if page_size:
            paginator, page, task_list, is_paginated = self.paginate_queryset(
                task_list, page_size)
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': task_list
            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': task_list
            }

        context.update(filter_list)

        context['tasks'] = task_list

        return context


class TaskDetailView(generic.DetailView):
    model = Task
    template_name = 'apptasks/task_detail.html'

    def get_context_data(self, **kwargs):
        
        context = super(TaskDetailView, self).get_context_data(**kwargs)

        kwargs = {
            'pk': self.object.id,
            'user': self.request.user,
            'add_author_data': True,
            'add_skill_data': True,
            'add_is_fl': True,
            'add_is_my_task': True,
            'add_rating': True,
            'count': 1,
        }
        context['task'] = TaskFunctions.get_task_list(**kwargs)[0]
        context['checkpoints'] = CheckPoint.objects.filter(task=self.object).order_by('order')

        if self.request.user.is_authenticated:
            context['user_authenticated'] = True
            context['answers_available'] = TaskFunctions.get_answers_available(self.object, self.request.user)
            context['is_favorite'] = context['task'].is_favorite(self.request.user)
            context['is_like'] = context['task'].is_like(self.request.user)
            orders = Order.objects.filter(task=context['task'], user=self.request.user)
            if orders.exists():
                context['order'] = orders[0]
            else:
                context['order'] = None
        else:
            context['user_authenticated'] = False
        
        context['order_creation_form'] = OrderCreationForm(initial={'user': self.request.user, 'task': context['task']})

        # lis of user's orders
        kwargs = {
            'filter_user': '!=',
            'user': self.request.user,
            'add_skill_data': True,
            'add_author_data': True,
            'add_order_in_check_data': True,
            'task': context['task'],
            'status': 'for_check',
        }
        context['order_for_check_list'] = OrderFunctions.get_order_list(**kwargs)

        # forms
        context['order_status_update_form'] = OrderStatusUpdateForm()
        context['favourite_update_form'] = FavouriteFormPOST()
        context['like_update_form'] = AddLikeForm(initial={'task': context['task']})
        context['set_rating_form'] = SetRatingForm(initial={'task': context['task']})
                                    
        return context


class SkillDetailView(generic.DetailView):
    model = Skill
    template_name = 'apptasks/skill_detail.html'
    paginate_by = 25
    paginate_orphans = 0
    allow_empty = True
    paginator_class = Paginator
    page_kwarg = 'page'

    def get_paginate_by(self, queryset):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        return self.paginate_by

    def get_allow_empty(self):
        """
        Return ``True`` if the view should display empty lists and ``False``
        if a 404 should be raised instead.
        """
        return self.allow_empty

    def get_paginate_orphans(self):
        """
        Return the maximum number of orphans extend the last page by when
        paginating.
        """
        return self.paginate_orphans

    def get_paginator(self, queryset, per_page, orphans=0,
                      allow_empty_first_page=True, **kwargs):
        """Return an instance of the paginator for this view."""
        return self.paginator_class(
            queryset, per_page, orphans=orphans,
            allow_empty_first_page=allow_empty_first_page, **kwargs)

    def paginate_queryset(self, queryset, page_size):
        """Paginate the queryset, if needed."""
        paginator = self.get_paginator(
            queryset, page_size, orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty())
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404(_('Page is not “last”, nor can it be converted to an int.'))
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            raise Http404(_('Invalid page (%(page_number)s): %(message)s') % {
                'page_number': page_number,
                'message': str(e)
            })

    def get_context_data(self, **kwargs):
        context = TaskListView.get_context_data(self, skill=self.object)
        context['skill'] = self.object
        return context


class FavouriteTaskListView(generic.ListView):
    model = Task
    template_name = 'apptasks/favourite_task_list.html'
    paginate_by = 50

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """
        Декорируем диспетчер функцией login_required, чтобы запретить просмотр отображения неавторизованными
        пользователями
        """
        return super(FavouriteTaskListView, self).dispatch(request, *args, **kwargs)
        
    def get_paginate_by(self, queryset):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        return self.paginate_by
        
    def get_queryset(self):
        return TaskFavourites.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)

        task_list = TaskFunctions.get_favourites_task_list(user=self.request.user)

        # пагинация
        page_size = self.get_paginate_by(task_list)
        if page_size:
            paginator, page, task_list, is_paginated = self.paginate_queryset(
                task_list, page_size)
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': task_list
            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': task_list
            }

        context['task_count'] = len(task_list)
        context['tasks'] = task_list

        return context

@verified_email_required
@login_required
def task_update(request, pk=None):
    
    import json
    
    if request.method == 'POST':

        if len(request.POST['text']) > settings.TASK_DESCRIPTION_LEN_MAX or len(request.POST['text']) < settings.TASK_DESCRIPTION_LEN_MIN:
            return JsonResponse({'response': 'error'})
        elif pk:

            task_inst = get_object_or_404(Task, pk = pk)

            task_update_form = TaskUpdateForm(request.POST)

            if task_update_form.is_valid():
                
                # Обновляем данные задачи
                task_inst.title = task_update_form.cleaned_data['title']
                task_inst.skill = task_update_form.cleaned_data['skill']
                task_inst.extra_skill1 = task_update_form.cleaned_data['extra_skill1']
                task_inst.extra_skill2 = task_update_form.cleaned_data['extra_skill2']
                task_inst.extra_skill3 = task_update_form.cleaned_data['extra_skill3']
                task_inst.description = request.POST['text']
                task_inst.description_short = request.POST['text_short']
                task_inst.description_HTML = request.POST['text_format']
                task_inst.code_storage = str(request.POST['code_storage'])
                task_inst.build_storage = str(request.POST['build_storage'])
                task_inst.save()

                checkpoints = json.loads(request.POST['checkpoints'])
                for checkpoint in checkpoints:
                    checkpoint_id = checkpoint['id']
                    new_checkpoint = None
                    deleted = False
                    if checkpoint_id:
                        checkpoint_qs = CheckPoint.objects.filter(id=checkpoint['id'], task=task_inst)
                        if not checkpoint_qs:
                            if checkpoint['remove'] == False:
                                new_checkpoint = CheckPoint.objects.create(title=checkpoint['title'], task=task_inst, order=int(checkpoint['order']))
                        else:
                            new_checkpoint = checkpoint_qs[0]
                            if checkpoint['remove'] == True:
                                deleted = True
                                new_checkpoint.delete()
                            else:
                                new_checkpoint.title = checkpoint['title']
                                new_checkpoint.order = checkpoint['order']
                    else:
                        if checkpoint['remove'] == True:
                            deleted = True
                        else:
                            deleted = False
                            new_checkpoint = CheckPoint.objects.create(title=checkpoint['title'], task=task_inst, order=int(checkpoint['order']))
                    
                    if not deleted:
                        new_checkpoint.save()

                return JsonResponse({'response': task_inst.get_absolute_url()})
            else:
                return JsonResponse({'response': 'error'})

        else:

            task_create_form = TaskUpdateForm(request.POST)
            if task_create_form.is_valid():
                
                import json
                
                # Создаем новую задачу
                new_task = task_create_form.save(commit=False)
                new_task.author = request.user
                new_task.description = request.POST['text']
                new_task.description_short = request.POST['text_short']
                new_task.description_HTML = request.POST['text_format']
                new_task.code_storage = str(request.POST['code_storage'])
                new_task.build_storage = str(request.POST['build_storage'])
                new_task.save()

                checkpoints = json.loads(request.POST['checkpoints'])
                for checkpoint in checkpoints:
                    checkpoint_id = checkpoint['id']
                    new_checkpoint = None
                    deleted = False
                    if checkpoint['remove'] != True:
                        new_checkpoint = CheckPoint.objects.create(title=checkpoint['title'], task=new_task, order=int(checkpoint['order']))
                        new_checkpoint.save()

                return JsonResponse({'response': new_task.get_absolute_url()})
            else:
                return JsonResponse({'response': 'error'})
        
    elif request.method == 'GET':
        
        if pk:

            task_inst = get_object_or_404(Task, pk = pk)

            if task_inst.author != request.user:
                raise Http404(_("Такой страницы не существует"))

            checkpoints = CheckPoint.objects.filter(task=task_inst).order_by('order')
        
            context = {
                'action_title': _('Редактирование задачи'),
                'btn_action_title': _('Сохранить изменения'),
                'task_update_form': TaskUpdateForm(instance=task_inst),
                'post_url': reverse('apptasks:task_update', args=[str(pk)]),
                'check_url': reverse('apptasks:task_update_check'),
                'task_id': task_inst.id,
                'task_url': task_inst.get_absolute_url(),
                'title': task_inst.title,
                'title_short': task_inst.title[0:40],
                'checkpoints': checkpoints,
                'description_HTML_JSON': task_inst.description_HTML,
                'code_storage': task_inst.code_storage,
                'build_storage': task_inst.build_storage,
            }
        else:
            checkpoints = [{'title': _('Результат решения соответствует ожиданиям'), 'id': 1}]
            context = {
                'action_title': _('Создание задачи'),
                'btn_action_title': _('Создать задачу'),
                'task_update_form': TaskUpdateForm(),
                'post_url': reverse('apptasks:task_create'),
                'check_url': reverse('apptasks:task_update_check'),
                'task_id': '',
                'task_url': '',
                'title': '',
                'title_short': '',
                'checkpoints': checkpoints,
                'description_HTML_JSON': '',
                'code_storage': '1',
                'build_storage': '1',
            }
        
        return render(request, 'apptasks/task_update.html', context)

    return JsonResponse({'response': '*response*'})


class MyTaskListView(generic.ListView):
    model = Task
    template_name = 'apptasks/my_task_list.html'
    paginate_by = 25

    def get_paginate_by(self, queryset):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        return self.paginate_by
        
    def get_queryset(self):
        return Task.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        kwargs = {
            'filter_author': '==',
            'author': self.request.user,
            'add_author_data': True,
            'add_skill_data': True,
        }
        task_list = TaskFunctions.get_task_list(**kwargs)

        # пагинация
        page_size = self.get_paginate_by(task_list)
        if page_size:
            paginator, page, task_list, is_paginated = self.paginate_queryset(
                task_list, page_size)
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': task_list
            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': task_list
            }

        context['task_count'] = len(task_list)
        context['tasks'] = task_list
        context['task_href_title_prefix'] = settings.TASK_HREF_TITLE_PREFIX
        context['skill_href_title_prefix'] = settings.SKILL_HREF_TITLE_PREFIX

        return context
