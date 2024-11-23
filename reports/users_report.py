from django.shortcuts import render
from course.models import Enrollment, Completion, UserCourseProgress
from django.db.models import Count
from module_group.models import ModuleGroup
from user.models import User, Student, Profile
from django.http import JsonResponse
from activity.models import UserActivityLog
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from progress_notification.models import ProgressNotification
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now
from django.db.models import Count, Q, Max
from activity.models import UserActivityLog
from quiz.models import StudentQuizAttempt
from assessments.models import StudentAssessmentAttempt
from role.models import Role, RoleModule
from django.core.paginator import Paginator
from decimal import Decimal
from functools import reduce
from main.models import PasswordChangeRecord
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import redirect


@login_required
def user_duration_login(request):
    user = request.user
    activity_logs = UserActivityLog.objects.filter(user=user).order_by('activity_timestamp')

    login_times = []
    logout_times = []

    # Lấy thời gian đăng nhập và đăng xuất
    for log in activity_logs:
        if log.activity_type == 'login' and log.activity_details == 'User logged in.':
            login_times.append(log.activity_timestamp)
        elif log.activity_type == 'logout':
            logout_times.append(log.activity_timestamp)

    # Tính toán thời gian phiên làm việc
    session_durations = []
    for login_time in login_times:
        # Tìm lần đăng xuất gần nhất sau thời gian đăng nhập
        logout_time = next((lt for lt in logout_times if lt > login_time), None)
        if logout_time:
            # Tính toán thời gian phiên
            duration = logout_time - login_time
            
            # Định dạng lại thời gian phiên thành chuỗi "X days, Y hours, Z minutes"
            days, seconds = duration.days, duration.seconds
            hours = seconds // 3600
            minutes = (seconds // 60) % 60
            
            formatted_duration = f"{days} days, {hours} hours, {minutes} minutes"
            total_minutes = duration.total_seconds() // 60  # Tính tổng phút
            
            session_durations.append({
                'login_time': login_time,
                'logout_time': logout_time,
                'duration': formatted_duration,  # Lưu trữ dưới dạng chuỗi
                'total_minutes': total_minutes,  # Lưu trữ tổng phút
            })
    session_durations = session_durations[-10:]
    return render(request, 'reports/user/user_duration_login.html', {
        'session_durations': session_durations,
    })

@login_required
def login_frequency_report(request):
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')

    today = timezone.now()
    start_date = today - timedelta(days=30)

    if from_date:
        from_date_parsed = parse_date(from_date)
        if from_date_parsed:
            start_date = from_date_parsed

    if to_date:
        to_date_parsed = parse_date(to_date)
        if to_date_parsed:
            end_date = to_date_parsed
        else:
            end_date = today
    else:
        end_date = today

    # Tổng hợp dữ liệu đăng nhập theo ngày trong khoảng thời gian đã chọn
    login_data = (
        UserActivityLog.objects.filter(
            user=request.user,
            activity_type='login',
            activity_timestamp__range=[start_date, end_date]
        )
        .annotate(day=TruncDate('activity_timestamp'))
        .values('day')
        .annotate(login_count=Count('log_id'))
        .order_by('day')
    )

    times = [entry['day'].strftime('%Y-%m-%d') for entry in login_data]
    counts = [entry['login_count'] for entry in login_data]

    title = "Login frequency in the last 30 days"
    back_to_month = False

    return render(request, 'reports/user/login_frequency_report.html', {
        'times': times,
        'counts': counts,
        'title': title,
        'login_frequency': login_data,
        'from_date': from_date,
        'to_date': to_date,
        'back_to_month': back_to_month,
    })


@login_required
def user_statistics_report(request):
    module_groups = ModuleGroup.objects.all()
    today = timezone.now().date()

    # Lấy tham số tuần (week_offset) từ URL, mặc định là tuần hiện tại
    week_offset = int(request.GET.get('week_offset', 0))  # Nếu không có tham số week_offset, mặc định là tuần này

    # Tính toán ngày bắt đầu và kết thúc của tuần dựa trên week_offset
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)  # Thứ Hai
    end_of_week = start_of_week + timedelta(days=6)  # Chủ Nhật

    # Lọc các hoạt động đăng nhập trong tuần đã chọn
    daily_login_counts = (
        UserActivityLog.objects.filter(
            activity_type='login',
            activity_timestamp__gte=start_of_week,
            activity_timestamp__lte=end_of_week,
            user__is_superuser=False
        )
        .annotate(login_date=TruncDate('activity_timestamp'))
        .values('login_date')
        .annotate(user_count=Count('user', distinct=True))
        .order_by('login_date')
    )

    # Lấy tất cả các ngày trong tuần từ Thứ Hai đến Chủ Nhật
    all_dates_in_week = [start_of_week + timedelta(days=i) for i in range(7)]
    
    # Tạo danh sách đầy đủ các ngày, kết hợp với số lượng đăng nhập
    daily_login_dict = {entry['login_date']: entry['user_count'] for entry in daily_login_counts}
    login_dates = [date.strftime('%Y-%m-%d') for date in all_dates_in_week]
    user_counts = [daily_login_dict.get(date, 0) for date in all_dates_in_week]

    # Kiểm tra xem người dùng có chọn ngày cụ thể không
    selected_login_date = request.GET.get('login_date')
    users = []
    if selected_login_date:
        users = User.objects.filter(
            useractivitylog__activity_type='login',
            useractivitylog__activity_timestamp__date=selected_login_date,
            is_superuser=False
        ).distinct()

    # Truyền lại dữ liệu cho template
    return render(request, 'reports/user/user_statistics_report.html', {
        'module_groups': module_groups,
        'login_dates': login_dates,
        'user_counts': user_counts,
        'users': users,
        'week_offset': week_offset,  # Truyền week_offset để xác định tuần
        'selected_login_date': selected_login_date  # Truyền ngày đã chọn
    })

def student_id_report(request):
    students = Student.objects.all()

    # Lọc theo student_group nếu có từ khóa tìm kiếm
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(student_code__icontains=search_query)

    # Phân trang
    paginator = Paginator(students, 30)  # 10 sinh viên mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Tạo bảng tổng kết
    student_cohorts = {}
    for student in students:
        if student.student_code and student.student_code.startswith("SE"):
            cohort = student.student_code[2:4]
            student_cohorts.setdefault(cohort, []).append(student)

    labels = [f"SE{cohort}" for cohort in student_cohorts.keys()]  # Thêm 'SE' vào nhãn
    data = [len(students) for students in student_cohorts.values()]
    total_students = sum(data)

    cohort_summary = [
        {
            'label': label,
            'count': count,
            'percentage': (count / total_students) * 100 if total_students > 0 else 0
        }
        for label, count in zip(labels, data)
    ]

    context = {
        'labels': labels,
        'data': data,
        'cohort_summary': cohort_summary,
        'page_obj': page_obj,
        'search_query': search_query,
    }

    return render(request, 'reports/user/student_id_report.html', context)

from django.http import JsonResponse

def student_group_details(request):
    group_name = request.GET.get('group')  # Nhận nhóm sinh viên từ yêu cầu Ajax
    students = Student.objects.filter(group=group_name)  # Lấy sinh viên theo nhóm

    student_data = []
    for student in students:
        student_data.append({
            'name': student.name,
            'code': student.student_code,
        })

    return JsonResponse({'students': student_data})  # Trả về dữ liệu JSON cho Ajax


def get_students_by_cohort(request, cohort):
    """Lấy danh sách sinh viên theo cohort cho yêu cầu AJAX"""
    students = Student.objects.filter(student_code__startswith=f"SE{cohort}")
    student_data = [{"name": student.user.username, "student_code": student.student_code} for student in students]
    return JsonResponse(student_data, safe=False)

def role_report(request):
    # Lấy tất cả các vai trò
    roles = Role.objects.all()

    # Lấy số lượng người dùng theo vai trò
    role_counts = Profile.objects.values('role__role_name').annotate(user_count=Count('user')).order_by('role__role_name')

    # Lấy các module của vai trò và số lượng người dùng cho mỗi vai trò
    role_modules = {}
    for role in roles:
        # Lấy các module của mỗi vai trò thông qua RoleModule
        role_modules_queryset = RoleModule.objects.filter(role=role)
        
        # Lấy tất cả các module từ RoleModule
        modules = [role_module.module.module_name for role_module in role_modules_queryset]
        
        # Lấy số lượng người dùng có vai trò này
        user_count = Profile.objects.filter(role=role).count()

        role_modules[role.role_name] = {
            'modules': modules,  # Cập nhật module từ RoleModule
            'user_count': user_count
        }

    # Đưa tất cả thông tin vào context
    context = {
        'roles': roles,
        'role_counts': role_counts,
        'role_modules': role_modules,  # Cập nhật context
    }

    return render(request, 'reports/user/role_report.html', context)


@login_required
def user_overview_report(request):
    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('filter', '')

    # Dữ liệu thống kê tóm tắt (áp dụng cho tất cả người dùng trừ superusers)
    all_users = User.objects.exclude(is_superuser=True).prefetch_related('profile__role', 'department')
    total_users = all_users.count()  # Tính tổng số người dùng

    # Danh sách các trường cần kiểm tra
    profile_fields = [
        'profile_picture_url', 'bio', 'interests', 'learning_style', 'preferred_language'
    ]

    # Tạo điều kiện Q() cho các trường cần kiểm tra
    incomplete_condition = reduce(
        lambda acc, field: acc | Q(**{f'profile__{field}__isnull': True}) | Q(**{f'profile__{field}': ''}),
        profile_fields,
        Q()
    )

    complete_condition = ~incomplete_condition  # Điều kiện ngược lại cho profile hoàn chỉnh

    # Lọc các profile hoàn thành và chưa hoàn thành
    complete_profiles = all_users.filter(complete_condition)
    incomplete_profiles = all_users.filter(incomplete_condition)

    profile_completion_percentage = (complete_profiles.count() / total_users) * 100 if total_users else 0

    # Thống kê đăng nhập gần đây
    recent_logins = all_users.filter(last_login__gte=timezone.now() - timedelta(days=30))
    active_user_percentage = (recent_logins.count() / total_users) * 100 if total_users else 0

    # Thống kê theo vai trò (role) và bộ phận (department)
    role_summary = {
        role.role_name: all_users.filter(profile__role=role).count()
        for role in Role.objects.all()
    }

    department_summary = all_users.filter(department__isnull=False).values('department__name').annotate(department_count=Count('department')).order_by('department__name')
    course_summary = all_users.filter(enrollments__isnull=False).values('enrollments__course__course_name').annotate(course_count=Count('enrollments')).order_by('enrollments__course__course_name')

    # Lọc danh sách người dùng dựa trên từ khóa tìm kiếm và bộ lọc chi tiết
    users = all_users.filter(
        Q(username__icontains=search_query) |
        Q(first_name__icontains=search_query) |
        Q(last_name__icontains=search_query) |
        Q(email__icontains=search_query) |
        Q(profile__role__role_name__icontains=search_query)
    )

    # Áp dụng bộ lọc chi tiết nếu có
    if filter_type == 'incomplete_profiles':
        users = users.filter(incomplete_condition)
    elif filter_type == 'complete_profiles':
        users = users.filter(complete_condition)
    elif filter_type == 'recent_logins':
        users = users.filter(last_login__gte=timezone.now() - timedelta(days=30))
    elif filter_type.startswith('role_'):
        role_name = filter_type.split('_', 1)[1].replace('-', ' ')
        users = users.filter(profile__role__role_name__iexact=role_name)
    elif filter_type.startswith('department_'):
        department_name = filter_type.split('_', 1)[1].replace('-', ' ')
        users = users.filter(department__name__iexact=department_name)
    elif filter_type.startswith('course_'):
        course_name = filter_type.split('_', 1)[1].replace('-', ' ')
        users = users.filter(enrollments__course__course_name__iexact=course_name)

    # Phân trang danh sách người dùng sau khi đã áp dụng tìm kiếm và lọc
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_users = paginator.get_page(page_number)
    # Tạo lại URL để giữ lại tham số lọc và tìm kiếm khi phân trang
    page_query = f"&search={search_query}" if search_query else ""
    page_query += f"&filter={filter_type}" if filter_type else ""

    return render(request, 'reports/user/user_overview_report.html', {
        'users': page_users,
        'search_query': search_query,
        'filter_type': filter_type,
        'role_summary': role_summary,
        'incomplete_profiles': incomplete_profiles,
        'profile_completion_percentage': profile_completion_percentage,
        'active_user_percentage': active_user_percentage,
        'department_summary': department_summary,
        'course_summary': course_summary,
        'page_query': page_query,  # Truyền tham số lọc và tìm kiếm
    })



@login_required
def user_progress_report(request):
    user = request.user
    progress = Completion.objects.filter(user=user).select_related('session', 'material')
    return render(request, 'reports/student/user_progress_report.html', {'progress': progress})



def engagement_activity_report(request):
    today = now().date()
    
    # Lấy tham số thời gian từ URL (tuần hoặc tháng)
    period = request.GET.get('period', 'week')  # Mặc định là tuần nếu không có tham số 'period'
    
    if period == 'week':
        start_of_period = today - timedelta(days=today.weekday())  # Bắt đầu tuần (Thứ Hai)
        end_of_period = start_of_period + timedelta(days=6)  # Kết thúc tuần (Chủ Nhật)
        period_label = f"{start_of_period.strftime('%d/%m')} - {end_of_period.strftime('%d/%m')}"
    elif period == 'month':
        # Tính ngày bắt đầu của tháng
        start_of_period = today.replace(day=1)
        # Tính ngày kết thúc của tháng
        if today.month == 12:
            end_of_period = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_period = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        period_label = f"{start_of_period.strftime('%d/%m')} - {end_of_period.strftime('%d/%m')}"
    else:
        start_of_period = today - timedelta(days=today.weekday())  # Mặc định là tuần nếu không hợp lệ
        end_of_period = start_of_period + timedelta(days=6)
        period_label = f"{start_of_period.strftime('%d/%m')} - {end_of_period.strftime('%d/%m')}"

    # Lấy số lượng người dùng hoạt động trong khoảng thời gian đã chọn
    active_users = UserActivityLog.objects.filter(
        activity_timestamp__gte=start_of_period,
        activity_timestamp__lte=end_of_period
    ).values('user__username', 'user__profile__role__role_name').annotate(
        active_user_count=Count('log_id')
    ).order_by('user__username')

    # Tần suất đăng nhập hàng tuần hoặc tháng và lần đăng nhập cuối cùng
    login_frequency = UserActivityLog.objects.filter(
        activity_timestamp__gte=start_of_period,
        activity_timestamp__lte=end_of_period,
        activity_type='login'
    ).values('user__username', 'user__profile__role__role_name').annotate(
        login_count=Count('log_id'),
        last_login_time=Max('activity_timestamp')
    ).order_by('user__username')

    # Báo cáo đánh giá: Tính điểm tương tác bằng cách kết hợp dữ liệu hoạt động hàng ngày và hàng tuần
    evaluation_report = []
    for user in active_users:
        username = user['user__username']
        role = user['user__profile__role__role_name']
        active_count = user['active_user_count']

        # Tìm dữ liệu đăng nhập hàng tuần/tháng cho người dùng
        login_data = next(
            (login for login in login_frequency if login['user__username'] == username),
            None
        )

        if login_data:
            login_count = login_data['login_count']
            last_login = login_data['last_login_time']
        else:
            login_count = 0
            last_login = None

        # Điểm tương tác: Tính toán từ số lần hoạt động và đăng nhập
        engagement_score = active_count * 0.6 + login_count * 0.4

        evaluation_report.append({
            'username': username,
            'role': role,
            'active_count': active_count,
            'login_count': login_count,
            'last_login_time': last_login,
            'engagement_score': engagement_score,
        })

    # Truyền dữ liệu vào template
    context = {
        'evaluation_report': evaluation_report,
        'period': period,  # Thêm period vào context để xác định khoảng thời gian
        'period_label': period_label,  # Truyền thông tin về khoảng thời gian vào context
        'start_of_period': start_of_period,
        'end_of_period': end_of_period
    }

    return render(request, 'reports/user/engagement_activity_report.html', context)


def user_progress_and_milestones_report(request):
    # Chuẩn bị dữ liệu báo cáo cho từng người dùng với khóa học đã đăng ký, tiến độ, và điểm đánh giá
    report_data = []
    users = User.objects.all()

    for user in users:
        user_courses = []
        enrollments = Enrollment.objects.filter(student=user)  # Giả sử Enrollment liên kết User với Course

        for enrollment in enrollments:
            course = enrollment.course
            progress_percent = course.get_completion_percent(user)

            # Lấy danh sách quiz attempts của khóa học
            quiz_attempts = StudentQuizAttempt.objects.filter(user=user, quiz__course=course).order_by('-attempt_date')
            quiz_scores = {}

            for quiz_attempt in quiz_attempts:
                if quiz_attempt.quiz_id not in quiz_scores and quiz_attempt.user_id not in quiz_scores:  # Kiểm tra thêm user_id
                    quiz_scores[quiz_attempt.quiz.id] = {
                        'quiz_name': quiz_attempt.quiz,  # Giả sử quiz có trường 'name'
                        'score': quiz_attempt.score,
                        'attempt_date': quiz_attempt.attempt_date,
                    }

            # Lấy danh sách assessment attempts của khóa học
            assessment_attempts = StudentAssessmentAttempt.objects.filter(user=user, assessment__course=course).order_by('-attempt_date')
            assessment_scores = {}

            for attempt in assessment_attempts:
                if attempt.assessment_id not in assessment_scores and attempt.user_id not in assessment_scores:  # Kiểm tra thêm user_id
                    assessment_scores[attempt.assessment.id] = {
                        'assessment_name': attempt.assessment.title,  # Giả sử assessment có trường 'title'
                        'score_quiz': attempt.score_quiz,
                        'score_ass': attempt.score_ass,
                        'attempt_date': attempt.attempt_date,
        }


            user_courses.append({
                'course_name': course.course_name,
                'progress_percent': progress_percent,
                'quiz_scores': list(quiz_scores.values()),  # Chuyển thành list để đưa vào dữ liệu
                'assessment_scores': list(assessment_scores.values()),  # Chuyển thành list để đưa vào dữ liệu
            })
        
        report_data.append({
            'username': user.username,
            'courses': user_courses,
        })
    
    return render(request, 'reports/user/user_progress_and_milestones_report.html', {
        'report_data': report_data
    })


#warning_student
def format_timedelta(td):
    days = td.days
    seconds = td.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    time_parts = []

    if days > 0:
        time_parts.append(f"{days} days")
    if hours > 0:
        time_parts.append(f"{hours} hours")
    if minutes > 0:
        time_parts.append(f"{minutes} minutes")
    if seconds > 0 or not time_parts:
        time_parts.append(f"{seconds} seconds")

    return ', '.join(time_parts)


@login_required
def warning_student_report(request):
    completion_cutoff_time = timedelta(days=5)  # Đặt thời gian giới hạn hoàn thành khóa học
    update_cutoff_time = timedelta(days=2)  # Đặt thời gian giới hạn cập nhật tiến độ
    current_time = timezone.now()

    enrollments = Enrollment.objects.all()
    dropout_students = []
    no_update_students = []
    course_progress = {}

    if 'completion_times' not in request.session:
        request.session['completion_times'] = {}

    def update_or_create_progress(student, course, completion_percent):
        completion_percent = Decimal(completion_percent).quantize(Decimal('0.01'))  # Làm tròn tới 2 chữ số thập phân

        last_progress = UserCourseProgress.objects.filter(user=student, course=course).last()
        if last_progress:
            last_progress_percent = last_progress.progress_percentage
            progress_change = completion_percent - last_progress_percent
            if progress_change != 0:
                last_progress.progress_percentage = completion_percent
                last_progress.last_accessed = current_time
                last_progress.save()
            return last_progress
        else:
            return UserCourseProgress.objects.create(
                user=student,
                course=course,
                progress_percentage=completion_percent,
                last_accessed=current_time
            )

    def send_progress_email_and_create_notification(student_info, email_subject, email_body, notification_message):
        student = student_info['student']
        course = student_info['course']

        # Gửi email
        send_mail(
            email_subject,
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [student.email],
            fail_silently=False,
        )

        # Kiểm tra và tạo thông báo nếu chưa có
        if not ProgressNotification.objects.filter(user=student, course=course, notification_message=notification_message).exists():
            ProgressNotification.objects.create(
                user=student,
                course=course,
                notification_message=notification_message
            )

    for enrollment in enrollments:
        student = enrollment.student
        course = enrollment.course
        date_enrolled = enrollment.date_enrolled
        completion_percent = Decimal(course.get_completion_percent(student)).quantize(Decimal('0.01'))  # Làm tròn đến 2 chữ số thập phân
        time_since_enrollment = current_time - date_enrolled

        is_not_completed = completion_percent < 100
        last_progress = update_or_create_progress(student, course, completion_percent)

        # Kiểm tra nếu thời gian vượt qua completion_cutoff_time, thì chuyển sinh viên vào bảng dropout_students
        if is_not_completed and time_since_enrollment > completion_cutoff_time:
            dropout_students.append({
                'student': student,
                'course': course,
                'completion_percent': completion_percent,
                'time_elapsed': format_timedelta(time_since_enrollment)
            })

        # Nếu thời gian từ lần cập nhật tiến độ vượt quá update_cutoff_time và chưa hoàn thành khóa học,
        # chỉ xét vào bảng "No Progress Update" nếu chưa vượt qua thời gian completion_cutoff_time.
        if last_progress:
            time_since_last_update = current_time - last_progress.last_accessed
            if is_not_completed and time_since_last_update > update_cutoff_time:
                # Điều kiện này chỉ thêm sinh viên vào bảng "No Progress Update" nếu không quá thời gian hoàn thành khóa học
                if time_since_enrollment <= completion_cutoff_time:  # Điều kiện này ngăn sinh viên quá hạn vào bảng no_update_students
                    no_update_students.append({
                        'student': student,
                        'course': course,
                        'last_accessed': last_progress.last_accessed,
                        'time_since_last_update': format_timedelta(time_since_last_update),
                        'progress_percentage': last_progress.progress_percentage
                    })

            if course not in course_progress:
                course_progress[course] = {}
            course_progress[course][student] = {
                'progress': completion_percent,
                'enrolled_at': date_enrolled,
                'last_accessed': last_progress.last_accessed,
                'time_since_last_update': format_timedelta(time_since_last_update),
            }

    dropout_students.sort(key=lambda x: x['student'].username)
    no_update_students.sort(key=lambda x: x['student'].username)

    if request.method == 'POST':
        selected_dropout_ids = request.POST.getlist('dropout_students')
        selected_update_ids = request.POST.getlist('no_update_students')
        emails_sent = []

        # Check if Select All was triggered for dropout students
        if 'select_all_dropout' in request.POST:
            selected_dropout_ids = [f"{student_info['student'].id}_{student_info['course'].id}" for student_info in dropout_students]

        # Check if Select All was triggered for no-update students
        if 'select_all_update' in request.POST:
            selected_update_ids = [f"{student_info['student'].id}_{student_info['course'].id}" for student_info in no_update_students]

        if request.POST.get('send_dropout_emails'):
            for student_info in dropout_students:
                student_id_course_id = f"{student_info['student'].id}_{student_info['course'].id}"
                if student_id_course_id in selected_dropout_ids:
                    email_subject = 'Course Completion Reminder'
                    email_body = f"Hello {student_info['student'].username},\n\n" \
                                 f"You have not completed the course {student_info['course'].course_name}. " \
                                 f"Please consider continuing your studies.\n\n" \
                                 f"Best regards,\nYour Learning Platform Team"
                    notification_message = f"You have not completed the course {student_info['course'].course_name}."

                    # Gửi email và tạo thông báo
                    send_progress_email_and_create_notification(student_info, email_subject, email_body, notification_message)
                    emails_sent.append(student_info['student'].email)

        if request.POST.get('send_update_emails'):
            for student_info in no_update_students:
                student_id_course_id = f"{student_info['student'].id}_{student_info['course'].id}"
                if student_id_course_id in selected_update_ids:
                    email_subject = 'Progress Reminder'
                    email_body = f"Hello {student_info['student'].username},\n\n" \
                                 f"Your progress for {student_info['course'].course_name} has not changed. " \
                                 f"Please revisit the course.\n\n" \
                                 f"Best regards,\nYour Learning Platform Team"
                    notification_message = f"Your progress for {student_info['course'].course_name} has not changed."

                    # Gửi email và tạo thông báo
                    send_progress_email_and_create_notification(student_info, email_subject, email_body, notification_message)
                    emails_sent.append(student_info['student'].email)

        # If this is an Ajax request, return a JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'emails_sent': emails_sent})

    return render(request, 'reports/user/warning_student_report.html', {
        'dropout_students': dropout_students,
        'no_update_students': no_update_students,
        'course_progress': course_progress,
    })


def authentication_security_report(request):
    today = now()
    # Xác định tuần hiện tại (bắt đầu từ thứ Hai)
    start_of_week = today - timedelta(days=today.weekday(), hours=today.hour, minutes=today.minute, seconds=today.second, microseconds=today.microsecond)
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

    # Xóa dữ liệu tuần trước vào thứ Hai
    if today.weekday() == 0:
        last_week_start = start_of_week - timedelta(days=7)
        last_week_end = start_of_week - timedelta(seconds=1)
        UserActivityLog.objects.filter(
            activity_type='login',
            activity_timestamp__range=[last_week_start, last_week_end]
        ).delete()

    search_query = request.GET.get('search', '').strip()
    
    # Lấy thông tin login
    login_data = (
        UserActivityLog.objects.filter(
            activity_timestamp__range=[start_of_week, end_of_week],
            user__username__icontains=search_query
        )
        .values('user__username')
        .annotate(
            total_logins=Count('log_id', filter=Q(activity_type='login')),
            successful_logins=Count('log_id', filter=Q(activity_details='success')),
            failed_logins=Count('log_id', filter=Q(activity_details='failure')),
            email_notifications=Count('log_id', filter=Q(activity_type='2fa_email_notification')),
            password_attempts=Count('log_id', filter=Q(activity_type='password_attempt')),
            last_login=Max('activity_timestamp')
        )
        .order_by('-total_logins')
    )

    # Lấy thông tin đổi mật khẩu
    password_change_data = []
    password_records = PasswordChangeRecord.objects.filter(
        user__username__icontains=search_query
    )

    for record in password_records:
        last_change_time = record.updated_at
        # Reset số lần thay đổi nếu đã quá 5 phút
        if last_change_time and now() - last_change_time >= timedelta(minutes=5):
            record.change_count = 0
            record.save()
        
        warning = False
        if last_change_time and now() - last_change_time < timedelta(minutes=5):
            if record.change_count > 5:
                warning = True
        
        password_change_data.append({
            'user__username': record.user.username,
            'total_password_changes': record.change_count,
            'last_password_change': last_change_time,
            'warning': warning,
        })

    # Gộp thông tin login và đổi mật khẩu
    combined_data = []
    for login_record in login_data:
        username = login_record['user__username']
        password_change_record = next((record for record in password_change_data if record['user__username'] == username), None)
        
        total_password_changes = password_change_record['total_password_changes'] if password_change_record else 0
        last_password_change = password_change_record['last_password_change'] if password_change_record else None
        warning = password_change_record['warning'] if password_change_record else False

        combined_data.append({
            **login_record,
            'total_password_changes': total_password_changes,
            'last_password_change': last_password_change,
            'password_warning': warning,
        })

    # Phân trang
    paginator = Paginator(combined_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Đếm số người dùng có bật/tắt 2FA
    two_fa_enabled_count = Profile.objects.filter(two_fa_enabled=True).count()
    two_fa_disabled_count = Profile.objects.filter(two_fa_enabled=False).count()

    return render(request, 'reports/user/authentication_security_report.html', {
        'login_data': page_obj,
        'start_of_week': start_of_week.strftime('%Y-%m-%d'),
        'end_of_week': end_of_week.strftime('%Y-%m-%d'),
        'two_fa_enabled_count': two_fa_enabled_count,
        'two_fa_disabled_count': two_fa_disabled_count,
        'search_query': search_query,
    })

def send_warning_email(request):
    if request.method == 'POST':
        # Lọc những người dùng có số lần thay đổi mật khẩu vượt quá 2 lần
        password_change_data = PasswordChangeRecord.objects.filter(change_count__gt=5)

        # Kiểm tra nếu không có người dùng nào phạm lỗi
        if not password_change_data.exists():
            messages.info(request, 'No users have exceeded the password change limit.')
            return redirect('reports:authentication_security_report')

        # Gửi email cảnh báo cho từng người dùng
        for record in password_change_data:
            user = record.user  # Lấy người dùng từ bản ghi PasswordChangeRecord
            try:
                send_mail(
                    'Password Change Warning',
                    f'Dear {user.username}, you have changed your password frequently. Please review your account security.',
                    'admin@example.com',
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, f'Warning email sent to {user.username}.')
            except Exception as e:
                messages.error(request, f'Error sending email to {user.username}: {str(e)}')

    return redirect('reports:authentication_security_report')

import re
def is_valid_email(email):
    """
    Hàm kiểm tra xem email có hợp lệ hay không.
    """
    # Kiểm tra email hợp lệ bằng regex đơn giản
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None