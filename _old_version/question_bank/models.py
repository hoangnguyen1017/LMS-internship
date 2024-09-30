from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class ModuleGroup(models.Model):
    group_name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.group_name

class Module(models.Model):
    module_name = models.CharField(max_length=255)
    module_url = models.URLField()
    group = models.ForeignKey(ModuleGroup, on_delete=models.CASCADE, related_name='modules')
    
    def __str__(self):
        return self.module_name


#========== ROLE
class Role(models.Model):
    role_name = models.CharField(max_length=255)

    def __str__(self):
        return self.role_name

#========== USER
class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username
    
#========== MODULE
class Module(models.Model):
    module_name = models.CharField(max_length=255)
    module_url = models.URLField(max_length=255)

    def __str__(self):
        return self.module_name

#========== USER_MODULE
class UserModule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'module')  # Composite primary key

    def __str__(self):
        return f"{self.user.username} - {self.module.module_name}"

class TrainingProgram(models.Model):
    program_name = models.CharField(max_length=255, unique=True)
    program_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.program_name

#========== SUBJECT
class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class TrainingProgram(models.Model):
    program_name = models.CharField(max_length=100)
    program_code = models.CharField(max_length=10)
    description = models.TextField()
    

class TrainingProgramSubjects(models.Model):
    program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('program', 'subject')

    def __str__(self):
        return f"{self.program} - {self.subject}"

#========== CATEGORY
class Category(models.Model):
    category_name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='categories')

    def __str__(self):
        return self.category_name
    
#========== QUESTION
class Question(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)

    def __str__(self):
        return self.question_text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

#========== QUIZ
class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title








