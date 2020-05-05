from django.conf import settings
from django.db.models import Q, Count, Case, When, Sum, Max, IntegerField, CharField, BooleanField, Value, Avg, Subquery, OuterRef
from django.db.models.functions import Substr
from django.utils.translation import gettext_lazy as _

from .models import Task, TaskFavourites, TaskLike, TaskRatings

from apporders.models import Order

def get_task_list(pk=None, skill=None, filter_author=False, author=None, filter_order=False, filter_status=False, 
                    order=None, add_author_data=False, add_skill_data=False, add_order_data=False, 
                    add_is_my_task=False, add_rating=False,
                    add_fl_count=False, add_is_fl=False, user=None, ordered='-created', count=None):
    """
    Return a list of task.

    The arguments:

        ``skill`` - set filter on Task.skill
        
        ``filter_author`` - set filter on Task.author. A string. Can be:
        - '==': select all task with author == author
        - '!=': select all task with author != author
        - None: select all task without filter

        ``author`` - author of task (model - User)

        ``filter_order`` - set filter on Order. A string. Can be:
        - '==': select all task for which Order == order
        - '!=': select all task for which Order != order
        - '*': select all task for which there is an Order
        - '-': select all task for which there is not an Order
        - None: select all task without filter

        ``add_author_data`` - add select_related('author__profile')
        
        ``add_skill_data`` - add select_related('skill')

        ``add_fl_count`` - add fields:
                favourite_count=Count('task_favourites')
                like_count=Count('task_like')
    """

    task_qset = Task.objects

    if add_author_data:
        task_qset = task_qset.select_related('author__profile')

    if add_skill_data:
        task_qset = task_qset.select_related('skill')

    if pk:
        task_qset = task_qset.filter(id=pk)
    elif not skill and not filter_author and not filter_order:
        task_qset = task_qset.all()
    else:

        # set filter on skill
        if skill:
            task_qset = task_qset.filter(skill=skill)
            
        # set filter on author
        if filter_author == '==':
            task_qset = task_qset.filter(author=author)
        elif filter_author == '!=':
            task_qset = task_qset.filter(~Q(author=author))

        # set filter on order
        if filter_order == '==':
            task_qset = task_qset.filter(Q(order_task=order))
        elif filter_order == '!=':
            task_qset = task_qset.filter(~Q(order_task=order))
        elif filter_order == '*':
            task_qset = task_qset.filter(~Q(order_task=None))
        elif filter_order == '-':
            task_qset = task_qset.filter(Q(order_task=None))

    if add_fl_count:
        # get favourite_count via Subquery
        task_qset = task_qset.annotate(
            favourite_count=Subquery(
                TaskFavourites.objects.filter(
                    task=OuterRef('pk')
                ).values(
                    'task'
                ).annotate(
                    favourite_count=Count('task'),
                ).values('favourite_count')[:1]
            )
        )
        # get like_count via Subquery
        task_qset = task_qset.annotate(
            like_count=Subquery(
                TaskLike.objects.filter(
                    task=OuterRef('pk')
                ).values(
                    'task'
                ).annotate(
                    like_count=Count('task'),
                ).values('like_count')[:1]
            )
        )
       
    if user and user.is_authenticated:

        if add_is_my_task:
            task_qset = task_qset.annotate(
                            is_my_task=Max(Case(
                                When(author=user, then=1),
                                default=0,
                                output_field=IntegerField(),
                            )),
                        )

        if add_order_data:

            # get data of order of task via Subquery
            task_qset = task_qset.annotate(
                order_status=Subquery(
                    Order.objects.filter(
                        Q(task=OuterRef('pk')) & Q(user=user)
                    ).values(
                        'status',
                    ).annotate(
                        order_status=Max('status'),
                    ).values('order_status')[:1]
                )
            )

            # task_qset = task_qset.annotate(
            #                 order_id=Max(Case(
            #                     When(order_task__user=user, then='order_task__id'),
            #                     default=None,
            #                     output_field=CharField(),
            #                 )),
            #                 order_status=Max(Case(
            #                     When(order_task__user=user, then='order_task__status'),
            #                     default=None,
            #                     output_field=CharField(),
            #                 )),
            #                 order_created=Max(Case(
            #                     When(order_task__user=user, then='order_task__status'),
            #                     default=None,
            #                     output_field=CharField(),
            #                 )),
            #             )
            # add order_status_display
            choices = dict(Order._meta.get_field('status').flatchoices)
            whens = [When(order_status=k, then=Value(v)) for k, v in choices.items()]
            task_qset = task_qset.annotate(order_status_display=Case(*whens, default=None, output_field=CharField()))

            if filter_status=='-':
                task_qset = task_qset.filter(Q(order_status=None))
            elif filter_status=='*':
                task_qset = task_qset.filter(~Q(order_status=None))
            elif filter_status:
                task_qset = task_qset.filter(Q(order_status=filter_status))

    # if add_is_fl:
    #     task_qset = task_qset.annotate(
    #                     is_favorite=Sum(Case(
    #                         When(task_favourites__user=user, then=1),
    #                         default=0,
    #                         output_field=IntegerField(),
    #                     )),
    #                     is_like=Sum(Case(
    #                         When(task_like__user=user, then=1),
    #                         default=0,
    #                         output_field=IntegerField(),
    #                     ))
    #                 )

    if add_rating:

        # get rating via Subquery
        task_qset = task_qset.annotate(
            rating=Subquery(
                TaskRatings.objects.filter(
                    task=OuterRef('pk')
                ).values(
                    'task'
                ).annotate(
                    the_sum=Avg('value'),
                ).values('the_sum')[:1]
            )
        )

    task_qset = task_qset.annotate(title_short=Substr('title', 1, settings.TASK_TITLE_LEN_SHORT))
    
    task_qset = task_qset.order_by(ordered)

    if count:
        return list(task_qset[:count])
    else:
        return list(task_qset)
    

def get_favourites_task_list(user=None, ordered='-created', count=None):
    """
    Return a list of task from favourites.

    The arguments:

        *user: set filter on user
        
        *ordered: sort direction

        *count: count of tasks in the list
    """
    task_qset = TaskFavourites.objects.select_related('task', 'task__author', 'task__author__profile', 'task__skill')
    
    if user and user.is_authenticated:
        task_qset = task_qset.filter(user=user)
    else:
        task_qset = task_qset.all()

    task_qset = task_qset.annotate(title_short=Substr('task__title', 1, settings.TASK_TITLE_LEN_SHORT))
    task_qset = task_qset.order_by(ordered)

    if count:
        return list(task_qset[:count])
    else:
        return list(task_qset)


def get_answers_available(task, user):
    
    if user and user.is_authenticated:
        order_exists = Order.objects.filter(Q(task=task) & Q(user=user) & (Q(status='for_check') | Q(status='done'))).exists()
    else:
        order_exists = False

    return order_exists or task.author == user