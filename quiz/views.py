from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Đây là view trang chủ, yêu cầu người dùng phải đăng nhập
@login_required
def home(request):
    user = request.user
    # Kiểm tra vai trò và render template tương ứng
    if user.role == 'TEACHER':
        return render(request, 'pages/teacher_dashboard.html')
    elif user.role == 'STUDENT':
        return render(request, 'pages/student_dashboard.html')
    # Admin hoặc các vai trò khác có thể xem một trang chung
    # Hoặc bạn có thể redirect admin tới '/admin'
    else:
        return render(request, 'pages/admin_dashboard.html')