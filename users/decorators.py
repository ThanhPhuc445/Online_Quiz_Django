# users/decorators.py

from django.core.exceptions import PermissionDenied

def student_required(function):
    """
    Decorator để kiểm tra xem người dùng có phải là học sinh không.
    Nếu không, sẽ trả về lỗi 403 Forbidden.
    """
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'STUDENT':
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap

def teacher_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'TEACHER':
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap