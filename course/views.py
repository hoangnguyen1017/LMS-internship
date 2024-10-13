from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, UserCourseProgress, User
from .forms import CourseForm, UserCourseProgressForm
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def course_list(request):
    query = request.GET.get('q', '')
    created_by_filter = request.GET.get('created_by', '')

    courses = Course.objects.all()
    users = User.objects.filter(course__isnull=False).distinct()  # Get users who have created courses

    # Apply search filters if provided

    if query and created_by_filter:
        courses = courses.filter(
            Q(course_name__icontains=query),
            created_by_id=created_by_filter
        )
    elif query: 
        courses = courses.filter(course_name__icontains=query)
    elif created_by_filter: 
        courses = courses.filter(created_by_id=created_by_filter)

    not_found = not courses.exists()

    # Pagination
    paginator = Paginator(courses, 5)  # Show 5 courses per page
    page_number = request.GET.get('page', 1)

    try:
        courses_page = paginator.page(page_number)
    except PageNotAnInteger:
        courses_page = paginator.page(1)
    except EmptyPage:
        courses_page = paginator.page(paginator.num_pages)

    return render(request, 'course_list.html', {
        'courses': courses_page,  # Use paginated courses
        'query': query,
        'created_by_filter': created_by_filter,
        'users': users,  # Pass the list of users to the template
        'not_found': not_found,  # Check if any courses were found

    })




def course_detail(request, pk):
    """Hiển thị chi tiết một khóa học và tiến độ của người dùng trong khóa học đó."""
    course = get_object_or_404(Course, pk=pk)
    
    # Lấy danh sách tiến độ của người dùng cho khóa học này
    user_progress = UserCourseProgress.objects.filter(course=course)
    
    # Lọc theo tên người dùng (nếu có tìm kiếm)
    query = request.GET.get('q', '')
    if query:
        user_progress = user_progress.filter(user__username__icontains=query)

    # Lọc theo phần trăm tiến độ (nếu có lựa chọn)
    progress_filter = request.GET.get('progress_filter', '')
    if progress_filter == 'under_50':
        user_progress = user_progress.filter(progress_percentage__lt=50)
    elif progress_filter == 'under_90':
        user_progress = user_progress.filter(progress_percentage__lt=90)
    elif progress_filter == '100':
        user_progress = user_progress.filter(progress_percentage=100)
    
    return render(request, 'course_detail.html', {
        'course': course,
        'user_progress': user_progress,
        'query': query,
        'progress_filter': progress_filter,
    })


def course_add(request):
    if request.method == 'POST':
        course_form = CourseForm(request.POST)
        if course_form.is_valid():
            course_form.save()
            return redirect('course:course_list')  # Redirect after saving
    else:
        course_form = CourseForm()
    
    return render(request, 'course_form.html', {'course_form': course_form})

def course_edit(request, pk):
    """Chỉnh sửa thông tin của một khóa học cụ thể."""
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        course_form = CourseForm(request.POST, instance=course)
        if course_form.is_valid():
            course_form.save()
            return redirect('course:course_list')
    else:
        course_form = CourseForm(instance=course)
    
    return render(request, 'course_form.html', {'course_form': course_form})

def course_delete(request, pk):
    """Xóa một khóa học cụ thể."""
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        course.delete()
        return redirect('course:course_list')  # Chuyển hướng về trang danh sách khóa học sau khi xóa
    
    return render(request, 'course_confirm_delete.html', {'course': course})

def create_progress(request, course_id):
    """Tạo tiến độ của người dùng trong một khóa học cụ thể."""
    course = get_object_or_404(Course, pk=course_id)  # Lấy thông tin khóa học
    users = User.objects.all()  # Lấy danh sách người dùng

    if request.method == 'POST':
        progress_form = UserCourseProgressForm(request.POST)
        if progress_form.is_valid():
            user = progress_form.cleaned_data['user']
            progress_percentage = progress_form.cleaned_data['progress_percentage']
            # Tạo mới tiến độ của người dùng trong khóa học
            UserCourseProgress.objects.create(
                user=user,
                course=course,
                progress_percentage=progress_percentage
            )
            messages.success(request, 'Progress created successfully.')
            return redirect('course:course_detail', pk=course_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        progress_form = UserCourseProgressForm()

    # Truyền biến course và users đến template
    return render(request, 'create_progress.html', {'form': progress_form, 'course': course, 'users': users})

def update_progress_percentage(request, course_id, user_id):
    """Cập nhật tiến độ của người dùng trong một khóa học cụ thể."""
    course = get_object_or_404(Course, pk=course_id)
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        progress_percentage = request.POST.get('progress_percentage')

        # Cập nhật hoặc tạo mới tiến độ của người dùng trong khóa học
        progress, created = UserCourseProgress.objects.update_or_create(
            user=user, course=course,
            defaults={'progress_percentage': progress_percentage, 'last_accessed': timezone.now()}
        )
        
        if created:
            print("Progress created successfully.")
        else:
            print("Progress updated successfully.")
        
        return redirect('course:course_detail', pk=course_id)
    
    # Lấy thông tin hiện tại của tiến độ người dùng
    progress = UserCourseProgress.objects.filter(user=user, course=course).first()
    
    return render(request, 'update_progress_percentage.html', {
        'course': course,
        'user': user,
        'progress': progress
    })