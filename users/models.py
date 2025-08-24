from django.contrib.auth.models import AbstractUser
from django.db import models

# Tên class phải là "User" (viết hoa chữ U)
class User(AbstractUser): 
    
    # Class Role phải nằm bên trong class User
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        TEACHER = "TEACHER", "Giáo viên"
        STUDENT = "STUDENT", "Học sinh"

    # Các trường khác
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.STUDENT)

    # Dòng này không bắt buộc nhưng nên có
    def __str__(self):
        return self.username