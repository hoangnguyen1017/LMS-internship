from django.utils import timezone
from django.urls import resolve
from .models import UserActivityLog
from course.models import Course  # Import Course model

class ActivityTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request
        response = self.get_response(request)

        # Log activity if the user is authenticated and the request is GET
        if request.user.is_authenticated and request.method == 'GET':
            current_url = resolve(request.path_info).url_name
            resolved_url = resolve(request.path_info)

            # Kiểm tra nếu người dùng đang truy cập vào trang chi tiết khóa học
            if current_url == 'course_enroll':
                # Lấy ID khóa học từ kwargs (từ URL)
                course_id = resolved_url.kwargs.get('pk')

                if course_id:
                    try:
                        # Lấy thông tin khóa học từ database
                        course = Course.objects.get(pk=course_id)
                        activity_details = f"Accessed course enroll: {course.course_name} (ID: {course.pk})"
                    except Course.DoesNotExist:
                        activity_details = "Accessed course page (course not found)"
                else:
                    activity_details = "Accessed course page with no valid course ID"

                # Ghi log hoạt động
                UserActivityLog.objects.create(
                    user=request.user,
                    activity_type='page_visit',
                    activity_details=activity_details,
                    activity_timestamp=timezone.now()
                )
            else:
                # Ghi log cho các trang khác
                UserActivityLog.objects.create(
                    user=request.user,
                    activity_type='page_visit',
                    activity_details=f"Accessed {current_url}",
                    activity_timestamp=timezone.now()
                )

        return response
