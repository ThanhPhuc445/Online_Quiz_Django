# quiz/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.contrib import messages
import random

from .models import Quiz, Answer, Subject, Question
from results.models import Result, StudentAnswer
from users.decorators import student_required, teacher_required

# ===========================================================================
# VIEW MỚI CHO TRANG CHỦ CÔNG KHAI
# ===========================================================================
def landing_page(request):
    """View cho trang chủ công khai, ai cũng có thể xem được."""
    return render(request, 'pages/landing_page.html')


# ===========================================================================
# VIEW PHÂN LUỒNG (ĐỔI TÊN TỪ home THÀNH dashboard)
# ===========================================================================
@login_required
def dashboard(request): # Đã đổi tên từ 'home'
    user = request.user
    if user.role == 'TEACHER':
        return render(request, 'pages/teacher_dashboard.html')
    elif user.role == 'STUDENT':
        now = timezone.now()
        quizzes = Quiz.objects.filter(start_time__lte=now, end_time__gte=now)
        taken_quiz_ids = Result.objects.filter(student=user).values_list('quiz__id', flat=True)
        context = {
            'quizzes': quizzes,
            'taken_quiz_ids': list(taken_quiz_ids), 
        }
        return render(request, 'pages/student_dashboard.html', context)
    else: # Admin
        return render(request, 'pages/admin_dashboard.html')

# ===========================================================================
# CÁC VIEW CỦA HỌC SINH (GIỮ NGUYÊN)
# ===========================================================================

@login_required
@student_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    now = timezone.now()
    if Result.objects.filter(student=request.user, quiz=quiz).exists():
        messages.warning(request, "Bạn đã hoàn thành bài thi này rồi.")
        return redirect('dashboard') # Chuyển hướng về dashboard
    if now > quiz.end_time:
        messages.error(request, "Bài thi này đã kết thúc.")
        return redirect('dashboard') # Chuyển hướng về dashboard
    if now < quiz.start_time:
        messages.info(request, "Bài thi này chưa đến giờ bắt đầu.")
        return redirect('dashboard') # Chuyển hướng về dashboard

    questions = list(quiz.questions.all())
    random.shuffle(questions)
    shuffled_questions = [{'question': q, 'answers': list(q.answers.all())} for q in questions]
    for item in shuffled_questions:
        random.shuffle(item['answers'])

    context = {'quiz': quiz, 'shuffled_questions': shuffled_questions}
    return render(request, 'quiz_taking/take_quiz.html', context)

@login_required
@student_required
@transaction.atomic
def submit_quiz(request, pk):
    if request.method != 'POST':
        raise PermissionDenied

    quiz = get_object_or_404(Quiz, pk=pk)
    if timezone.now() > quiz.end_time:
        messages.error(request, "Đã hết thời gian làm bài, không thể nộp.")
        return redirect('dashboard') # Chuyển hướng về dashboard
    if Result.objects.filter(student=request.user, quiz=quiz).exists():
        messages.warning(request, "Bạn đã nộp bài thi này rồi.")
        return redirect('dashboard') # Chuyển hướng về dashboard

    questions = quiz.questions.all()
    correct_answers_count = 0
    total_questions = questions.count()
    result = Result.objects.create(student=request.user, quiz=quiz, score=0)
    for question in questions:
        selected_answer_id = request.POST.get(f'question_{question.id}')
        if selected_answer_id:
            try:
                selected_answer = Answer.objects.get(pk=selected_answer_id)
                StudentAnswer.objects.create(result=result, question=question, selected_answer=selected_answer)
                if selected_answer.is_correct:
                    correct_answers_count += 1
            except Answer.DoesNotExist:
                pass
    score = (correct_answers_count / total_questions) * 100 if total_questions > 0 else 0
    result.score = round(score, 2)
    result.save()
    return redirect('quiz:view_result', pk=result.pk)


# (Các view còn lại: view_result, test_history, practice... giữ nguyên như cũ, chỉ sửa các redirect về 'dashboard')

@login_required
@student_required
def view_result(request, pk):
    result = get_object_or_404(Result, pk=pk, student=request.user)
    detailed_answers = []
    student_answers_dict = {sa.question.id: sa.selected_answer for sa in result.student_answers.all()}
    for question in result.quiz.questions.order_by('id'):
        correct_answer = question.answers.get(is_correct=True)
        student_answer = student_answers_dict.get(question.id)
        detailed_answers.append({
            'question_text': question.text, 'all_answers': question.answers.all(),
            'correct_answer_id': correct_answer.id, 'student_answer_id': student_answer.id if student_answer else None,
        })
    context = {'result': result, 'detailed_answers': detailed_answers}
    return render(request, 'quiz_taking/view_result.html', context)

@login_required
@student_required
def test_history(request):
    results = Result.objects.filter(student=request.user).order_by('-completed_at')
    context = {'results': results}
    return render(request, 'quiz_taking/test_history.html', context)

@login_required
@student_required
def practice_mode_selection(request):
    subjects = Subject.objects.all()
    context = {'subjects': subjects}
    return render(request, 'practice_mode/practice_selection.html', context)

@login_required
@student_required
def start_practice(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    questions = list(subject.questions.order_by('?')[:10])
    if not questions:
        messages.info(request, f"Hiện chưa có câu hỏi nào cho môn {subject.name}.")
        return redirect('quiz:practice_selection')
    shuffled_questions = [{'question': q, 'answers': list(q.answers.all())} for q in questions]
    for item in shuffled_questions:
        random.shuffle(item['answers'])
    context = {'subject': subject, 'shuffled_questions': shuffled_questions}
    return render(request, 'practice_mode/practice_session.html', context)

@login_required
@student_required
def submit_practice(request):
    if request.method != 'POST':
        return redirect('quiz:practice_selection')
    question_ids = request.POST.getlist('question_id')
    questions = Question.objects.filter(id__in=question_ids).prefetch_related('answers')
    results_data = []
    correct_count = 0
    for question in questions:
        selected_answer_id = request.POST.get(f'question_{question.id}')
        correct_answer = question.answers.get(is_correct=True)
        is_student_correct = (str(correct_answer.id) == selected_answer_id)
        if is_student_correct:
            correct_count += 1
        results_data.append({
            'question': question, 'all_answers': question.answers.all(),
            'selected_answer_id': int(selected_answer_id) if selected_answer_id else None,
            'correct_answer_id': correct_answer.id, 'is_correct': is_student_correct,
        })
    total_questions = len(question_ids)
    score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
    context = {
        'results_data': results_data, 'correct_count': correct_count,
        'total_questions': total_questions, 'score': round(score, 2),
    }
    return render(request, 'practice_mode/practice_result.html', context)