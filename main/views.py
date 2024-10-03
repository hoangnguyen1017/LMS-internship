from django.shortcuts import render, redirect
from .forms import RegistrationForm, CustomLoginForm, Registration
from module_group.models import ModuleGroup, Module
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
from functools import wraps
from role.models import Role
from user.models import User
# Định nghĩa decorator
def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('main:login')  # Chuyển hướng đến trang đăng nhập
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
def home(request):
    module_groups = ModuleGroup.objects.all()
    modules = Module.objects.all()
    return render(request, 'home.html', {
        'module_groups': module_groups,
        'modules': modules,
    })


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('main:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})



def login_view(request):
    # Kiểm tra nếu người dùng đã đăng nhập
    if request.session.get('user_id'):
        return redirect('main:home')  

    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            full_name = form.cleaned_data['full_name']
            password = form.cleaned_data['password']
            try:
                # Kiểm tra theo username trước
                user = User.objects.get(username=username)
                # Hoặc có thể kiểm tra theo full_name
                if not user:  # nếu không tìm thấy user theo username, kiểm tra full_name
                    user = User.objects.get(full_name=full_name)

                # Kiểm tra mật khẩu
                if check_password(password, user.password):
                    # Lưu thông tin người dùng vào session
                    request.session['user_id'] = user.id
                    request.session['username'] = user.username  # Lưu username
                    request.session['full_name'] = user.full_name
                    request.session['role_id'] = user.role.id  
                    request.session['profile_picture_url'] = user.profile_picture_url  # Lưu URL hình ảnh

                    # Redirect đến trang chính sau khi đăng nhập
                    return redirect('main:home')  
            except User.DoesNotExist:
                messages.error(request, "Invalid username or password.")
    
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})



