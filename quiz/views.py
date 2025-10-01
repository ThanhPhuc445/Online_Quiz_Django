# quiz/views.py
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.contrib import messages
import random

from quiz.forms import AnswerForm, AnswerFormSet, QuestionForm,QuizForm

from .models import Quiz, Answer, Subject, Question
from results.models import Result, StudentAnswer
from users.decorators import student_required, teacher_required
from openpyxl import load_workbook

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

@login_required
@teacher_required
def teacher_dashboard(request):
    teacher = request.user
    total_questions = Question.objects.filter(created_by=teacher).count()
    total_quizzes = Quiz.objects.filter(created_by=teacher).count()
    recent_quizzes = Quiz.objects.filter(created_by=teacher).order_by('created_at')[:5]
    total_attempts = Result.objects.filter(quiz__created_by=teacher).count()
    context = {'total_quizzes': total_quizzes, 'total_questions': total_questions, 'recent_quizzes': recent_quizzes, 'total_attempts': total_attempts}
    return render(request, 'pages/teacher_dashboard.html', context)

@login_required
@teacher_required
def quiz_list(request):
    quizzes = Quiz.objects.filter(created_by=request.user)
    return render(request, 'quiz_taking/quiz_list.html', {'quizzes': quizzes})

@login_required
@teacher_required
def create_quiz(request):
    if request.method == "POST":
        form = QuizForm(request.POST, user=request.user)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = request.user
            quiz.save()
            form.save_m2m()
            messages.success(request, "Quiz created.")
            return redirect('quiz:quiz_list')
    else:
        form = QuizForm(user=request.user)
    context = {
        'form': form
    }
    return render(request, 'quiz_taking/create_quiz.html', context)


@login_required
@teacher_required
def edit_quiz(request, pk):
    quiz_instance = get_object_or_404(Quiz, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz_instance, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đề thi đã được cập nhật thành công!')
            return redirect('quiz:quiz_list')
    else:
        form = QuizForm(instance=quiz_instance, user=request.user)
        context = {
        'form': form,
        'quiz': quiz_instance 
    }
        return render(request, 'quiz_taking/create_quiz.html', context)
def delete_quiz(request, pk):
    quiz_instance = get_object_or_404(Quiz, pk=pk, created_by=request.user)
    if request.method == 'POST':
        quiz_instance.delete()
        messages.success(request, 'Đề thi đã được xóa thành công!')
        return redirect('quiz:quiz_list')
    
    context = {
        'quiz': quiz_instance
    }
    return render(request, 'quiz_taking/quiz_confirm_delete.html', context)

@login_required
def question_list(request):
    current_teacher = request.user
    questions_list = Question.objects.filter(created_by=current_teacher)
    subject_id = request.GET.get('subject')
    difficulty_level = request.GET.get('difficulty')
    if subject_id:
        questions_list = questions_list.filter(subject_id=subject_id)
    if difficulty_level:
        questions_list = questions_list.filter(difficulty=difficulty_level)
    paginator = Paginator(questions_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    subjects = Subject.objects.all()
    difficulty_choices = Question.Difficulty.choices
    context = {
        'questions': page_obj,
        'subjects': subjects,
        'difficulty_choices': difficulty_choices,
        'selected_subject': int(subject_id) if subject_id else None,
        'selected_difficulty': difficulty_level,
    }
    return render(request, 'quiz_taking/question_list.html', context)

@login_required
@teacher_required
def create_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.created_by = request.user
            q.save()
            formset = AnswerFormSet(request.POST, instance=q)
            if formset.is_valid():
                formset.save()
                return redirect('quiz:question_list')
    else:
        form = QuestionForm()
        formset = AnswerFormSet()
    return render(request, 'quiz_taking/question_form.html', {'form': form, 'formset': formset})

@login_required
@teacher_required
def edit_question(request, pk):
    question_instance = get_object_or_404(Question, pk=pk, created_by=request.user)
    if request.method == 'POST':
        question_form = QuestionForm(request.POST, instance=question_instance)
        answer_formset = AnswerFormSet(request.POST, instance=question_instance)

        if question_form.is_valid() and answer_formset.is_valid():
            question_form.save()
            answer_formset.save()
            messages.success(request, 'Câu hỏi đã được cập nhật thành công!')
            return redirect('quiz:question_list')
    else:
        question_form = QuestionForm(instance=question_instance)
        answer_formset = AnswerFormSet(instance=question_instance)

        context = {
        'form': question_form,
        'formset': answer_formset,
        'question': question_instance
    }
    return render(request, 'quiz_taking/question_form.html', context)

@login_required
@teacher_required
def delete_question(request, pk):
    question_instance = get_object_or_404(Question, pk=pk, created_by=request.user)
    if request.method == 'POST':
        question_instance.delete()
        messages.success(request, 'Câu hỏi đã được xóa thành công!')
        return redirect('quiz:question_list')
    context = {
        'question': question_instance
    }
    return render(request, 'quiz_taking/question_confirm_delete.html', context)

@login_required
@teacher_required
def quiz_results(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, created_by=request.user)
    results = Result.objects.filter(quiz=quiz).order_by('-score')
    context = {
        'quiz': quiz,
        'results': results
    }
    return render(request, 'pages/teacher_quiz_results.html', context)

@login_required
@teacher_required
def import_questions_excel(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file', None)

        if not excel_file:
            messages.error(request, "Vui lòng chọn một file để upload.")
            return redirect('quiz:import_questions')

        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, "File không hợp lệ. Hệ thống chỉ chấp nhận file .xlsx.")
            return redirect('quiz:import_questions')

        try:
            workbook = load_workbook(filename=excel_file, data_only=True)
            sheet = workbook.active
            questions_created_count = 0

            for row in sheet.iter_rows(min_row=2, values_only=True):
                if len(row) < 8 or not row[1]:
                    continue
                
                subject_name, question_text, difficulty, *options, correct_idx = row[:8]
                subject_name = row[0]
                difficulty = row[1]
                question_text = row[2]
                options = row[3:7]
                subject, _ = Subject.objects.get_or_create(name=str(subject_name).strip())
                
                difficulty_processed = (str(difficulty).strip().upper() or 'MEDIUM')
                valid_difficulties = [choice[0] for choice in Question.Difficulty.choices]
                if difficulty_processed not in valid_difficulties:
                    continue

                try:
                    correct_answer_index = int(correct_idx)
                    if not (1 <= correct_answer_index <= 4):
                        continue
                except (ValueError, TypeError):
                    continue
                
                question = Question.objects.create(
                    subject=subject,
                    text=str(question_text).strip(),
                    difficulty=difficulty_processed,
                    created_by=request.user
                )

                for index, option_text in enumerate(options, start=1):
                    if option_text:
                        is_correct = (index == correct_answer_index)
                        Answer.objects.create(
                            question=question,
                            text=str(option_text).strip(),
                            is_correct=is_correct
                        )
                
                questions_created_count += 1

            messages.success(request, f'Đã import thành công {questions_created_count} câu hỏi.')
            return redirect('quiz:question_list')

        except Exception as e:
            messages.error(request, f"Đã có lỗi xảy ra: {e}")
            return redirect('quiz:import_questions')

    return render(request, 'quiz_taking/import_questions.html')
        

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
# quiz/views.py

@login_required
@student_required
def join_with_code(request):
    if request.method == 'POST':
        code = request.POST.get('access_code', '').strip().upper()
        if not code:
            messages.error(request, "Vui lòng nhập mã tham gia.")
            return redirect('quiz:student_dashboard')

        try:
            # Tìm đề thi có mã code tương ứng
            quiz_to_join = Quiz.objects.get(access_code=code)
            
            # Thêm học sinh hiện tại vào danh sách allowed_students
            quiz_to_join.allowed_students.add(request.user)
            
            messages.success(request, f"Bạn đã tham gia thành công vào đề thi '{quiz_to_join.title}'.")

        except Quiz.DoesNotExist:
            messages.error(request, "Mã tham gia không hợp lệ hoặc không tồn tại.")

    return redirect('quiz:student_dashboard')