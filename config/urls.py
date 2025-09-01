# config/urls.py

from django.contrib import admin
from django.urls import path, include
from quiz import views as quiz_views

from django.conf import settings
from django.conf.urls.static import static

# THÊM DÒNG NÀY VÀO ĐẦU FILE
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', quiz_views.landing_page, name='landing_page'),
    path('dashboard/', quiz_views.dashboard, name='dashboard'),
    path('quiz/', include('quiz.urls', namespace='quiz')),
]

if settings.DEBUG:
    # Bây giờ, 'os' đã được định nghĩa và dòng này sẽ không báo lỗi nữa
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'static'))