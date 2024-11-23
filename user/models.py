from django.db import models
from role.models import Role
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from training_program.models import TrainingProgram
from module_group.models import Module
from course.models import Course

class User(AbstractUser):
    date_joined = models.DateTimeField(auto_now_add=True)
    training_programs = models.ManyToManyField(TrainingProgram, blank=True)  
    modules = models.ManyToManyField(Module, related_name='assigned_users', blank=True)
    is_2fa_enabled = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False) 
    groups = models.ManyToManyField(
        Group,
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
        related_name='custom_user_groups',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
        related_name='custom_user_permissions',
    )
     # Trạng thái khóa tài khoản

    def lock_account(self):
        """Khóa tài khoản người dùng"""
        self.is_locked = True
        self.save()

    def unlock_account(self):
        """Mở khóa tài khoản người dùng"""
        self.is_locked = False
        self.save()
    def __str__(self):
        return f"{self.username} - {'Locked' if self.is_locked else 'Active'}"

class Student(models.Model):
    user = models.OneToOneField('user.User', on_delete=models.CASCADE, primary_key=True)
    student_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    enrolled_courses = models.ManyToManyField(Course, blank=True) 
    
    def __str__(self):
        return f"{self.user.username} - Student"

class Profile(models.Model):
    user = models.OneToOneField('user.User', on_delete=models.CASCADE, null=True, blank=True)  
    email_verified = models.BooleanField(default=False)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    profile_picture_url = models.URLField(max_length=10000, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    interests = models.TextField(blank=True, null=True)
    learning_style = models.CharField(max_length=50, blank=True, null=True)
    preferred_language = models.CharField(max_length=50, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    two_fa_enabled = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user.username if self.user else self.student.username} - {self.role.role_name if self.role else 'No Role'}"
    def __str__(self):
        return f"{self.user.username if self.user else self.instructor.username} - {self.role.role_name if self.role else 'No Role'}"
    def get_instructor_courses(self):
        if hasattr(self, 'user') and hasattr(self.user, 'instructor'):
            return self.user.instructor.taught_courses.all()
        return []

    def get_enrolled_courses(self):
        if hasattr(self, 'user') and hasattr(self.user, 'instructor'):
            return self.user.instructor.enrolled_courses.all()
        return []

class Instructor(models.Model):
    user = models.OneToOneField('user.User', on_delete=models.CASCADE, primary_key=True)
    taught_courses = models.ManyToManyField(Course, related_name='instructors', blank=True)
    enrolled_courses = models.ManyToManyField(Course, related_name='students', blank=True)

    def __str__(self):
        return f"{self.user.username} - Instructor"

    def total_taught_courses(self):
        return self.taught_courses.count()

    def total_enrolled_courses(self):
        return self.enrolled_courses.count()



    
