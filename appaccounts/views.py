from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic.base import ContextMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from allauth.account.views import EmailView, PasswordChangeView, LoginView

from apporders.functions import get_order_list
from appcourses.functions import get_user_power

from .functions import login_user, get_user_from_session
from .forms import ProfileEditForm, AllAuthAddEmailForm, AllAuthChangePasswordForm
from .models import Profile


class BaseContextData(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super(BaseContextData, self).get_context_data(**kwargs)
        context['base_css_path'] = settings.BASE_CSS_COURSE_PATH
        context['base_js_path'] = settings.BASE_JS_COURSE_PATH
        power = get_user_power(self.request.user)
        if not power:
            power = _('в начале пути')
        context['power'] = power

        return context


class ProfileDetail(DetailView):
    model = Profile
    template_name = 'appaccounts/profile-detail.html'
    
    def get_context_data(self, **kwargs):
        context = super(ProfileDetail, self).get_context_data(**kwargs)
        
        # lis of user's orders
        kwargs = {
            'filter_user': '==',
            'user': self.object.user,
            'add_skill_data': True,
            'add_fl_count': True,
        }
        context['orders'] = get_order_list(**kwargs)
        if self.request.user.is_authenticated:
            context['its_me'] = self.object == self.request.user.profile

        import json
        user_data = self.object.get_user_skills_data(user=self.object.user)
        context['user_skills_data'] = json.dumps(user_data['skills_data'])
        context['user_total_rate'] = user_data['total_rate_display']
        context['user_total_task_count'] = len(context['orders'])
        
        return context


class AllAuthEmailView(LoginRequiredMixin, BaseContextData, EmailView):

    template_name = "appaccounts/email.html"
    form_class = AllAuthAddEmailForm
    success_url = reverse_lazy('appaccounts:account_email')

    def get_context_data(self, **kwargs):
        
        context = super(AllAuthEmailView, self).get_context_data(**kwargs)

        context['profile'] = self.request.user.profile
        context['profile_chapter'] = 2
        context['post_url'] = reverse_lazy('appaccounts:account_email')
        context['form_file'] = False
        
        return context


class AllAuthPasswordChangeView(LoginRequiredMixin, BaseContextData, PasswordChangeView):

    template_name = "appaccounts/password_change.html"
    form_class = AllAuthChangePasswordForm
    success_url = reverse_lazy('appaccounts:password_change')

    def get_context_data(self, **kwargs):
        
        context = super(AllAuthPasswordChangeView, self).get_context_data(**kwargs)

        context['profile'] = self.request.user.profile
        context['profile_chapter'] = 3
        context['post_url'] = reverse_lazy('appaccounts:password_change')
        context['form_file'] = False
        
        return context


class ProfileUpdate(LoginRequiredMixin, BaseContextData, UpdateView):
    model = Profile
    form_class = ProfileEditForm
    template_name = 'appaccounts/profile-edit.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileUpdate, self).get_context_data(**kwargs)

        context['profile'] = self.request.user.profile
        context['login'] = self.request.user.username
        context['first_name'] = self.request.user.first_name
        context['profile_chapter'] = 1
        context['post_url'] = reverse_lazy('appaccounts:profile_edit')
        context['form_file'] = True
        context['avatar_list'] = Profile.get_avatar_list()

        return context

    def get_object(self, queryset=None):
        return Profile.objects.filter(id=self.request.user.profile.id).first()

    def form_valid(self, form):

        first_name = self.request.POST.get('first_name', '')
        if first_name:
            self.request.user.first_name = first_name
        username = form.cleaned_data['username']
        if username:
            self.request.user.username = username
        self.request.user.save()
        self.request.session[settings.SESSION_USERNAME_KEY] = username

        return super(ProfileUpdate, self).form_valid(form)


class CustomLogoutView(LogoutView):
    
    def dispatch(self, request, *args, **kwargs):
        username = request.user.username
        dis = super(CustomLogoutView, self).dispatch(request, *args, **kwargs)
        request.session[settings.SESSION_USERNAME_KEY] = username
        request.session[settings.SESSION_AUTO_LOGIN_KEY] = '0'
        return dis


class CustomLoginView(LoginView):

    def dispatch(self, request, *args, **kwargs):
        username = request.session.get(settings.SESSION_USERNAME_KEY, '')
        if username:
            user_qs = User.objects.filter(username=username)
            if user_qs:
                user = user_qs.get()
                if user and user.profile and not user.profile.need_password:
                    login(request, user, 'django.contrib.auth.backends.ModelBackend')
        return super(LoginView, self).dispatch(request, *args, **kwargs)


@require_POST
def login_user_view(request, username):
    if not request.user.is_authenticated:
        user_qs = User.objects.filter(username=username)
        if user_qs.exists():
            login_user(request, user_qs.get())
            return redirect('appmain:dashboard')
    return redirect('appaccounts:login')


@require_POST
def create_new_user_view(request):
    if not request.user.is_authenticated:
        new_user = get_user_from_session(request)
        if new_user:
            login_user(request, new_user)
            return redirect('appmain:dashboard')
    return redirect('appaccounts:login')
