from django.urls import path
from django.conf.urls import url
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from allauth.account.decorators import verified_email_required

from . import views, api

app_name = 'apporders'

urlpatterns = [
    # url(r'^list$', views.OrderForCheckListView.as_view(), name='order-for-check-list'),
    # url(r'^list$', views.order_for_check_list, name='order_for_check_list'),
    # url(r'^order_in_check/(?P<pk>\d+)$', views.OrderInChekDetailView.as_view(), name='order_in_check_detail'),
    url(r'^order_view/(?P<pk>\d+)$', login_required(views.OrderView.as_view()), name='order_view'),
    url(r'^favourites$', login_required(views.FavouriteOrderListView.as_view()), name='favourite_list'),
    

    # edit
    url(r'^order_create/$', login_required(views.order_create), name='order_create'),
    url(r'^(?P<pk>\d+)/$', login_required(views.order_update), name='order_update'),
    url(r'^order_status_update/(?P<pk>\d+)/$', login_required(views.order_status_update), name='order_status_update'),
    url(r'^order_in_check_create/(?P<order_for_check_id>\d+)/$', login_required(views.order_in_check_create), name='order_in_check_create'),
    url(r'^order_in_check/(?P<pk>\d+)/edit/$', login_required(verified_email_required(views.OrderInChekUpdateView.as_view())), name='order_in_check_update'),

    # favourite and like
    url(r'^favourite_update/$', login_required(views.order_favourite_update), name='favourite_update'),
    url(r'^like_update/$', login_required(views.order_like_update), name='like_update'),
    
    # api
    url(r'^order_update_check$', login_required(api.order_update_check), name='order_update_check'),
]