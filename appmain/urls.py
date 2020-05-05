from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import (
    main_page,
    dashboard,
    dashboard_task,
    MyOrderListView,
    DashboardManage,
    QuizResults,
    MyAchievements,
    Exams,
)

app_name = 'appmain'

urlpatterns = [

    # index
    url(r'^$', main_page, name='index'),

    # dashboard
    url(r'^dashboard/$', dashboard, name='dashboard'),
    url(r'^dashboard/(?P<section>[-:\w]+)/$', dashboard, name='dashboard_section'),

    # dashboard-quiz: list - user results
    url(r'^my-achievements/$', MyAchievements.as_view(), name='my_achievements'),

    # dashboard-quiz: list - all quizzes
    url(r'^exams/$', Exams.as_view(), name='exams'),

    # dashboard-quiz: detail of user result
    url(r'^quiz-results/(?P<slug>[-\w]+)/$', QuizResults.as_view(), name='quiz_results'),

    # dashboard manage
    url(r'^dshm/(?P<section>[-:\w]+)/$', DashboardManage.as_view(), name='dashboard_manage_section'),
    url(r'^dshm/$', DashboardManage.as_view(), name='dashboard_manage'),


    # urls task
    url(r'^dashboard_task', dashboard_task, name='dashboard_task'),
    url(r'^myorders$', login_required(MyOrderListView.as_view()), name='my_order_list'),
]