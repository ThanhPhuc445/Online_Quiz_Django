from django.contrib import admin
from django.urls import path, include
from quiz import views as quiz_views # Import view từ app quiz

urlpatterns = [
    path('admin/', admin.site.urls),

    # URL cho app 'users' (Đăng ký) và của Django (Đăng nhập, Đăng xuất,...)
    path('accounts/', include('users.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    # URL trang chủ, sẽ gọi đến view 'home' trong app 'quiz'
    # Chúng ta sẽ tạo view này ngay sau đây
    path('', quiz_views.home, name='home'),
]