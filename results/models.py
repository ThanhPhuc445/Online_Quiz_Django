# results/models.py
from django.db import models
from django.conf import settings
from quiz.models import Quiz, Question, Answer

class Result(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    completed_at = models.DateTimeField(auto_now_add=True)
    
    # === THÊM CÁC TRƯỜNG MỚI ===
    is_graded = models.BooleanField(default=False, verbose_name="Đã được chấm điểm?")
    teacher_feedback = models.TextField(blank=True, null=True, verbose_name="Nhận xét của giáo viên")
    short_answer_score = models.FloatField(default=0, verbose_name="Điểm tự luận")

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"

    @property
    def short_answer_count(self):
        """Số câu hỏi tự luận trong bài thi"""
        return self.student_answers.filter(question__question_type='SHORT_ANSWER').count()

class StudentAnswer(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='student_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    
    custom_answer = models.TextField(blank=True, null=True, verbose_name="Câu trả lời tự luận")
    created_at = models.DateTimeField(auto_now_add=True)
    
    # === THÊM TRƯỜNG CHẤM ĐIỂM ===
    points_earned = models.FloatField(default=0, verbose_name="Điểm đạt được")
    teacher_comment = models.TextField(blank=True, null=True, verbose_name="Nhận xét của giáo viên")
    
    @property
    def is_correct(self):
        """Kiểm tra câu trả lời có đúng không"""
        if self.question.question_type == Question.QuestionType.SHORT_ANSWER:
            return self.points_earned > 0
        elif self.selected_answer:
            return self.selected_answer.is_correct
        return False
    
    @property
    def is_short_answer(self):
        """Kiểm tra có phải câu hỏi tự luận không"""
        return self.question.question_type == Question.QuestionType.SHORT_ANSWER

    def __str__(self):
        if self.selected_answer:
            return f"Answer for {self.question.id} in result {self.result.id}"
        else:
            return f"Short answer for {self.question.id} in result {self.result.id}"

class PracticeResult(models.Model):
    """Kết quả luyện tập (không ảnh hưởng đến điểm chính thức)"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    total_questions = models.IntegerField()
    correct_answers = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} - {self.score}"