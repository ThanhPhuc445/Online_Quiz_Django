from django.db import models
from django.conf import settings
from quiz.models import Quiz

class SupportTicket(models.Model):
    class TicketType(models.TextChoices):
        TECHNICAL = 'TECHNICAL', 'Sự cố kỹ thuật'
        QUESTION = 'QUESTION', 'Câu hỏi về đề thi'
        ACCOUNT = 'ACCOUNT', 'Vấn đề tài khoản'
        FEEDBACK = 'FEEDBACK', 'Góp ý, phản hồi'
        OTHER = 'OTHER', 'Khác'
    
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Đang chờ xử lý'
        IN_PROGRESS = 'IN_PROGRESS', 'Đang xử lý'
        RESOLVED = 'RESOLVED', 'Đã giải quyết'
        CLOSED = 'CLOSED', 'Đã đóng'
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                            verbose_name="Người gửi", related_name='support_tickets')
    
    # Thêm trường teacher để lưu giáo viên được liên hệ
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                               null=True, blank=True, verbose_name="Giáo viên",
                               related_name='received_tickets', limit_choices_to={'role': 'TEACHER'})
    
    ticket_type = models.CharField(max_length=20, choices=TicketType.choices, 
                                  default=TicketType.QUESTION, verbose_name="Loại yêu cầu")
    subject = models.CharField(max_length=200, verbose_name="Tiêu đề")
    message = models.TextField(verbose_name="Nội dung")
    
    # Liên quan đến đề thi (nếu có)
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True, blank=True, 
                            verbose_name="Liên quan đến đề thi")
    
    # Thông tin phản hồi
    admin_response = models.TextField(blank=True, null=True, verbose_name="Phản hồi từ quản trị viên")
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, 
                             related_name='handled_tickets', verbose_name="Người xử lý",
                             limit_choices_to={'role': 'ADMIN'})
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, 
                             verbose_name="Trạng thái")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    is_read = models.BooleanField(default=False, verbose_name="Đã đọc?")
    replied_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                   null=True, blank=True, verbose_name="Người phản hồi",
                                   related_name='replied_tickets')
    replied_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian phản hồi")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Yêu cầu hỗ trợ"
        verbose_name_plural = "Yêu cầu hỗ trợ"
    
    def __str__(self):
        return f"{self.user.username} - {self.subject} ({self.get_status_display()})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('quiz:support_ticket_detail', kwargs={'ticket_id': self.id})