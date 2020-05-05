from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy

from . import views, api

app_name = 'apptasks'

urlpatterns = [
    
    # list
    url(r'^list$', views.TaskListView.as_view(), name='task_list'),
    
    # detail
    url(r'^(?P<pk>\d+)/$', views.TaskDetailView.as_view(), name='task_detail'),    
    url(r'^skill/(?P<pk>\d+)/$', views.SkillDetailView.as_view(), name='skill_detail'),

    # edit
    url(r'^create/$', views.task_update, name='task_create'),
    url(r'^(?P<pk>\d+)/edit$', views.task_update, name='task_update'),

    # login_required
    url(r'^my_task_list$', login_required(views.MyTaskListView.as_view()), name='my_task_list'),
    url(r'^favourite-task$', login_required(views.FavouriteTaskListView.as_view()), name='favourite_task_list'),

    # api
    url(r'^task_favourite_update/(?P<task_id>\d+)/$', login_required(api.task_favourite_update), name='task_favourite_update'),
    url(r'^task_like_update/$', login_required(api.task_like_update), name='task_like_update'),
    url(r'^task_update_check$', login_required(api.task_update_check), name='task_update_check'),
    url(r'^task_set_rating/$', login_required(api.task_set_rating), name='task_set_rating'),
]
