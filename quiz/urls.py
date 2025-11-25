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

    path('api/question/quick-create/', views.api_quick_create_question, name='api_quick_create_question'),
    
    # URLs chấm điểm tự luận
    path('grading/dashboard/', views.grading_dashboard, name='grading_dashboard'),
    path('grading/grade/<int:result_id>/', views.grade_short_answer, name='grade_short_answer'),
    
    # URLs của Học sinh - Thi thật
    path('take/<int:pk>/', views.take_quiz, name='take_quiz'),
    path('submit/<int:pk>/', views.submit_quiz, name='submit_quiz'),
    path('results/<int:pk>/', views.view_result, name='view_result'),
    path('history/', views.test_history, name='test_history'),
    path('join/', views.join_with_code, name='join_with_code'),
    
    # URLs LUYỆN TẬP - ĐẦY ĐỦ
    path('practice/', views.practice_selection, name='practice_selection'),
    path('practice/quiz/<int:pk>/', views.practice_quiz, name='practice_quiz'),
    path('practice/quiz/<int:pk>/submit/', views.submit_practice_quiz, name='submit_practice_quiz'),
    path('practice/history/', views.practice_history, name='practice_history'),
    path('practice/subject/<int:subject_id>/', views.practice_by_subject, name='practice_by_subject'),
    path('practice/random/', views.practice_random, name='practice_random'),
]