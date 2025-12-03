from django.contrib import admin
from .models import SupportTicket

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'teacher', 'subject', 'ticket_type', 'status', 'created_at']
    list_filter = ['status', 'ticket_type', 'created_at']
    search_fields = ['subject', 'message', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Thông tin yêu cầu', {
            'fields': ('user', 'teacher', 'quiz', 'ticket_type', 'subject', 'message')
        }),
        ('Phản hồi', {
            'fields': ('admin', 'admin_response', 'status')
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )