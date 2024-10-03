# views.py
from django.shortcuts import render, redirect
from .forms import RegistrationForm, CustomLoginForm
from django.contrib import messages
from django.contrib.auth import login, authenticate
from module_group.models import ModuleGroup, Module

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
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)  # Sửa chỗ này
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Điều hướng về trang chính sau khi đăng nhập thành công
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Error in form data.")
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})
