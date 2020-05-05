from django import template
from apporders.models import Order

register = template.Library()


@register.filter(name='get_badge_class_for_order_status')
def get_badge_class_for_order_status(order_status):
    if order_status == 'inprogress':
        return 'badge-warning'
    elif order_status == 'done':
        return 'badge-success'
    elif order_status == 'for_check':
        return 'badge-success'
    elif order_status == 'disabled':
        return 'badge-danger'
    else:
        return ''


@register.simple_tag
def define(val=None):
  return val
