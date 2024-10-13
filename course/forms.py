from django import forms
from .models import Course, UserCourseProgress

from user.models import User  


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_name', 'course_description', 'created_by', 'course_picture_url']
        widgets = {
            'created_by': forms.Select(),
            'course_picture_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter course picture URL'}),
        }

class UserCourseProgressForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label='User') 
    course = forms.ModelChoiceField(queryset=Course.objects.all(), label='Course')  


    class Meta:
        model = UserCourseProgress
        fields = ['user', 'course', 'progress_percentage']
        widgets = {
            'progress_percentage': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100'}),  

        }
