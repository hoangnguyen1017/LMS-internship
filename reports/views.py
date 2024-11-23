from django.shortcuts import render
from course.models import Course, Enrollment, Session, Completion, Tag, CourseMaterial, UserCourseProgress
from django.db.models import Count
from module_group.models import ModuleGroup
from user.models import User, Student, Profile
from collections import Counter
from django.http import JsonResponse
from activity.models import UserActivityLog
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.dateformat import DateFormat
from django.shortcuts import render
import plotly.graph_objs as go
from django.utils.timezone import make_aware
from progress_notification.models import ProgressNotification
from django.core.mail import send_mail
from django.conf import settings

@login_required
def report_dashboard(request):
    module_groups = ModuleGroup.objects.all()
    return render(request, 'reports/dashboard_report.html', 
    {
        'module_groups': module_groups,
    })


@login_required
def course_overview_report(request):
    module_groups = ModuleGroup.objects.all()
    courses = Course.objects.all()
    return render(request, 'reports/course/course_overview_report.html', 
    {'courses': courses, 'module_groups': module_groups,
    })

@login_required
def student_enrollment_report(request):
    enrollments = Enrollment.objects.select_related('student', 'course').all()
    return render(request, 'reports/student/student_enrollment_report.html', {'enrollments': enrollments})


@login_required
def course_completion_report(request):
    # Lấy tất cả các khóa học
    courses = Course.objects.all()
    course_progress = {}

    for course in courses:
        # Kiểm tra các lượt đăng ký cho khóa học hiện tại
        enrollments = Enrollment.objects.filter(course=course)
        
        # Chỉ thêm khóa học vào course_progress nếu có ít nhất một người tham gia
        if enrollments.exists():
            course_progress[course] = {}
            
            # Lặp qua tất cả các lượt đăng ký khóa học
            for enrollment in enrollments:
                user = enrollment.student
                progress_percent = course.get_completion_percent(user)  # Lấy tiến độ hiện tại của người dùng
                
                # Lấy ngày tham gia khóa học
                enrolled_at = enrollment.date_enrolled
                
                # Lấy tiến độ trước đó (nếu có)
                last_progress = UserCourseProgress.objects.filter(user=user, course=course).last()
                
                if last_progress:
                    last_progress_percent = float(last_progress.progress_percentage)
                    progress_change = round(progress_percent - last_progress_percent, 2)
                    
                    # Chỉ cập nhật 'last_accessed' và 'progress_percentage' nếu có sự thay đổi tiến độ
                    if progress_change != 0:
                        # Cập nhật dữ liệu mới (chỉ khi có sự thay đổi)
                        last_progress.progress_percentage = progress_percent
                        last_progress.last_accessed = timezone.now()  # Cập nhật thời gian thay đổi
                        last_progress.save()
                        
                        # Cập nhật last_changed_at cho hiển thị
                        last_changed_at = last_progress.last_accessed
                    else:
                        last_changed_at = last_progress.last_accessed  # Không thay đổi, giữ lại giá trị cũ
                else:
                    # Nếu không có tiến độ trước đó, tạo mới tiến độ
                    progress_change = 0  # Đặt về 0 nếu chưa có tiến độ trước đó
                    last_changed_at = None  # Không có lần thay đổi nào

                    # Tạo mới tiến độ
                    UserCourseProgress.objects.create(
                        user=user,
                        course=course,
                        progress_percentage=progress_percent,
                        last_accessed=timezone.now()
                    )

                # Thêm dữ liệu tiến độ vào dictionary
                course_progress[course][user] = {
                    'progress': progress_percent,
                    'enrolled_at': enrolled_at,
                    'progress_change': progress_change,
                    'last_changed_at': last_changed_at,  # Chỉ cập nhật last_changed_at nếu có sự thay đổi
                }
    
    # Trả về dữ liệu cho template
    return render(request, 'reports/course/course_completion_report.html', {'course_progress': course_progress})


@login_required
def session_overview_report(request):
    sessions = Session.objects.select_related('course').all()
    return render(request, 'reports/assessment/session_overview_report.html', {'sessions': sessions})

@login_required
def material_usage_report(request):
    completions = Completion.objects.select_related('session', 'material', 'user').all()
    return render(request, 'reports/course/material_usage_report.html', {'completions': completions})

@login_required
def enrollment_trends_report(request):
    today = timezone.now()
    
    # Querying enrollments and annotating with count
    enrollments = (
        Enrollment.objects
        .filter(date_enrolled__month=today.month)
        .values('course__course_name')  # Get the course name by following the ForeignKey relationship
        .annotate(count=Count('id'))
    )

    return render(request, 'reports/assessment/enrollment_trends_report.html', {'enrollments': enrollments})
@login_required
def material_type_distribution_report(request):
    materials = CourseMaterial.objects.values('material_type').annotate(count=Count('id'))
    return render(request, 'reports/course/material_type_distribution_report.html', {'materials': materials})

@login_required
def tag_report(request):
    tags = Tag.objects.annotate(course_count=Count('courses'))
    return render(request, 'reports/assessment/tag_report.html', {'tags': tags})

@login_required
def instructor_performance_report(request):
    instructors = Course.objects.values('instructor').annotate(enrollment_count=Count('enrollment')).order_by('-enrollment_count')
    return render(request, 'reports/assessment/instructor_performance_report.html', {'instructors': instructors})



