from django.shortcuts import render, redirect
from .forms import RegistrationForm, CustomLoginForm, Registration
from module_group.models import ModuleGroup, Module
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required


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
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = Registration.objects.get(username=username)
                
                if check_password(password, user.password):
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