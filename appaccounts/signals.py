from django.conf import settings
from django.db.models.signals import post_save
from allauth.account.signals import password_set, password_changed, password_reset
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Profile


def set_profile_need_password(request, profile, need_password):
    profile.need_password = need_password
    profile.save()
    request.session[settings.SESSION_AUTO_LOGIN_KEY] = '0'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        instance.last_login = timezone.now()
        instance.save()


@receiver(password_set, sender=User)
def password_set_signal(request, user, **kwargs):
    set_profile_need_password(request, request.user.profile, True)


@receiver(password_changed, sender=User)
def password_changed_signal(request, user, **kwargs):
    set_profile_need_password(request, request.user.profile, True)


@receiver(password_reset, sender=User)
def password_reset_signal(request, user, **kwargs):
    set_profile_need_password(request, request.user.profile, True)
