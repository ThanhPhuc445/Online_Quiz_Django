from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    # URLs chung
    path('', views.landing_page, name='landing_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # URLs của Giáo viên
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    
    # Quản lý câu hỏi
    path('teacher/questions/', views.question_list, name='question_list'),
    path('teacher/questions/add/', views.question_create, name='question_create'),
    path('teacher/questions/<int:pk>/edit/', views.question_edit, name='question_edit'),
    path('teacher/questions/<int:pk>/delete/', views.question_delete, name='question_delete'),
    path('teacher/questions/import/', views.question_import_excel, name='question_import'),

    # Quản lý đề thi
    path('teacher/quizzes/', views.quiz_list, name='quiz_list'),
    path('teacher/quizzes/add/', views.quiz_create, name='quiz_create'),
    path('teacher/quizzes/<int:pk>/edit/', views.quiz_edit, name='quiz_edit'),
    path('teacher/quizzes/<int:pk>/delete/', views.quiz_delete, name='quiz_delete'),
    path('teacher/quizzes/<int:pk>/results/', views.quiz_results, name='quiz_results'),

    # API
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
    
    # URLs LUYỆN TẬP
    path('practice/', views.practice_selection, name='practice_selection'),
    path('practice/quiz/<int:pk>/', views.practice_quiz, name='practice_quiz'),
    path('practice/quiz/<int:pk>/submit/', views.submit_practice_quiz, name='submit_practice_quiz'),
    path('practice/history/', views.practice_history, name='practice_history'),
    path('practice/subject/<int:subject_id>/', views.practice_by_subject, name='practice_by_subject'),
    path('practice/random/', views.practice_random, name='practice_random'),

    # URLs settings
    path('settings/', views.settings_page, name='settings'),
    path('settings/update-profile/', views.update_profile, name='update_profile'),
    path('settings/change-password/', views.change_password, name='change_password'),

    # URLs hỗ trợ
    path('support/', views.support_dashboard, name='support_dashboard'),
    path('support/contact-teacher/', views.contact_teacher, name='contact_teacher'),
    path('support/contact-teacher/<int:teacher_id>/', views.contact_teacher, name='contact_teacher_with_id'),
    path('support/contact-teacher/quiz/<int:quiz_id>/', views.contact_teacher, name='contact_teacher_quiz'),
    path('support/contact-admin/', views.contact_admin, name='contact_admin'),
    path('support/ticket/<int:ticket_id>/', views.support_ticket_detail, name='support_ticket_detail'),
    path('support/my-tickets/', views.my_support_tickets, name='my_support_tickets'),
    path('support/teacher-inbox/', views.teacher_support_inbox, name='teacher_support_inbox'),
    path('support/admin-dashboard/', views.admin_support_dashboard, name='admin_support_dashboard'),
]