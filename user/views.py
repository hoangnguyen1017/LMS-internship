from django.shortcuts import render, get_object_or_404, redirect
from role.models import Role
from .models import Profile, User, Student, Instructor
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from user.forms import UserForm, ExcelImportForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import UserCourseProgress
from course.models import Enrollment
from quiz.models import StudentQuizAttempt
from activity.models import UserActivityLog
from django.contrib.auth.hashers import check_password
from import_export.formats.base_formats import XLSX
from .admin import UserProfileResource
from tablib import Dataset
from django.utils import timezone
from datetime import timedelta
from module_group.models import ModuleGroup
from main.module_utils import get_grouped_modules
from course.models import Course
from django.contrib.auth import logout
from main.models import PasswordChangeRecord
from import_export.formats.base_formats import XLSX, JSON, YAML, CSV, TSV
from django.core.files.uploadedfile import UploadedFile
from django.views.decorators.csrf import csrf_protect


@login_required
def user_list(request):
    is_superuser = request.user.is_superuser
    module_groups = ModuleGroup.objects.all()  # Thay đổi theo cách bạn lấy dữ liệu

    # Kiểm tra xem người dùng có profile hay không, nếu không là superuser thì hiện thông báo lỗi
    if not is_superuser and (not hasattr(request.user, 'profile') or request.user.profile is None):
        messages.error(request, "Bạn không có quyền.")
        return redirect('user:user_list')

    user_role_permissions = request.user.profile.role.permissions.values_list('codename', flat=True) if not is_superuser else []

    # Kiểm tra quyền
    can_detail_user = 'can_detail_user' in user_role_permissions or is_superuser
    can_add_user = 'can_add_user' in user_role_permissions or is_superuser
    can_edit_user = 'can_edit_user' in user_role_permissions or is_superuser
    can_delete_user = 'can_delete_user' in user_role_permissions or is_superuser
    can_import_users = 'can_import_users' in user_role_permissions or is_superuser
    can_export_users = 'can_export_users' in user_role_permissions or is_superuser

    # Lấy các thông tin tìm kiếm từ request
    query = request.GET.get('q', '')
    selected_role = request.GET.get('role', '')

    # Lấy danh sách người dùng, không bao gồm superuser
    users = User.objects.exclude(is_superuser=True)
    roles = Role.objects.all()
    form = ExcelImportForm()

    # Lọc người dùng dựa trên truy vấn tìm kiếm
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

    # Phân trang
    paginator = Paginator(users, 10)
    page = request.GET.get('page', 1)

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    if 'lock_user' in request.GET:
        user_id = request.GET.get('lock_user')
        try:
            user_to_lock = User.objects.get(id=user_id)
            if is_superuser:
                user_to_lock.is_locked = True  # Sử dụng thuộc tính is_locked của User
                user_to_lock.save()
                messages.success(request, f"Tài khoản {user_to_lock.username} đã bị khóa.")
            else:
                messages.error(request, "Bạn không có quyền khóa tài khoản này.")
        except User.DoesNotExist:
            messages.error(request, "Người dùng không tồn tại.")
    
    if 'unlock_user' in request.GET:
        user_id = request.GET.get('unlock_user')
        try:
            user_to_unlock = User.objects.get(id=user_id)
            if is_superuser:
                user_to_unlock.is_locked = False  # Sử dụng thuộc tính is_locked của User
                user_to_unlock.save()
                messages.success(request, f"Tài khoản {user_to_unlock.username} đã được mở khóa.")
            else:
                messages.error(request, "Bạn không có quyền mở khóa tài khoản này.")
        except User.DoesNotExist:
            messages.error(request, "Người dùng không tồn tại.")

    return render(request, 'user_list.html', {
        'users': users,
        'query': query,
        'roles': roles,
        'selected_role': selected_role,
        'not_found': not_found,
        'form': form,
        'can_detail_user': can_detail_user,
        'can_add_user': can_add_user,
        'can_edit_user': can_edit_user,
        'can_delete_user': can_delete_user,
        'can_import_users': can_import_users,
        'can_export_users': can_export_users,
        'page_obj': users,
        'module_groups': module_groups,
    })
from django.conf import settings
from django.core.mail import send_mail
@login_required
def student_list(request):
    # Lấy từ khóa tìm kiếm
    query = request.GET.get('q', '')
    students = Student.objects.select_related('user').all()  # Tối ưu hóa với select_related
    form = ExcelImportForm()

    # Lọc danh sách sinh viên theo từ khóa
    if query:
        students = students.filter(Q(user__username__icontains=query))

    # Sắp xếp danh sách sinh viên theo username
    students = students.order_by('user__username')

    # Phân trang
    paginator = Paginator(students, 5)  # 5 sinh viên mỗi trang
    page = request.GET.get('page', 1)
    try:
        students = paginator.page(page)
    except PageNotAnInteger:
        students = paginator.page(1)
    except EmptyPage:
        students = paginator.page(paginator.num_pages)

    # Gửi email và tạo thông báo
    def send_progress_email_and_create_notification(student, email_subject, email_body):
        # Gửi email
        send_mail(
            email_subject,
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [student.user.email],
            fail_silently=False,
        )


    # Xử lý gửi email nhắc nhở nếu form được submit
    if request.method == 'POST' and 'send_dropout_emails' in request.POST:
        selected_student_ids = request.POST.getlist('selected_students')
        students_to_notify = Student.objects.filter(id__in=selected_student_ids)

        for student in students_to_notify:
            email_body = (
                f"Hello {student.user.username},\n\n"
                f"Please remember to continue your studies.\n\n"
                f"Best regards,\nYour Learning Platform Team"
            )

            # Gửi email và tạo thông báo
            send_progress_email_and_create_notification(student, email_body)

    return render(
        request,
        'student_list.html',
        {
            'students': students,
            'query': query,
            'form': form,
            'page_obj': students,
        }
    )



@login_required
def user_detail(request, pk):
    # Lấy thông tin người dùng
    user = get_object_or_404(User, pk=pk)
    is_superuser = request.user.is_superuser

    # Kiểm tra quyền truy cập
    if not is_superuser:
        if not hasattr(request.user, 'profile') or not request.user.profile:
            messages.error(request, "Bạn không có quyền.")
            return redirect('user:user_list')
        
        user_role_permissions = request.user.profile.role.permissions.values_list('codename', flat=True)
        if 'can_detail_user' not in user_role_permissions:
            messages.error(request, "Bạn không có quyền.")
            return redirect('user:user_list')

    # Lấy thông tin tiến trình học tập
    course_progress = UserCourseProgress.objects.filter(user=user)
    courses_with_progress = [
        {
            'course': progress.course,
            'progress_percentage': progress.progress_percentage
        }
        for progress in course_progress
    ]

    # Lấy các khóa học đã đăng ký
    enrollments = Enrollment.objects.filter(student=user)

    # Xác định vai trò của người dùng là sinh viên hay giảng viên
    role = getattr(user.profile.role, 'role_name', None) if hasattr(user, 'profile') else None
    is_student = role == 'Student'
    is_instructor = role == 'Instructor'  # Kiểm tra nếu người dùng là giảng viên

    # Thông tin dành cho sinh viên
    student_code = "N/A"
    quiz_results = []
    if is_student:
        try:
            student = Student.objects.get(user=user)
            student_code = student.student_code if student.student_code else "N/A"
            quiz_results = StudentQuizAttempt.objects.filter(user=user).select_related('quiz')
        except Student.DoesNotExist:
            student_code = "N/A"

    # Thông tin dành cho giảng viên
    taught_courses = []
    if is_instructor:
        instructor = Instructor.objects.get(user=user)
        taught_courses = Course.objects.filter(instructor=user)  # Sử dụng instructor.user thay vì user
    # Nhật ký hoạt động
    two_days_ago = timezone.now() - timedelta(days=2)
    activity_logs = UserActivityLog.objects.filter(user=user, activity_timestamp__gte=two_days_ago).order_by('-activity_timestamp')

    paginator = Paginator(activity_logs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Trả về template với context
    return render(request, 'user_detail.html', {
        'user': user,
        'courses_with_progress': courses_with_progress,
        'enrollments': enrollments,
        'is_student': is_student,
        'is_instructor': is_instructor,
        'is_superuser': is_superuser,
        'student_code': student_code,
        'quiz_results': quiz_results,
        'taught_courses': taught_courses,
        'activity_logs': activity_logs,
        'page_obj': page_obj,
    })

@login_required
def user_add(request):
    is_superuser = request.user.is_superuser

    # Kiểm tra profile của người dùng
    if not is_superuser and (not hasattr(request.user, 'profile') or request.user.profile is None):
        messages.error(request, "Bạn không có quyền.")  # Thông báo lỗi
        return redirect('user:user_list')  # Chuyển hướng đến danh sách người dùng
    
    # Lấy quyền hạn của người dùng
    user_role_permissions = request.user.profile.role.permissions.values_list('codename', flat=True) if not is_superuser else []

    if 'can_add_user' not in user_role_permissions and not is_superuser:
        messages.error(request, "Bạn không có quyền.")  # Thông báo lỗi
        return redirect('user:user_list')  # Chuyển hướng đến danh sách người dùng

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

            # Tạo Student nếu role là 'Student'
            if profile.role.role_name == 'Student':
                try:
                    student_code = form.cleaned_data.get('student_code')  
                    student = Student(user=user, student_code=student_code)
                    student.save()
                    profile.student = student
                    profile.save()
                except Exception as e:
                    print('Error saving Student:', e)

            # Tạo Instructor nếu role là 'Instructor'
            if profile.role.role_name == 'Instructor':
                try:
                    instructor = Instructor(user=user)
                    instructor.save()
                    profile.instructor = instructor
                    profile.save()
                except Exception as e:
                    print('Error saving Instructor:', e)

            # Thiết lập các chương trình đào tạo
            training_programs = form.cleaned_data.get('training_programs')
            if training_programs:
                user.training_programs.set(training_programs)

            messages.success(request, "Người dùng đã được thêm thành công!")
            return redirect('user:user_list')
        else:
            print('Invalid form')
            print(form.errors)
    else:
        form = UserForm()

    return render(request, 'user_form.html', {'form': form, 'is_superuser': is_superuser})



@login_required
def user_edit(request, pk):
    is_superuser = request.user.is_superuser
    user = get_object_or_404(User, pk=pk)

    # Kiểm tra profile của người dùng
    if not is_superuser and (not hasattr(request.user, 'profile') or request.user.profile is None):
        messages.error(request, "Bạn không có quyền.")
        return redirect('user:user_list')

    user_role_permissions = request.user.profile.role.permissions.values_list('codename', flat=True) if not is_superuser else []

    if 'can_edit_user' not in user_role_permissions and request.user.pk != user.pk and not is_superuser:
        messages.error(request, "Bạn không có quyền chỉnh sửa người dùng này.")
        return redirect('user:user_list')

    profile, created = Profile.objects.get_or_create(user=user)
    old_role = profile.role

    student_code = None
    if profile.role and profile.role.role_name == 'Student':
        try:
            student = Student.objects.get(user=user)
            student_code = student.student_code
        except Student.DoesNotExist:
            pass

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)

        if form.is_valid():  # Đảm bảo form hợp lệ trước khi xử lý
            # Cập nhật các thông tin người dùng
            user.username = form.cleaned_data.get('username', user.username)
            user.first_name = form.cleaned_data.get('first_name', user.first_name)
            user.last_name = form.cleaned_data.get('last_name', user.last_name)
            user.email = form.cleaned_data.get('email', user.email)

            # Kiểm tra và cập nhật mật khẩu nếu có
            new_password = form.cleaned_data.get('password1')
            if new_password:
                user.set_password(new_password)
                try:
                    # Lấy hoặc tạo bản ghi thay đổi mật khẩu cho người dùng
                    password_change_record = PasswordChangeRecord.get_or_create_record(user)

                    # Cập nhật số lần thay đổi mật khẩu
                    password_change_record.update_change_count()

                    print(f"Password change count updated: {password_change_record.change_count}")  # Debugging print
                except Exception as e:
                    print(f"Error updating password change record: {e}")  # Debugging print
            user.save()

            # Kiểm tra và thay đổi vai trò nếu cần
            new_role_name = form.cleaned_data.get('role')  # lấy tên vai trò
            if new_role_name and new_role_name != old_role.role_name:  # so sánh với tên vai trò cũ
                try:
                    # Truy vấn Role dựa trên tên vai trò
                    new_role = Role.objects.get(role_name = new_role_name)
                    profile.role = new_role
                except Role.DoesNotExist:
                    messages.error(request, "Vai trò không tồn tại.")
                    return redirect('user:user_list')

            profile.profile_picture_url = form.cleaned_data.get('profile_picture_url', profile.profile_picture_url)
            profile.bio = form.cleaned_data.get('bio', profile.bio)
            profile.interests = form.cleaned_data.get('interests', profile.interests)
            profile.learning_style = form.cleaned_data.get('learning_style', profile.learning_style)
            profile.preferred_language = form.cleaned_data.get('preferred_language', profile.preferred_language)
            # Xử lý nếu người dùng có vai trò là Student
            if profile.role and profile.role.role_name == 'Student':
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

            # Xử lý nếu người dùng có vai trò là Instructor
            if profile.role and profile.role.role_name == 'Instructor':
                instructor, created = Instructor.objects.get_or_create(user=user)
                instructor.save()
                profile.instructor = instructor
            else:
                try:
                    instructor = Instructor.objects.get(user=user)
                    instructor.delete()
                    profile.instructor = None
                except Instructor.DoesNotExist:
                    pass

            profile.save()

            if new_password and request.user.pk == user.pk:
                logout(request)  # Đăng xuất người dùng
                messages.success(request, "Mật khẩu của bạn đã được thay đổi. Vui lòng đăng nhập lại.")
                return redirect('main:login')  # Chuyển hướng đến trang đăng nhập

            # Cập nhật session nếu người dùng thay đổi chính thông tin của mình
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
            return redirect('user:user_edit', pk=user.pk)
        else:
            messages.error(request, "Vui lòng sửa các lỗi bên dưới.")
    else:
        form = UserForm(instance=user)

    # Thiết lập giá trị khởi tạo cho các trường
    form.fields['bio'].initial = profile.bio
    form.fields['interests'].initial = profile.interests
    form.fields['learning_style'].initial = profile.learning_style
    form.fields['preferred_language'].initial = profile.preferred_language
    form.fields['profile_picture_url'].initial = profile.profile_picture_url
    form.fields['role'].initial = profile.role.id if profile.role else None

    # Nếu người dùng không phải là superuser, Manager hoặc chính họ, đặt thuộc tính readonly cho trường 'role'
    if not (is_superuser or (request.user.profile and request.user.profile.role and request.user.profile.role.role_name == 'Manager' and request.user.pk == user.pk)):
        form.fields['role'].widget.attrs['readonly'] = True


    # Hiển thị trường student_code không bị ẩn
    form.fields['student_code'].initial = student_code if profile.role and profile.role.role_name == 'Student' else ''

    return render(request, 'user_form.html', {'form': form, 'user': user})


def user_delete(request):
    is_superuser = request.user.is_superuser

    if not is_superuser and 'can_delete_user' not in request.user.profile.role.permissions.values_list('codename', flat=True):
        messages.error(request, "Bạn không có quyền xóa người dùng.")
        return redirect('user:user_list')

    if request.method == "POST":
        user_ids = request.POST.getlist('selected_users')
        origin = request.POST.get('origin', 'user_list')

        if not user_ids:
            messages.error(request, "Không có người dùng nào được chọn để xóa.")
            return redirect(f'user:{origin}')

        deleted_users = []

        users_to_delete = User.objects.filter(pk__in=user_ids, is_superuser=False)

        for user in users_to_delete:
            deleted_users.append(user.username)
            user.delete()

        if deleted_users:
            messages.success(request, f"Các người dùng {', '.join(deleted_users)} đã được xóa thành công.")
        else:
            messages.error(request, "Không có người dùng nào được xóa.")

    return redirect(f'user:{origin}')



@login_required
def export_users(request):
    is_superuser = request.user.is_superuser

    # Kiểm tra quyền của người dùng
    if not is_superuser and (not hasattr(request.user, 'profile') or request.user.profile is None):
        messages.error(request, "Bạn không có quyền.")
        return redirect('user:user_list')

    user_role_permissions = request.user.profile.role.permissions.values_list('codename', flat=True) if not is_superuser else []

    if 'can_export_users' not in user_role_permissions and not is_superuser:
        messages.error(request, "Bạn không có quyền xuất dữ liệu người dùng.")
        return redirect('user:user_list')

    # Lấy định dạng file từ request (mặc định là xlsx)
    export_format = request.GET.get('format', 'xlsx').lower()

    # Kiểm tra định dạng hợp lệ
    valid_formats = ['csv', 'json', 'yaml', 'tsv', 'xlsx']
    if export_format not in valid_formats:
      return JsonResponse({"error": "Invalid format specified"}, status=400)

    # Tạo resource và dataset
    resource = UserProfileResource()
    selected_role = request.GET.get('role', '').strip()

    # Lọc người dùng theo role nếu cần
    if selected_role:
        users = User.objects.exclude(is_superuser=True).filter(profile__role__role_name=selected_role)
    else:
        users = User.objects.exclude(is_superuser=True)

    dataset = resource.export(users)

    # Xử lý các định dạng khác nhau
    formats = {
        'csv': (CSV(), 'text/csv'),
        'json': (JSON(), 'application/json'),
        'yaml': (YAML(), 'application/x-yaml'),
        'tsv': (TSV(), 'text/tab-separated-values'),
        'xlsx': (XLSX(), XLSX().get_content_type()),
    }

    dataset_format, content_type = formats[export_format]
    file_extension = export_format

    response = HttpResponse(content_type=content_type)
    safe_role = "".join(c for c in selected_role if c.isalnum() or c in ['_', '-'])
    filename = f'{safe_role}.{file_extension}' if selected_role else f'users.{file_extension}'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    response.write(dataset_format.export_data(dataset))
    
    return response


@csrf_protect
@login_required
def import_users(request):
    is_superuser = request.user.is_superuser

    # Check user permissions
    if not is_superuser and (not hasattr(request.user, 'profile') or request.user.profile is None):
        messages.error(request, "You do not have permission.")
        return redirect('user:user_list')

    user_role_permissions = request.user.profile.role.permissions.values_list('codename', flat=True) if not is_superuser else []

    if 'can_import_users' not in user_role_permissions and not is_superuser:
        messages.error(request, "You do not have permission to import user data.")
        return redirect('user:user_list')

    resource = UserProfileResource()

    if request.method == 'POST':
        # Get the uploaded file via form (drag-and-drop or file select)
        uploaded_file = request.FILES.get('file')

        # Check if file is uploaded
        if not isinstance(uploaded_file, UploadedFile):
            messages.error(request, "No file found to import.")
            return redirect('user:user_list')

        if uploaded_file.size == 0:  # Check if the file is empty
            messages.error(request, "The file cannot be empty.")
            return redirect('user:user_list')

        file_format = uploaded_file.name.split('.')[-1].lower()
        dataset = Dataset()

        # Handle file formats
        formats = {
            'csv': lambda: dataset.load(uploaded_file.read().decode('utf-8'), format='csv'),
            'json': lambda: dataset.load(uploaded_file.read().decode('utf-8'), format='json'),
            'yaml': lambda: dataset.load(uploaded_file.read().decode('utf-8'), format='yaml'),
            'tsv': lambda: dataset.load(uploaded_file.read().decode('utf-8'), format='tsv'),
            'xlsx': lambda: dataset.load(uploaded_file.read(), format='xlsx'),
        }

        try:
            if file_format in formats:
                formats[file_format]()  # Call the respective format handler
            else:
                messages.error(request, "Invalid file format. Supported formats: csv, json, yaml, tsv, xlsx.")
                return redirect('user:user_list')
        except Exception as e:
            messages.error(request, f"Error reading file: {e}")
            return redirect('user:user_list')

        # Check and import data
        result = resource.import_data(dataset, dry_run=True)

        if result.has_validation_errors():
            print(f"Validation Errors: {result.errors}")
            invalid_rows = result.invalid_rows
            error_messages = [f"Error at row {row.number}: {row.error}" for row in invalid_rows]
            messages.error(request, "There were errors importing users:\n" + "\n".join(error_messages))
        else:
            resource.import_data(dataset, dry_run=False)
            messages.success(request, "Users have been successfully imported!")

        return redirect('user:user_list')

    messages.error(request, "Unable to import users.")
    return redirect('user:user_list')


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


@login_required
def instructor_list(request):
    query = request.GET.get('q', '')
    instructors = Instructor.objects.all()
    form = ExcelImportForm()

    if query:
        instructors = instructors.filter(
            Q(user__username__icontains=query)
        )

    instructors = instructors.order_by('user__username')

    paginator = Paginator(instructors, 5)
    page = request.GET.get('page', 1)

    try:
        instructors = paginator.page(page)
    except PageNotAnInteger:
        instructors = paginator.page(1)
    except EmptyPage:
        instructors = paginator.page(paginator.num_pages)
    return render(request, 'instructor_list.html', {
        'instructors': instructors,
        'query': query,
        'form': form,
        'page_obj': instructors
    })