# quiz/admin.py
from django.contrib import admin
from .models import Subject, Question, Answer, Quiz

# 1. Đăng ký Môn học (Quan trọng nhất để fix lỗi của bạn)
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# 2. Đăng ký Câu hỏi (Để Admin soi nội dung nếu cần)
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'subject', 'question_type', 'difficulty', 'created_by')
    list_filter = ('subject', 'question_type', 'difficulty')
    search_fields = ('text',)
    inlines = [AnswerInline] # Cho phép sửa đáp án ngay trong câu hỏi

# 3. Đăng ký Đề thi
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'created_by', 'start_time', 'is_public')
    list_filter = ('subject', 'is_public')
    search_fields = ('title',)