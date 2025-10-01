# quiz/models.py

from django.db import models
from django.conf import settings
import uuid

class Subject(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Tên môn học")

    def __str__(self):
        return self.name

class Question(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "EASY", "Dễ"
        MEDIUM = "MEDIUM", "Trung bình"
        HARD = "HARD", "Khó"

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions', verbose_name="Môn học")
    text = models.TextField(verbose_name="Nội dung câu hỏi")
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, verbose_name="Độ khó")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Người tạo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    def __str__(self):
        return self.text[:50]

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE, verbose_name="Câu hỏi")
    text = models.CharField(max_length=255, verbose_name="Nội dung đáp án")
    is_correct = models.BooleanField(default=False, verbose_name="Là đáp án đúng?")

    def __str__(self):
        return self.text

class Quiz(models.Model):
    title = models.CharField(max_length=255, verbose_name="Tiêu đề đề thi")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Môn học")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Người tạo")
    questions = models.ManyToManyField(Question, verbose_name="Các câu hỏi")
    duration_minutes = models.PositiveIntegerField(help_text="Thời gian làm bài (tính bằng phút)", verbose_name="Thời gian làm bài")
    start_time = models.DateTimeField(verbose_name="Thời gian bắt đầu")
    end_time = models.DateTimeField(verbose_name="Thời gian kết thúc")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    
    # === TRƯỜNG MỚI ĐƯỢC THÊM VÀO ===
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

    def save(self, *args, **kwargs):
        # Tự động tạo mã tham gia nếu chưa có
        if not self.access_code:
            self.access_code = str(uuid.uuid4()).upper().replace('-', '')[:6]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title