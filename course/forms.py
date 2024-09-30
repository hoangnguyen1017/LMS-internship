from django import forms
from .models import Course, UserCourseProgress
from user.models import User  # Giả sử mô hình User nằm trong ứng dụng user

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_name', 'course_description', 'created_by']
        widgets = {
            'created_by': forms.Select(),  # Hiển thị danh sách người dùng để chọn người tạo khóa học
        }

class UserCourseProgressForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label='User')  # Dropdown để chọn người dùng
    course = forms.ModelChoiceField(queryset=Course.objects.all(), label='Course')  # Dropdown để chọn khóa học

    class Meta:
        model = UserCourseProgress
        fields = ['user', 'course', 'progress_percentage']
        widgets = {
            'progress_percentage': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100'}),  # Hiển thị trường số với bước và phạm vi
        }
