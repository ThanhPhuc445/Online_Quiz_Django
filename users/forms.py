from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User

class CustomUserCreationForm(UserCreationForm):
    # Định nghĩa lại các trường để thêm class của Bootstrap cho đẹp
    username = forms.CharField(label='Tên đăng nhập', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email', required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(label='Vai trò', choices=User.Role.choices, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        model = User
        # Các trường sẽ được hiển thị trên form
        fields = ('username', 'email', 'role')