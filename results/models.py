# results/models.py
from django.db import models
from django.conf import settings
from quiz.models import Quiz, Question, Answer

class Result(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"

class StudentAnswer(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='student_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"Answer for {self.question.id} in result {self.result.id}"