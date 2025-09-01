# config/urls.py

from django.contrib import admin
from django.urls import path, include
from quiz import views as quiz_views # Dòng này vẫn giữ nguyên

urlpatterns = [
    path('admin/', admin.site.urls),

    # URL cho app 'users' (Đăng ký) và của Django (Đăng nhập, Đăng xuất,...)
    path('accounts/', include('users.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    # URL trang chủ, vẫn trỏ đến view 'home' trong app 'quiz'
    path('', quiz_views.home, name='home'),
    
    # ===== DÒNG QUAN TRỌNG CẦN THÊM VÀO =====
    # Dòng này sẽ kết nối TẤT CẢ các URL khác trong file quiz/urls.py
    # và gán cho chúng namespace là 'quiz'.
    # Ví dụ: /quiz/history/, /quiz/take/1/, /quiz/practice/
    path('quiz/', include('quiz.urls', namespace='quiz')),
]