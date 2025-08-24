from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm

def register(request):
    # Nếu người dùng đã đăng nhập, không cho vào trang đăng ký nữa
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            # Gửi một thông báo flash để hiển thị ở trang đăng nhập
            messages.success(request, f'Tài khoản "{username}" đã được tạo thành công! Vui lòng đăng nhập.')
            return redirect('login') # Chuyển hướng đến trang đăng nhập
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})