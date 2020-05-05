from django.contrib.auth.decorators import wraps
from django.core.exceptions import PermissionDenied

from apppermission.functions import check_object_permission


def check_user_group_for_view(group_name):
    def _check_group(view_func):
        @wraps(view_func)
        def wrapper(view, request, *args, **kwargs):
            result = True
            if not request or not request.user or not request.user.is_authenticated:
                result = False
            elif request.user.is_superuser:
                result = True
            elif not request.user.groups.filter(name=group_name).exists():
                result = False
            if result:
                return view_func(view, request, *args, **kwargs)
            else:
                raise PermissionDenied()

        return wrapper

    return _check_group


def object_permission_required(action_type=None):
    def check_permission(view_func):
        @wraps(view_func)
        def wrapper(view, request, *args, **kwargs):
            result = check_object_permission(request.user, view.get_object(), action_type)
            if result:
                return view_func(view, request, *args, **kwargs)
            else:
                raise PermissionDenied()

        return wrapper

    return check_permission
