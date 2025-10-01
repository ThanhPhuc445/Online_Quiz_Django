from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/quizzes/', views.quiz_list, name='quiz_list'),
    path('teacher/quizzes/create/', views.create_quiz, name='quiz_create'),
    path('teacher/quizzes/<int:pk>/edit/', views.edit_quiz, name='quiz_edit'),
    path('teacher/quizzes/<int:pk>/delete/', views.delete_quiz, name='quiz_delete'),

    path('teacher/questions/', views.question_list, name='question_list'),
    path('teacher/questions/create/', views.create_question, name='create_question'),
    path('teacher/questions/<int:pk>/edit/', views.edit_question, name='edit_question'),
    path('teacher/questions/<int:pk>/delete/', views.delete_question, name='delete_question'),

    path('teacher/quizzes/<int:pk>/results/', views.quiz_results, name='quiz_results'),
    path('teacher/questions/import/', views.import_questions_excel, name='import_questions'),
    # URLs cho luồng thi chính thức của học sinh
    path('take/<int:pk>/', views.take_quiz, name='take_quiz'),
    path('submit/<int:pk>/', views.submit_quiz, name='submit_quiz'),
    path('results/<int:pk>/', views.view_result, name='view_result'),
    path('history/', views.test_history, name='test_history'),

    # URLs cho chế độ Luyện tập của học sinh
    path('practice/', views.practice_mode_selection, name='practice_selection'),
    path('practice/start/<int:subject_id>/', views.start_practice, name='start_practice'),
    path('practice/submit/', views.submit_practice, name='submit_practice'),
    path('join-with-code/', views.join_with_code, name='join_with_code'),
]