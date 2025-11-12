from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def mathjax(text):
    """Filter để xử lý công thức toán học"""
    if text:
        # Có thể thêm xử lý đặc biệt cho công thức toán ở đây
        return mark_safe(text)
    return text