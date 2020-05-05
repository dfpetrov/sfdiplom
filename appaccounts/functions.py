from django.contrib.auth import login
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST


def get_profile_description(user, fields=None):
    general_description = {
        'profile_id': '',
        'profile_name': '',
        'profile_description': '',
        'profile_avatar': '',
        'profile_url': '',
        'profile_created': '',
    }

    if user and user.profile:
        profile = user.profile
        general_description['profile_id'] = profile.id
        general_description['profile_name'] = user.username
        general_description[
            'profile_description'] = profile.description if profile.description else 'Пользователь пока ничего не написал о себе'
        general_description['profile_avatar'] = profile.avatar.url if profile.avatar else ''
        general_description['profile_url'] = profile.get_absolute_url()
        general_description['profile_created'] = profile.created

    if fields:
        description = {}
        for field in fields:
            description[field] = general_description[field]
        return description
    else:
        return general_description


def get_user_from_session(request, create=True):
    session_user = None
    if request.user.is_authenticated:
        return request.user
    else:
        session_user_name = request.session.get(settings.SESSION_USERNAME_KEY, '')
        if session_user_name:
            user_qs = User.objects.filter(username=session_user_name)
            if user_qs:
                session_user = user_qs.get()
        if not session_user and create:
            session_user = create_user(request)
            request.session[settings.SESSION_USERNAME_KEY] = session_user.username
            request.session[settings.SESSION_AUTO_LOGIN_KEY] = '1'

    return session_user


@require_POST
def login_user(request, user):
    if not request.user.is_authenticated and user.profile and not user.profile.need_password:
        login(request, user, 'allauth.account.auth_backends.AuthenticationBackend')
        request.session[settings.SESSION_USERNAME_KEY] = user.username
    return user


@require_POST
def create_user(request):
    new_user = None
    if request:
        random_username = User.objects.make_random_password(20)
        while User.objects.filter(username=random_username).exists():
            if len(random_username < 100):
                random_username += '1'
        new_user = User()
        new_user.username = random_username
        new_user.first_name = _('Гость')
        new_user.set_password(User.objects.make_random_password())
        new_user.save()
        new_user.username = f'guest{new_user.id}'
        new_user.save()
    return new_user
