from django.shortcuts import render, get_object_or_404, redirect
from role.models import Role
from .models import Profile, User, Student
import pandas as pd
import bcrypt
from openpyxl import Workbook
from django.http import HttpResponse
from django.contrib import messages
from user.forms import UserForm, RoleForm, ExcelImportForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from .forms import AssignTrainingProgramForm, UserEditForm
from .decorators import role_required
from functools import wraps
from django.contrib.auth.decorators import login_required
from django import forms
from course.forms import UserCourseProgress
@login_required
def assign_training_programs(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = AssignTrainingProgramForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Training programs successfully assigned to {user.username}.")
            return redirect('user:user_list')
    else:
        form = AssignTrainingProgramForm(instance=user)

    return render(request, 'assign_training_programs.html', {'user': user, 'form': form})

@login_required
def user_list(request):
    query = request.GET.get('q', '')
    selected_role = request.GET.get('role', '')
    users = User.objects.exclude(is_superuser=True)
    roles = Role.objects.all()
    form = ExcelImportForm()

    if query and selected_role:
        users = users.filter(
            Q(username__icontains=query),
            profile__role__role_name=selected_role
        )
    elif query:
        users = users.filter(username__icontains=query)
    elif selected_role:
        users = users.filter(profile__role__role_name=selected_role)

    not_found = not users.exists()

    users = users.order_by('username')

    paginator = Paginator(users, 5)
    page = request.GET.get('page', 1)

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    return render(request, 'user_list.html', {
        'users': users,
        'query': query,
        'roles': roles,
        'selected_role': selected_role,
        'not_found': not_found,
        'form': form,
    })

@login_required
def student_list(request):
    query = request.GET.get('q', '')
    students = Student.objects.all()
    form = ExcelImportForm()

    if query:
        students = students.filter(
            Q(user__username__icontains=query)
        )

    students = students.order_by('user__username')

    paginator = Paginator(students, 5)
    page = request.GET.get('page', 1)

    try:
        students = paginator.page(page)
    except PageNotAnInteger:
        students = paginator.page(1)
    except EmptyPage:
        students = paginator.page(paginator.num_pages)

    return render(request, 'student_list.html', {
        'students': students,
        'query': query,
        'form': form,
    })

@login_required
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)

    course_progress = UserCourseProgress.objects.filter(user=user)

    courses_with_progress = [
        {
            'course': progress.course,
            'progress_percentage': progress.progress_percentage
        }
        for progress in course_progress
    ]

    role = getattr(user.profile.role, 'role_name', None)
    is_student = request.user.is_authenticated and role == 'Student'

    student_code = "N/A"
    if is_student:
        try:
            student = Student.objects.get(user=user)
            student_code = student.student_code if student.student_code else "N/A"
        except Student.DoesNotExist:
            student_code = "N/A"

    return render(request, 'user_detail.html', {
        'user': user,
        'courses_with_progress': courses_with_progress,
        'is_student': is_student,
        'student_code': student_code
    })


@login_required
def user_add(request):
    is_superuser = request.user.is_superuser

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            profile = Profile(
                user=user,
                role=form.cleaned_data['role'],
                profile_picture_url=form.cleaned_data.get('profile_picture_url', ''),
                bio=form.cleaned_data.get('bio', ''),
                interests=form.cleaned_data.get('interests', ''),
                learning_style=form.cleaned_data.get('learning_style', ''),
                preferred_language=form.cleaned_data.get('preferred_language', '')
            )
            profile.save()

            if profile.role.role_name == 'Student':
                try:
                    student_code = form.cleaned_data.get('student_code')  
                    student = Student(user=user, student_code=student_code)
                    student.save()
                    profile.student = student
                    profile.save()
                except Exception as e:
                    print('Error saving Student:', e)

            training_programs = form.cleaned_data.get('training_programs')
            if training_programs:
                user.training_programs.set(training_programs)

            return redirect('user:user_list')
        else:
            print('Invalid form')
            print(form.errors)
    else:
        form = UserForm()
    
    return render(request, 'user_form.html', {'form': form, 'is_superuser': is_superuser})


@login_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.user.pk != user.pk and not (request.user.is_superuser or 
        (hasattr(request.user, 'profile') and request.user.profile.role and request.user.profile.role.role_name == 'Manager')):
        messages.error(request, "Bạn không có quyền chỉnh sửa người dùng này.")
        return redirect('user:user_list')

    profile, created = Profile.objects.get_or_create(user=user)
    old_role = profile.role

    student_code = None
    if profile.role.role_name == 'Student':
        try:
            student = Student.objects.get(user=user)
            student_code = student.student_code
        except Student.DoesNotExist:
            pass

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)

        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            
            new_role = form.cleaned_data['role']
            if new_role != old_role:
                profile.role = new_role
            
            new_profile_picture_url = form.cleaned_data.get('profile_picture_url')
            profile.profile_picture_url = new_profile_picture_url if new_profile_picture_url else profile.profile_picture_url
            
            profile.bio = form.cleaned_data.get('bio', profile.bio)
            profile.interests = form.cleaned_data.get('interests', profile.interests)
            profile.learning_style = form.cleaned_data.get('learning_style', profile.learning_style)
            profile.preferred_language = form.cleaned_data.get('preferred_language', profile.preferred_language)

            if profile.role.role_name == 'Student':
                student, created = Student.objects.get_or_create(user=user)
                new_student_code = form.cleaned_data.get('student_code', student_code)
                student.student_code = new_student_code if new_student_code else student_code
                student.save()
                profile.student = student
            else:
                try:
                    student = Student.objects.get(user=user)
                    student.delete()
                    profile.student = None
                except Student.DoesNotExist:
                    pass
            
            profile.save()
            user.save()
            
            training_programs = form.cleaned_data.get('training_programs')
            if training_programs:
                user.training_programs.set(training_programs)

            if request.user.pk == user.pk:
                request.session['username'] = user.username
                request.session['full_name'] = f"{user.first_name} {user.last_name}"
                request.session['role'] = profile.role.role_name if profile.role else 'No Role'
                request.session['profile_picture_url'] = profile.profile_picture_url
                request.session['bio'] = profile.bio
                request.session['interests'] = profile.interests
                request.session['learning_style'] = profile.learning_style
                request.session['preferred_language'] = profile.preferred_language

            messages.success(request, f"Người dùng {user.username} đã được cập nhật thành công.")
            return redirect('user:user_list')
        else:
            messages.error(request, "Vui lòng sửa các lỗi bên dưới.")
    else:
        form = UserForm(instance=user)

    form.fields['bio'].initial = profile.bio
    form.fields['interests'].initial = profile.interests
    form.fields['learning_style'].initial = profile.learning_style
    form.fields['preferred_language'].initial = profile.preferred_language
    form.fields['profile_picture_url'].initial = profile.profile_picture_url
    form.fields['role'].initial = profile.role
    if hasattr(request.user, 'profile') and request.user.profile.role and request.user.profile.role.role_name == 'User':
        form.fields['role'].widget.attrs['disabled'] = True

    if profile.role.role_name == 'Student':
        form.fields['student_code'].initial = student_code
    else:
        form.fields['student_code'].widget = forms.HiddenInput()

    return render(request, 'user_form.html', {'form': form, 'user': user})


@login_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, "delete successful!")
        return redirect('user:user_list')

    return render(request, 'user_confirm_delete.html', {'user': user})



@login_required
@role_required(['Manager'])
def export_users(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    selected_role = request.GET.get('role', '').strip()

    if selected_role:
        safe_role = "".join(c for c in selected_role if c.isalnum() or c in ['_', '-'])
        filename = f'{safe_role}.xlsx'
    else:
        filename = 'users.xlsx'

    response['Content-Disposition'] = f'attachment; filename={filename}'

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = f'{safe_role}' if selected_role else 'Users'

    columns = ['Username', 'Email', 'First Name', 'Last Name', 'Role', 'Profile Picture', 'Password Hash', 'Bio', 'Interests', 'Learning Style', 'Preferred Language', 'Student Code']
    worksheet.append(columns)

    users = User.objects.exclude(is_superuser=True)

    if selected_role:
        users = users.filter(profile__role__role_name=selected_role)

    for user in users:
        profile = Profile.objects.filter(user=user).first()
        student = None

        if profile and profile.student:
            student = profile.student

        if profile:
            role_name = profile.role.role_name if profile.role else 'No Role'
            profile_picture_url = profile.profile_picture_url if profile else 'No Image'
            bio = profile.bio if profile else 'N/A'
            interests = profile.interests if profile else 'N/A'
            learning_style = profile.learning_style if profile else 'N/A'
            preferred_language = profile.preferred_language if profile else 'N/A'
        else:
            role_name = 'No Role'
            profile_picture_url = 'No Image'
            bio = 'N/A'
            interests = 'N/A'
            learning_style = 'N/A'
            preferred_language = 'N/A'

        password_hash = user.password
        student_code = student.student_code if student else 'N/A'

        worksheet.append([
            user.username, user.email, user.first_name, user.last_name,
            role_name, profile_picture_url, password_hash, bio, interests, learning_style, preferred_language, student_code
        ])

    workbook.save(response)
    return response

@login_required
@role_required(['Manager'])
def import_users(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, "Invalid file format. Please upload an .xlsx file.")
            return redirect('user:user_list')

        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            messages.error(request, f"Error reading the Excel file: {e}")
            return redirect('user:user_list')

        for index, row in df.iterrows():
            username = row.get('Username')
            email = row.get('Email')
            first_name = row.get('First Name')
            last_name = row.get('Last Name')
            role_name = row.get('Role')
            password_hash = row.get('Password Hash')
            profile_picture_url = row.get('Profile Picture')
            bio = row.get('Bio')
            interests = row.get('Interests')
            learning_style = row.get('Learning Style')
            preferred_language = row.get('Preferred Language')
            student_code = row.get('Student Code')

            if not username or not email or not password_hash:
                messages.warning(request, f"Missing required fields for user at row {index + 1}. Skipping.")
                continue

            user, created = User.objects.get_or_create(username=username, defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'password': password_hash
            })

            profile = Profile.objects.filter(user=user).first()
            old_role_name = profile.role.role_name if profile and profile.role else None

            if not created:
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.password = password_hash
                user.save()

            if role_name:
                role = Role.objects.filter(role_name=role_name).first()
                if role:
                    profile, _ = Profile.objects.get_or_create(user=user)
                    profile.role = role
                    profile.profile_picture_url = profile_picture_url or 'No Image'
                    profile.bio = bio or 'N/A'
                    profile.interests = interests or 'N/A'
                    profile.learning_style = learning_style or 'N/A'
                    profile.preferred_language = preferred_language or 'N/A'
                    profile.save()

                    if role_name == 'Student':
                        student, _ = Student.objects.get_or_create(user=user)
                        student.student_code = student_code or 'N/A'
                        student.save()
                        profile.student = student
                        profile.save()
                else:
                    messages.warning(request, f"Role '{role_name}' not found for user {username}.")
            else:
                messages.warning(request, f"User {username} has no role assigned.")

            if old_role_name == 'Student' and profile.role.role_name != 'Student':
                try:
                    student = Student.objects.get(user=user)
                    student.delete()
                except Student.DoesNotExist:
                    pass

        messages.success(request, "Users imported successfully!")
        return redirect('user:user_list')

    messages.error(request, "Failed to import users.")
    return redirect('user:user_list')

from django.contrib.auth.hashers import check_password

def user_edit_password(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        if check_password(old_password, user.password):
            return redirect('user:user_edit', user.pk)
        else:
            error_message = "Incorrect password. Please try again."
            return render(request, 'user_detail.html', {'user': user, 'error_message': error_message})

    return render(request, 'user_detail.html', {'user': user})
