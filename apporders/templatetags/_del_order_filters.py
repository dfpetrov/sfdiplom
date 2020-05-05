from django import template
from apporders.models import Order

register = template.Library()

@register.simple_tag
def get_answers_available(task, user):
    from django.db.models import Q
    order_exists = Order.objects.filter(Q(task=task) & Q(user=user) & (Q(status='for_check') | Q(status='done'))).exists()

    return order_exists or task.author == user