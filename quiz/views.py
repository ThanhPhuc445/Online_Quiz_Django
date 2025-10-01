# quiz/views.py

# ===== CÁC THƯ VIỆN CẦN THIẾT =====
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator
from django.contrib import messages
import random
from openpyxl import load_workbook
from django.db.models import Count, Q
from .models import Question, Quiz, Answer, Subject

# ===== IMPORT TỪ CÁC FILE KHÁC TRONG DỰ ÁN CỦA BẠN =====
from .forms import QuestionForm, AnswerFormSet, QuizForm
from .models import Quiz, Answer, Subject, Question
from results.models import Result, StudentAnswer
from users.decorators import student_required, teacher_required


# ===========================================================================
# VIEWS CHUNG & PHÂN LUỒNG
# ===========================================================================

def landing_page(request):
    """View cho trang chủ công khai, ai cũng có thể xem được."""
    return render(request, 'pages/landing_page.html')


@login_required
def dashboard(request):
    user = request.user
    if user.role == 'TEACHER':
        return redirect('quiz:teacher_dashboard')
    
    elif user.role == 'STUDENT':
        now = timezone.now()
        # Lấy các đề thi công khai, đang diễn ra
        public_quizzes = Quiz.objects.filter(is_public=True, start_time__lte=now, end_time__gte=now)
        # Lấy các đề thi riêng tư mà học sinh đã được phép tham gia
        private_quizzes_joined = user.allowed_quizzes.filter(is_public=False, start_time__lte=now, end_time__gte=now)
        
        all_quizzes = (public_quizzes | private_quizzes_joined).distinct()
        
        taken_quiz_ids = Result.objects.filter(student=user).values_list('quiz__id', flat=True)
        context = {'quizzes': all_quizzes, 'taken_quiz_ids': list(taken_quiz_ids)}
        return render(request, 'pages/student_dashboard.html', context)
    
    else: # Admin
        return render(request, 'pages/admin_dashboard.html')

# ===========================================================================
# VIEWS CHO GIÁO VIÊN
# ===========================================================================

@login_required
@teacher_required
def teacher_dashboard(request):
    teacher = request.user
    total_questions = Question.objects.filter(created_by=teacher).count()
    total_quizzes = Quiz.objects.filter(created_by=teacher).count()
    recent_quizzes = Quiz.objects.filter(created_by=teacher).order_by('-created_at')[:5]
    total_attempts = Result.objects.filter(quiz__created_by=teacher).count()

    student_answers = StudentAnswer.objects.filter(result__quiz__created_by=teacher)
    total_answers_submitted = student_answers.count()
    total_correct_answers = student_answers.filter(selected_answer__is_correct=True).count()
    
    average_correct_rate = 0
    if total_answers_submitted > 0:
        average_correct_rate = round((total_correct_answers / total_answers_submitted) * 100)

    context = {
        'total_quizzes': total_quizzes, 'total_questions': total_questions, 'recent_quizzes': recent_quizzes, 
        'total_attempts': total_attempts, 'average_correct_rate': average_correct_rate
    }
    return render(request, 'pages/teacher_dashboard.html', context)
# ===========================================================================


# --- Chức năng Quản lý Câu hỏi (Question CRUD) ---

@login_required
@teacher_required
def question_list(request):
    questions_qs = Question.objects.filter(created_by=request.user).order_by('-created_at')
    paginator = Paginator(questions_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'quiz_management/question_list.html', {'page_obj': page_obj})

@login_required
@teacher_required
def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.created_by = request.user
            formset = AnswerFormSet(request.POST, instance=question)
            if formset.is_valid():
                question.save()
                formset.save()
                messages.success(request, "Thêm câu hỏi thành công!")
                return redirect('quiz:question_list')
    else:
        form = QuestionForm()
        formset = AnswerFormSet()
    return render(request, 'quiz_management/question_form.html', {'form': form, 'formset': formset, 'is_edit': False})


@login_required
@teacher_required
@transaction.atomic  # <-- Rất khuyến khích có dòng này
def question_edit(request, pk):
    question = get_object_or_404(Question, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormSet(request.POST, instance=question)

        # Cả form và formset đều phải hợp lệ
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Cập nhật câu hỏi thành công!')
            return redirect('quiz:question_list')
        # Nếu không hợp lệ, code sẽ không redirect mà render lại form với các lỗi
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)
        
    context = {
        'form': form, 
        'formset': formset, 
        'is_edit': True
    }
    return render(request, 'quiz_management/question_form.html', context)

@login_required
@teacher_required
def question_delete(request, pk):
    question = get_object_or_404(Question, pk=pk, created_by=request.user)
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Xóa câu hỏi thành công!')
        return redirect('quiz:question_list')
    return render(request, 'quiz_management/question_confirm_delete.html', {'question': question})

@login_required
@teacher_required
def question_import_excel(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if not excel_file or not excel_file.name.endswith('.xlsx'):
            messages.error(request, "Vui lòng upload một file Excel (.xlsx).")
            return redirect('quiz:question_import')
        try:
            workbook = load_workbook(excel_file)
            sheet = workbook.active
            count = 0
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not all(row[i] for i in [0, 1, 2, 3, 4, 7]): continue
                subject_name, q_text, difficulty, ans1, ans2, ans3, ans4, correct_idx_str = row[:8]
                subject, _ = Subject.objects.get_or_create(name=str(subject_name).strip())
                difficulty_val = str(difficulty).strip().upper()
                if difficulty_val not in Question.Difficulty.values: continue
                
                question = Question.objects.create(subject=subject, text=str(q_text).strip(), difficulty=difficulty_val, created_by=request.user)
                answers = [ans1, ans2, ans3, ans4]
                correct_idx = int(correct_idx_str)
                for i, ans_text in enumerate(answers, 1):
                    if ans_text:
                        Answer.objects.create(question=question, text=str(ans_text).strip(), is_correct=(i == correct_idx))
                count += 1
            messages.success(request, f'Import thành công {count} câu hỏi.')
            return redirect('quiz:question_list')
        except Exception as e:
            messages.error(request, f"Lỗi xử lý file Excel: {e}")
            return redirect('quiz:question_import')
    return render(request, 'quiz_management/question_import.html')


# --- Chức năng Quản lý Đề thi (Quiz CRUD) ---

@login_required
@teacher_required
def quiz_list(request):
    quizzes = Quiz.objects.filter(created_by=request.user).order_by('-created_at')
    context = {
        'quizzes': quizzes,
        'now': timezone.now()  # <-- Đảm bảo dòng này tồn tại
    }
    return render(request, 'quiz_management/quiz_list.html', context)

@login_required
@teacher_required
def quiz_create(request):
    if request.method == "POST":
        form = QuizForm(request.POST, user=request.user)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = request.user
            quiz.save()
            form.save_m2m() # Quan trọng để lưu ManyToManyField
            messages.success(request, "Tạo đề thi thành công!")
            return redirect('quiz:quiz_list')
    else:
        form = QuizForm(user=request.user)
    return render(request, 'quiz_management/quiz_form.html', {'form': form, 'is_edit': False})


@login_required
@teacher_required
def quiz_edit(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật đề thi thành công!')
            return redirect('quiz:quiz_list')
    else:
        form = QuizForm(instance=quiz, user=request.user)
    return render(request, 'quiz_management/quiz_form.html', {'form': form, 'is_edit': True, 'quiz': quiz})


@login_required
@teacher_required
def quiz_delete(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, created_by=request.user)
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Xóa đề thi thành công!')
        return redirect('quiz:quiz_list')
    return render(request, 'quiz_management/quiz_confirm_delete.html', {'quiz': quiz})
    
@login_required
@teacher_required
def quiz_results(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, created_by=request.user)
    results = Result.objects.filter(quiz=quiz).order_by('-score')
    return render(request, 'quiz_management/quiz_results.html', {'quiz': quiz, 'results': results})

# ===========================================================================
# VIEWS CHO HỌC SINH
# ===========================================================================

@login_required
@student_required
def join_with_code(request):
    if request.method == 'POST':
        code = request.POST.get('access_code', '').strip().upper()
        if not code:
            messages.error(request, "Vui lòng nhập mã tham gia.")
            return redirect('dashboard')
        try:
            quiz = Quiz.objects.get(access_code=code)
            quiz.allowed_students.add(request.user)
            messages.success(request, f"Bạn đã tham gia thành công vào đề thi '{quiz.title}'.")
        except Quiz.DoesNotExist:
            messages.error(request, "Mã tham gia không hợp lệ hoặc không tồn tại.")
    return redirect('dashboard')


@login_required
@student_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    now = timezone.now()
    if not quiz.is_public and request.user not in quiz.allowed_students.all():
        messages.error(request, "Đây là kỳ thi riêng tư. Bạn cần nhập mã tham gia trước."); return redirect('dashboard')
    if Result.objects.filter(student=request.user, quiz=quiz).exists():
        result = Result.objects.get(student=request.user, quiz=quiz); return redirect('quiz:view_result', pk=result.pk)
    if now > quiz.end_time: messages.error(request, "Bài thi này đã kết thúc."); return redirect('dashboard')
    if now < quiz.start_time: messages.info(request, "Bài thi này chưa đến giờ bắt đầu."); return redirect('dashboard')
    questions = list(quiz.questions.all()); random.shuffle(questions)
    shuffled_questions = []
    for q in questions:
        answers = list(q.answers.all()); random.shuffle(answers)
        shuffled_questions.append({'question': q, 'answers': answers})
    context = {'quiz': quiz, 'shuffled_questions': shuffled_questions}
    return render(request, 'quiz_taking/take_quiz.html', context)


@login_required
@student_required
@transaction.atomic
def submit_quiz(request, pk):
    if request.method != 'POST': raise PermissionDenied
    quiz = get_object_or_404(Quiz, pk=pk)
    if timezone.now() > quiz.end_time: messages.error(request, "Đã hết thời gian làm bài, không thể nộp."); return redirect('dashboard')
    if Result.objects.filter(student=request.user, quiz=quiz).exists(): messages.warning(request, "Bạn đã nộp bài thi này rồi."); return redirect('dashboard')

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
                if selected_answer.is_correct: correct_answers_count += 1
            except Answer.DoesNotExist: pass
    score = (correct_answers_count / total_questions) * 100 if total_questions > 0 else 0
    result.score = round(score, 2); result.save()
    return redirect('quiz:view_result', pk=result.pk)


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
    shuffled_questions = []
    for q in questions:
        answers = list(q.answers.all()); random.shuffle(answers)
        shuffled_questions.append({'question': q, 'answers': answers})
    context = {'subject': subject, 'shuffled_questions': shuffled_questions}
    return render(request, 'practice_mode/practice_session.html', context)

@login_required
@student_required
def submit_practice(request):
    if request.method != 'POST': return redirect('quiz:practice_selection')
    question_ids = request.POST.getlist('question_id')
    questions = Question.objects.filter(id__in=question_ids).prefetch_related('answers')
    results_data = []
    correct_count = 0
    for question in questions:
        selected_answer_id = request.POST.get(f'question_{question.id}')
        correct_answer = question.answers.get(is_correct=True)
        is_student_correct = (str(correct_answer.id) == selected_answer_id)
        if is_student_correct: correct_count += 1
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