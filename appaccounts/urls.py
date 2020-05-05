from django.urls import path, re_path
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from django.contrib.auth.views import (
    LogoutView
)
from allauth.account.views import (
    LoginView, 
    SignupView, 
    ConfirmEmailView,
    PasswordResetView as AllAuthPasswordResetView,
    PasswordResetDoneView as AllAuthPasswordResetDoneView,
    PasswordResetFromKeyDoneView as AllAuthPasswordResetFromKeyDoneView
)

from .forms import (
    AllAuthLoginForm,
    AllAuthSignupForm,
    AllAuthResetPasswordForm
)
from . import views

app_name = 'appaccounts'

urlpatterns = [
    
    # url(r'^profile/(?P<pk>\d+)$', views.ProfileDetail.as_view(), name='profile'),
    # url(r'^profile/(?P<pk>\d+)/edit/$', login_required(views.ProfileUpdate.as_view()), name='profile_edit'),
    url(r'^profile/$', views.ProfileUpdate.as_view(), name='profile_edit'),
    
    ###################
    # Auth urls by Django
    ###################

    # register urls
    # url(r'^register/$', views.register, name='register'),
     
    # password reset
    # url(r'^password-reset/$', DjangoPasswordResetView.as_view(form_class=UserPasswordResetForm, success_url=reverse_lazy('appaccounts:password_reset_done')), name='password_reset'),
    # url(r'^password-reset/done/$', DjangoPasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    # url(r'^password-reset/confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$', DjangoPasswordResetConfirmView.as_view(form_class=UserSetPasswordForm, success_url=reverse_lazy('appaccounts:password_reset_complete')), name='password_reset_confirm'),
    # url(r'^password-reset/complete/$', DjangoPasswordResetCompleteView.as_view(), name='password_reset_complete'),


    ###################
    # Auth urls by AllAuth
    ###################

    # register urls
    url(r'^register/$', SignupView.as_view(form_class=AllAuthSignupForm, template_name='appaccounts/register.html'), name='register'),
    
    # password reset
    url(r'^password/reset/$', AllAuthPasswordResetView.as_view(form_class=AllAuthResetPasswordForm), name="password_reset"), 
    url(r'^password/reset/done/$', AllAuthPasswordResetDoneView.as_view(), name="account_reset_password_done"),
    # url(r'^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$', AllAuthPasswordResetFromKeyView.as_view(form_class=AllAuthResetPasswordKeyForm), name="account_reset_password_from_key"),
    url(r'^password/reset/key/done/$', AllAuthPasswordResetFromKeyDoneView, name="account_reset_password_from_key_done"),

    # Login
    url(r'^login/$', LoginView.as_view(form_class=AllAuthLoginForm, template_name='registration/login.html'), name='login'),
    # url(r'^logout/$', login_required(LogoutView.as_view()), name='logout'),
    # url(r'^login/$', views.CustomLoginView.as_view(form_class=AllAuthLoginForm, template_name='registration/login.html'), name='login'),
    url(r'^logout/$', login_required(views.CustomLogoutView.as_view()), name='logout'),

    # E-mail
    url(r'^email/$', views.AllAuthEmailView.as_view(), name="account_email"),
    re_path(r'^confirm-email/(?P<key>[-:\w]+)/$', ConfirmEmailView.as_view(), name="confirm_email"),
    
    # change password
    url(r'^password-change/$', views.AllAuthPasswordChangeView.as_view(), name="password_change"),

    # login user from session
    url(r'^api/login-user/(?P<username>[-\w]+)/$', views.login_user_view, name="login_user"),

    # create user new user
    url(r'^api/create-new-user/$', views.create_new_user_view, name="create_new_user"),

]
