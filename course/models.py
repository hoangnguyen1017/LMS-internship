from django.db import models
from user.models import User  # Giả sử mô hình User nằm trong ứng dụng user

class Course(models.Model):
    course_name = models.CharField(max_length=255)
    course_description = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    course_picture_url = models.URLField(max_length=500, blank=True, null=True)


    def __str__(self):
        return self.course_name

class UserCourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    last_accessed = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user} - {self.course} - {self.progress_percentage}%"