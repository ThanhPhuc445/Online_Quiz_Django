# quiz/models.py
from django.db import models
from django.conf import settings

class Subject(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "EASY", "Dễ"
        MEDIUM = "MEDIUM", "Trung bình"
        HARD = "HARD", "Khó"

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer for: {self.question.text[:20]}"

# ===== ĐÂY LÀ CLASS QUAN TRỌNG BỊ THIẾU =====
class Quiz(models.Model):
    title = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    questions = models.ManyToManyField(Question)
    duration_minutes = models.PositiveIntegerField(help_text="Thời gian làm bài (phút)")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.title