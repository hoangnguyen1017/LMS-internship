from django.shortcuts import render, redirect
from .forms import RegistrationForm, CustomLoginForm, Registration
from module_group.models import ModuleGroup, Module
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
from functools import wraps

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
    # Kiểm tra xem người dùng đã đăng nhập hay chưa
    if request.session.get('user_id'):
        return redirect('main:home')  # Chuyển hướng nếu đã đăng nhập

    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = Registration.objects.get(username=username)
                
                if check_password(password, user.password):
                    # Lưu thông tin đăng nhập vào phiên
                    request.session['user_id'] = user.id
                    request.session['username'] = user.username
                    return redirect('main:home')  
                else:
                    messages.error(request, "Invalid username or password.")
            except Registration.DoesNotExist:
                messages.error(request, "Invalid username or password.")
    
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})






