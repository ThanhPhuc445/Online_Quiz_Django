# quiz/models.py

from django.db import models
from django.conf import settings
import uuid

class Subject(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Tên môn học")

    def __str__(self):
        return self.name

class Question(models.Model):
    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = "MULTIPLE_CHOICE", "Câu hỏi nhiều lựa chọn"
        TRUE_FALSE = "TRUE_FALSE", "Câu hỏi Đúng/Sai"
        SHORT_ANSWER = "SHORT_ANSWER", "Câu tự luận ngắn"
        SINGLE_CHOICE = "SINGLE_CHOICE", "Câu hỏi một lựa chọn"
    
    class Difficulty(models.TextChoices):
        EASY = "EASY", "Dễ"
        MEDIUM = "MEDIUM", "Trung bình"
        HARD = "HARD", "Khó"

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions', verbose_name="Môn học")
    text = models.TextField(verbose_name="Nội dung câu hỏi")
    question_type = models.CharField(
        max_length=20, 
        choices=QuestionType.choices, 
        default=QuestionType.SINGLE_CHOICE,
        verbose_name="Loại câu hỏi"
    )
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, verbose_name="Độ khó")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Người tạo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    # Thêm trường cho câu hỏi tự luận
    correct_answer_text = models.TextField(blank=True, null=True, verbose_name="Đáp án đúng (cho tự luận)")

    def __str__(self):
        return self.text[:50]

    def clean(self):
        """Validation cho loại câu hỏi"""
        from django.core.exceptions import ValidationError
        
        if self.question_type == self.QuestionType.SHORT_ANSWER and not self.correct_answer_text:
            raise ValidationError({'correct_answer_text': 'Vui lòng nhập đáp án đúng cho câu hỏi tự luận'})

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE, verbose_name="Câu hỏi")
    text = models.CharField(max_length=255, verbose_name="Nội dung đáp án")
    is_correct = models.BooleanField(default=False, verbose_name="Là đáp án đúng?")

    def __str__(self):
        return self.text
    
    def clean(self):
        """Validation cho đáp án"""
        from django.core.exceptions import ValidationError
        
        if self.question.question_type == Question.QuestionType.TRUE_FALSE:
            if self.text not in ['Đúng', 'Sai']:
                raise ValidationError({'text': 'Câu hỏi Đúng/Sai chỉ được có đáp án "Đúng" hoặc "Sai"'})

class Quiz(models.Model):
    title = models.CharField(max_length=255, verbose_name="Tiêu đề đề thi")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Môn học")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Người tạo")
    questions = models.ManyToManyField(Question, verbose_name="Các câu hỏi")
    duration_minutes = models.PositiveIntegerField(help_text="Thời gian làm bài (tính bằng phút)", verbose_name="Thời gian làm bài")
    start_time = models.DateTimeField(verbose_name="Thời gian bắt đầu")
    end_time = models.DateTimeField(verbose_name="Thời gian kết thúc")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    
    is_public = models.BooleanField(
        default=True, 
        verbose_name="Công khai?",
        help_text="Nếu được chọn, tất cả học sinh sẽ thấy đề thi này. Nếu không, chỉ học sinh tham gia bằng mã code mới thấy."
    )
    
    # Trường này vẫn cần để lưu danh sách học sinh tham gia đề riêng tư
    allowed_students = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='allowed_quizzes', 
        blank=True,
        limit_choices_to={'role': 'STUDENT'},
        verbose_name="Học sinh được phép tham gia (cho đề riêng tư)"
    )

    access_code = models.CharField(
        max_length=8, 
        unique=True, 
        blank=True, 
        null=True,
        verbose_name="Mã tham gia"
    )
    allow_multiple_attempts = models.BooleanField(
        default=False,
        verbose_name="Cho phép thi nhiều lần",
        help_text="Nếu được chọn, học sinh có thể thi đề này nhiều lần. Nếu không, mỗi học sinh chỉ được thi 1 lần."
    )
    def save(self, *args, **kwargs):
        # Tự động tạo mã tham gia nếu chưa có
        if not self.access_code:
            self.access_code = str(uuid.uuid4()).upper().replace('-', '')[:6]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title