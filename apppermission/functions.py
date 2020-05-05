from django.conf import settings
from .models import AccessType


def user_is_manager(user):
    if not user:
        return False
    elif not user.is_authenticated:
        return False
    elif user.is_superuser or user.groups.filter(name=settings.GROUP_MANAGER).exists():
        return True


def check_object_permission(user, object, action_type=None):
    result = False
    if not user or not user.is_authenticated:
        result = False
    elif user.is_superuser:
        result = True
    else:
        access_type = None
        if action_type == 'public':
            if object.active:
                access_type = AccessType.REMOVE_PUBLIC
            else:
                access_type = AccessType.SET_PUBLIC
        else:
            if object.active:
                access_type = AccessType.EDIT_ACTIVE
            else:
                access_type = AccessType.EDIT_NON_ACTIVE
        if not access_type:
            result = False
        else:
            permissions = None
            model_name = object._meta.model_name
            if model_name == 'course':
                permissions = user.course_permissions.filter(course=object)
            if model_name == 'module':
                if object.active:
                    permissions = user.module_permissions.filter(module=object)
                else:
                    if action_type == 'public':
                        permissions = user.module_permissions.filter(module=object)
                    else:
                        access_type = AccessType.EDIT_NON_ACTIVE
                        permissions = user.module_permissions.filter(module=object)
                        if not permissions.filter(access_type__type__in=access_type).exists():
                            permissions = user.course_permissions.filter(course=object.course)
            if model_name == 'quiz' or model_name == 'question':
                object_filter = object
                if model_name == 'question':
                    object_filter = object.quiz
                if object.active:
                    permissions = user.quiz_permissions.filter(quiz=object_filter)
                else:
                    if action_type == 'public':
                        permissions = user.quiz_permissions.filter(quiz=object_filter)
                    else:
                        access_type = AccessType.EDIT_NON_ACTIVE
                        permissions = user.quiz_permissions.filter(quiz=object_filter)
            if model_name == 'lesson' or model_name == 'content':
                if object.active:
                    permissions = user.lesson_permissions.filter(lesson=object)
                else:
                    if action_type == 'public':
                        permissions = user.lesson_permissions.filter(lesson=object)
                    else:
                        access_type = AccessType.EDIT_NON_ACTIVE
                        permissions = user.lesson_permissions.filter(lesson=object)
                        if not permissions.filter(access_type__type__in=access_type).exists():
                            permissions = user.module_permissions.filter(module=object.module)
                            if not permissions.filter(access_type__type__in=access_type).exists():
                                permissions = user.course_permissions.filter(course=object.module.course)
            if permissions:
                result = permissions.filter(access_type__type__in=access_type).exists()
            else:
                result = False
    return result
