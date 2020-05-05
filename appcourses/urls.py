from django.conf.urls import url
from . import views
from .api import check_answer, quiz_restart


app_name = 'appcourses'

urlpatterns = [

    # courses
    # courses: library
    url(r'^$', views.LibraryListView.as_view(), name='library'),

    # courses: course overview
    url(r'^(?P<slug>[-\w]+)/$', views.CourseDetailView.as_view(), name='course_overview'),

    # courses: enroll to course
    url(r'^course-update/enroll-to-course/$', views.enroll_to_course, name='enroll_to_course'),

    # lessons
    # lessons: lesson detail
    url(r'^(?P<course_slug>[-\w]+)/lessons/(?P<module_slug>[-\w]+)/(?P<slug>[-\w]+)/$',
        views.LessonDetailView.as_view(),
        name='lesson_detail'),

    # lessons: add lesson to complete
    url(r'^lesson-update/complete-lesson/$', views.complete_lesson, name='complete_lesson'),

    # lessons: module review
    url(r'^(?P<course_slug>[-\w]+)/module-review/(?P<slug>[-\w]+)/$',
        views.ModuleReviewView.as_view(),
        name='module_review'),

    # lessons: course review
    url(r'^course-review/(?P<slug>[-\w]+)/$', views.CourseReviewView.as_view(), name='course_review'),

    # lessons: send module review
    url(r'^api/send-module-review/$', views.ModuleReviewView.as_view(), name='send_module_review'),

    # lessons: send course review
    url(r'^api/send-course-review/$', views.CourseReviewView.as_view(), name='send_course_review'),

    # quiz
    # quiz: exam overview
    url(r'^assessment/(?P<slug>[-\w]+)/$', views.ExamOverview.as_view(), name='exam_overview'),

    # quiz: exam progress
    url(r'^assessment/(?P<slug>[-\w]+)/progress/$', views.ExamProgress.as_view(), name='exam_progress'),

    # quiz: check answer
    url(r'^api/check-answer/$', check_answer, name='check_answer'),

    # quiz: restart
    url(r'^api/quiz-restart/$', quiz_restart, name='quiz_restart'),

    # manage
    # manage-course: course create
    url(r'^manage/course-create/$', views.ManageCourseCreateView.as_view(), name='manage_course_create'),

    # manage-course: course update
    url(r'^manage/course-update/(?P<slug>[-\w]+)/$', views.ManageCourseUpdateView.as_view(),
        name='manage_course_update'),

    # manage-course: course change public
    url(r'^manage/course-change-public/(?P<pk>\d+)/$', views.ManageCoursePublicView.as_view(),
        name='manage_course_change_public'),

    # manage-module: module update
    url(r'^manage/module-update/(?P<slug>[-\w]+)/$', views.ManageModuleUpdateView.as_view(),
        name='manage_module_update'),

    # manage-module: module change public
    url(r'^manage/module-change-public/(?P<pk>\d+)/$', views.ManageModulePublicView.as_view(),
        name='manage_module_change_public'),

    # manage-lesson: lesson update
    url(r'^manage/lesson-update/(?P<slug>[-\w]+)/$', views.ManageLessonUpdateView.as_view(),
        name='manage_lesson_update'),

    # manage-lesson: lesson change public
    url(r'^manage/lesson-change-public/(?P<pk>\d+)/$', views.ManageLessonPublicView.as_view(),
        name='manage_lesson_change_public'),

    # manage-content: content update
    url(r'^manage/content-update/(?P<pk>\d+)/$', views.ManageContentUpdateView.as_view(),
        name='manage_content_update'),

    # manage-content: content change public
    url(r'^manage/content-change-public/(?P<pk>\d+)/$', views.ManageContentPublicView.as_view(),
        name='manage_content_change_public'),

    # manage-quiz: quiz create
    url(r'^manage/quiz-create/$', views.ManageQuizCreateView.as_view(), name='manage_quiz_create'),

    # manage-quiz: quiz update
    url(r'^manage/quiz-update/(?P<slug>[-\w]+)/$', views.ManageQuizUpdateView.as_view(),
        name='manage_quiz_update'),

    # manage-quiz: quiz change public
    url(r'^manage/quiz-change-public/(?P<pk>\d+)/$', views.ManageQuizPublicView.as_view(),
        name='manage_quiz_change_public'),

    # manage-question: question update
    url(r'^manage/question-update/(?P<pk>\d+)/$', views.ManageQuestionUpdateView.as_view(),
        name='manage_question_update'),

    # manage-question: question change public
    url(r'^manage/question-change-public/(?P<pk>\d+)/$', views.ManageQuestionPublicView.as_view(),
        name='manage_question_change_public'),

]
