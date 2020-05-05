from django.contrib import admin
from .models import Order, OrderInCheck, CheckPointOrderItem, OrderFavourites, OrderLike

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'task', 'status', 'created')

@admin.register(OrderInCheck)
class OrderInCheckAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order', 'status', 'created')

@admin.register(CheckPointOrderItem)
class CheckPointOrderItemAdmin(admin.ModelAdmin):
    # list_display = ('id', 'user', 'check_point', 'user_order', 'order_in_check', 'rate', 'created')
    list_display = ('id', 'check_point', 'order_in_check', 'rate', 'created')

@admin.register(OrderFavourites)
class OrderFavouritesAdmin(admin.ModelAdmin):
     list_display = ('order', 'user', 'created')


@admin.register(OrderLike)
class OrderLikeAdmin(admin.ModelAdmin):
     list_display = ('order', 'user', 'created')