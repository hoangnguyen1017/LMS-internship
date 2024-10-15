from django.shortcuts import render, redirect
from .forms import RegistrationForm, CustomLoginForm
from django.contrib.auth import authenticate, login
from user.models import User, Profile, Role
from module_group.models import Module, ModuleGroup
from django.db.models import Q
from module_group.forms import ExcelImportForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .forms import PasswordResetRequestForm, PasswordResetCodeForm, PasswordResetForm
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.cache import cache

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                random_code = get_random_string(length=6)

                request.session['reset_code'] = random_code
                request.session['user_id'] = user.id
                request.session['email'] = email
                request.session['code_created_at'] = timezone.now().isoformat()

                send_mail(
                    'Password Reset Code',
                    f'Your code is: {random_code}',
                    'from@example.com',
                    [email],
                    fail_silently=False,
                )
                return redirect('main:password_reset_code')
            except User.DoesNotExist:
                messages.error(request, 'Email does not exist.')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'password_reset.html', {'form': form, 'current_step': 'request'})

def get_remaining_time(created_at, expiration_duration_minutes):
    if created_at:
        created_at = timezone.datetime.fromisoformat(created_at)
        if created_at.tzinfo is None:
            created_at = timezone.make_aware(created_at)

        expiration_time = created_at + timedelta(minutes=expiration_duration_minutes)
        remaining_time = expiration_time - timezone.now()

        if remaining_time.total_seconds() >= 0:
            minutes = remaining_time.seconds // 60
            seconds = remaining_time.seconds % 60  
            return remaining_time, minutes, seconds

    return None, 0, 0

def password_reset_code(request):
    created_at = request.session.get('code_created_at')
    expiration_duration_minutes = 0.5  

    
    remaining_time, minutes, seconds = get_remaining_time(created_at, expiration_duration_minutes)

    if request.method == 'POST':
        form = PasswordResetCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            session_code = request.session.get('reset_code')

            if session_code and created_at:
                if code == session_code and remaining_time and remaining_time.total_seconds() > 0:
                    messages.success(request, 'The verification code is valid. Please enter a new password.')
                    return redirect('main:password_reset_form')
                else:
                    messages.error(request, 'The code has expired or is invalid.')
            else:
                messages.error(request, 'The code is invalid.')
        else:
            messages.error(request, 'An error occurred. Please check your code.')
    else:
        form = PasswordResetCodeForm()


    return render(request, 'password_reset.html', {
        'form': form,
        'current_step': 'code',
        'remaining_time': remaining_time,
        'minutes': minutes,
        'seconds': seconds  # Gửi seconds dưới dạng số nguyên
    })

def resend_code_auto(request):
    email = request.session.get('email')

    if email:
        user = User.objects.filter(email=email).first()
        
        if user:
            random_code = get_random_string(length=6)

            request.session['reset_code'] = random_code
            request.session['code_created_at'] = timezone.now().isoformat()

            try:
                send_mail(
                    'Password Reset Verification Code',
                    f'Your verification code is: {random_code}',
                    'no-reply@yourdomain.com',
                    [email],
                    fail_silently=False,
                )

                messages.success(request, 'The verification code has been resent to your email.')
            except Exception as e:
                messages.error(request, f'Failed to send email: {str(e)}')
        else:
            messages.error(request, 'User with this email does not exist.')
    else:
        messages.error(request, 'Email not found. Please try again.')

    return redirect('main:password_reset_code')

def password_reset_form(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user_id = request.session.get('user_id')
            if user_id:
                user = User.objects.get(id=user_id)
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password updated successfully.')
                del request.session['reset_code']
                del request.session['user_id']
                return redirect('main:home')
    else:
        form = PasswordResetForm()
    
    return render(request, 'password_reset.html', {'form': form, 'current_step': 'reset'})

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main:login')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    selected_role = request.POST.get('role', '')

    if request.method == 'POST':
        form = CustomLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_superuser:
                    login(request, user)
                    return redirect('/admin/')
                user_role = user.profile.role.role_name

                if user_role == selected_role:
                    login(request, user)
                    messages.success(request, "Login successful!")
                    next_url = request.GET.get('next', 'main:home')
                    return redirect(next_url)
                else:
                    messages.error(request, "Role does not match your account's role.")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Form is not valid.")
    else:
        form = CustomLoginForm()

    roles = Role.objects.all()
    return render(request, 'login.html', {
        'form': form,
        'roles': roles,
        'selected_role': selected_role if not request.user.is_superuser else ''
    })

def home(request):
    query = request.GET.get('q')
    all_modules = Module.objects.all()

    if request.user.is_authenticated:
        try:
            user_profile = getattr(request.user, 'profile', None)
            user_role = getattr(user_profile, 'role', None)

            if request.user.is_superuser:
                modules = all_modules
            elif user_role:
                modules = all_modules.filter(role_modules=user_role).distinct()
            else:
                messages.error(request, "Invalid role or no modules available for this role.")
                modules = Module.objects.none()
        except AttributeError:
            messages.error(request, "User profile not found.")
            modules = Module.objects.none()
    else:
        modules = all_modules

    if query:
        modules = modules.filter(
            Q(module_name__icontains=query) |
            Q(module_group__group_name__icontains=query)
        )

    module_groups = ModuleGroup.objects.all()
    form = ExcelImportForm()

    return render(request, 'home.html', {
        'module_groups': module_groups,
        'modules': modules,
        'form': form,
    })
