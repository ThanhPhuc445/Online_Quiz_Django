from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    # URLs cho luồng thi chính thức của học sinh
    path('take/<int:pk>/', views.take_quiz, name='take_quiz'),
    path('submit/<int:pk>/', views.submit_quiz, name='submit_quiz'),
    path('results/<int:pk>/', views.view_result, name='view_result'),
    path('history/', views.test_history, name='test_history'),

    # URLs cho chế độ Luyện tập của học sinh
    path('practice/', views.practice_mode_selection, name='practice_selection'),
    path('practice/start/<int:subject_id>/', views.start_practice, name='start_practice'),
    path('practice/submit/', views.submit_practice, name='submit_practice'),
]