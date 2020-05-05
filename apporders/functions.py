from django.conf import settings
from .models import Order, OrderInCheck, OrderFavourites, OrderLike

def get_order_list(prefix='', filter_user=None, user=None, 
                    add_author_data=False, add_task_data=False, add_skill_data=False, add_order_in_check_data=False,
                    task=None, status=None, add_fl_count=False, 
                    ordered='-created', count=None):
    """
    Return a list of order.

    The arguments:

        ``filter_user`` - set filter on Order.user. A string. Can be:
        - '==': select all orders with order.user == user
        - '!=': select all orders with order.user != user
        - None: select all orders without filter

        ``user`` - user of order (model - User)

        ``add_skill_data`` - add select_related('task__skill')

        ``add_fl_count`` - add fields:
                favourite_count=Count('order_favourites')
                like_count=Count('order_like')
    """

    from django.db.models import Q, Count, Case, When, Sum, Max, IntegerField, CharField, DateTimeField, Subquery, OuterRef
    from django.db.models.functions import Substr

    order_qset = Order.objects

    if add_skill_data:
        order_qset = order_qset.select_related('task__skill')

    if add_task_data:
        order_qset = order_qset.select_related('task')
        
    if add_author_data:
        order_qset = order_qset.select_related('user__profile')

    if not filter_user and not task and not status:
        order_qset = order_qset.all()
    else:
        
        if user and user.is_authenticated:
            # set filter on user
            if filter_user == '==':
                order_qset = order_qset.filter(Q(user=user))
            elif filter_user == '!=':
                order_qset = order_qset.filter(~Q(user=user))

        # set filter on task
        if task:
            order_qset = order_qset.filter(Q(task=task))

        # set filter on status
        if status:
            order_qset = order_qset.filter(Q(status=status))

    if add_fl_count:
        # get favourite_count via Subquery
        order_qset = order_qset.annotate(
            favourite_count=Subquery(
                OrderFavourites.objects.filter(
                    order=OuterRef('pk')
                ).values(
                    'order'
                ).annotate(
                    favourite_count=Count('order'),
                ).values('favourite_count')[:1]
            )
        )
        # get like_count via Subquery
        order_qset = order_qset.annotate(
            like_count=Subquery(
                OrderLike.objects.filter(
                    order=OuterRef('pk')
                ).values(
                    'order'
                ).annotate(
                    like_count=Count('order'),
                ).values('like_count')[:1]
            )
        )

    if user and user.is_authenticated:

        if add_order_in_check_data:
            # get order_in_check data via Subquery
            order_qset = order_qset.annotate(
                order_in_check_id=Subquery(
                    OrderInCheck.objects.filter(
                        Q(order=OuterRef('pk')) & Q(user=user)
                    ).values(
                        'id'
                    ).annotate(
                        order_in_check_id=Max('id'),
                    ).values('order_in_check_id')[:1]
                )
            )
            order_qset = order_qset.annotate(
                order_in_check_status=Subquery(
                    OrderInCheck.objects.filter(
                        Q(order=OuterRef('pk')) & Q(user=user)
                    ).values(
                        'status'
                    ).annotate(
                        order_in_check_status=Max('status'),
                    ).values('order_in_check_status')[:1]
                )
            )
            order_qset = order_qset.annotate(
                order_in_check_update=Subquery(
                    OrderInCheck.objects.filter(
                        Q(order=OuterRef('pk')) & Q(user=user)
                    ).values(
                        'updated'
                    ).annotate(
                        order_in_check_update=Max('updated'),
                    ).values('order_in_check_update')[:1]
                )
            )
            # order_qset = order_qset.annotate(
            #                 order_in_check_id=Max(Case(
            #                     When(order_order_in_check__user=user, then='order_order_in_check__id'),
            #                     default=None,
            #                     output_field=CharField(),
            #                 )),
            #                 order_in_check_status=Max(Case(
            #                     When(order_order_in_check__user=user, then='order_order_in_check__status'),
            #                     default=None,
            #                     output_field=CharField(),
            #                 )),
            #                 order_in_check_update=Max(Case(
            #                     When(order_order_in_check__user=user, then='order_order_in_check__updated'),
            #                     default=None,
            #                     output_field=DateTimeField(),
            #                 )),
            #             )

    order_qset = order_qset.annotate(task_title_short=Substr('task__title', 1, settings.TASK_TITLE_LEN_SHORT), task_description_short=Substr('task__description_short', 1, settings.TASK_DESCRIPTION_LEN_SHORT))
    order_qset = order_qset.order_by(ordered)

    if count:
        return list(order_qset[:count])
    else:
        return list(order_qset)

def get_order_in_check_list(**kwargs):
    """
    Return a list of order.

    The arguments:

        ``filter_user`` - set filter on Order.user. A string. Can be:
        - '==': select all orders with order.user == user
        - '!=': select all orders with order.user != user
        - None: select all orders without filter

        ``user`` - user of order (model - User)

        ``add_skill_data`` - add select_related('task__skill')

        ``add_fl_count`` - add fields:
                favourite_count=Count('order_favourites')
                like_count=Count('order_like')
    """

    from django.db.models import Q, Count, Case, When, Sum, Max, IntegerField, CharField, DateTimeField, Subquery, OuterRef
    from django.db.models.functions import Substr

    

    _ = {
        'order': None,
        'ordered': None,
        'count': None,
        'add_checkpoints': None,
    }

    if kwargs:

        for k in _.keys():
            if k in kwargs:
                _[k] = kwargs[k]

    if _['order']:

        objects_qset = OrderInCheck.objects

        if _['ordered']:
            objects_qset = objects_qset.order_by(_['ordered'])
            
        if _['add_checkpoints']:
            objects_qset = objects_qset.select_related('order')

        objects_qset = objects_qset.prefetch_related('order_in_check_checkpoint')

        objects_qset = objects_qset.filter(order=_['order'])

        if _['count']:
            return list(objects_qset[:_['count']])
        else:
            return list(objects_qset)

    else:
        return []


def get_favourites_order_list(user=None, ordered='-created', count=None):
    """
    Return a list of order from favourites.

    The arguments:

        *user: set filter on user
        
        *ordered: sort direction

        *count: count of tasks in the list
    """
    from django.db.models.functions import Substr

    objects_qset = OrderFavourites.objects.select_related('order', 'order__user', 'order__user__profile', 'order__task', 'order__task__skill')
    
    if user and user.is_authenticated:
        objects_qset = objects_qset.filter(user=user)
    else:
        objects_qset = objects_qset.all()

    objects_qset = objects_qset.annotate(title_short=Substr('order__task__title', 1, settings.TASK_TITLE_LEN_SHORT))
    objects_qset = objects_qset.order_by(ordered)

    if count:
        return list(objects_qset[:count])
    else:
        return list(objects_qset)

