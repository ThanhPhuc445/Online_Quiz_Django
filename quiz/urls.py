# quiz/urls.py
from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    # URLs của Giáo viên
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    
    path('teacher/questions/', views.question_list, name='question_list'),
    path('teacher/questions/add/', views.question_create, name='question_create'),
    path('teacher/questions/<int:pk>/edit/', views.question_edit, name='question_edit'),
    path('teacher/questions/<int:pk>/delete/', views.question_delete, name='question_delete'),
    path('teacher/questions/import/', views.question_import_excel, name='question_import'),

    path('teacher/quizzes/', views.quiz_list, name='quiz_list'),
    path('teacher/quizzes/add/', views.quiz_create, name='quiz_create'),
    path('teacher/quizzes/<int:pk>/edit/', views.quiz_edit, name='quiz_edit'),
    path('teacher/quizzes/<int:pk>/delete/', views.quiz_delete, name='quiz_delete'),
    path('teacher/quizzes/<int:pk>/results/', views.quiz_results, name='quiz_results'),
    
    # URLs của Học sinh
    path('take/<int:pk>/', views.take_quiz, name='take_quiz'),
    path('submit/<int:pk>/', views.submit_quiz, name='submit_quiz'),
    path('results/<int:pk>/', views.view_result, name='view_result'),
    path('history/', views.test_history, name='test_history'),
    path('join/', views.join_with_code, name='join_with_code'),
    
    path('practice/', views.practice_mode_selection, name='practice_selection'),
    path('practice/start/<int:subject_id>/', views.start_practice, name='start_practice'),
    path('practice/submit/', views.submit_practice, name='submit_practice'),
]