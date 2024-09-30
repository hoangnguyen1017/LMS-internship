from django import forms
from .models import Role, User, Quiz, Question, Answer, Module, UserModule, Category
from .models import TrainingProgram, Subject
from django.forms import modelformset_factory, inlineformset_factory



#============== QUIZ
class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description']

#USER
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'full_name', 'role']
        widgets = {
            'password': forms.PasswordInput(),
        }

#ROLE
class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['role_name']

#======== MODULE
# Form to create and edit modules
class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['module_name', 'module_url']

#======== USER MODULE
# Form to assign modules to users
class UserModuleForm(forms.ModelForm):
    class Meta:
        model = UserModule
        fields = ['user', 'module']


#======== QUESTION 

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['subject', 'category', 'question_text']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']

AnswerFormSet = inlineformset_factory(Question, Answer, form=AnswerForm, extra=1)
QuestionFormSet = modelformset_factory(Question, form=QuestionForm, extra=1)


# TRAINING PROGRAM
class TrainingProgramForm(forms.ModelForm):
    class Meta:
        model = TrainingProgram
        fields = ['program_name', 'program_code', 'description']

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'description']

from django import forms
from .models import TrainingProgramSubjects, Subject

class TrainingProgramSubjectsForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = TrainingProgramSubjects
        fields = ['subjects']  # List other fields if necessary

    def __init__(self, *args, **kwargs):
        program = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        if program:
            # Initialize the form with the existing subjects
            self.fields['subjects'].initial = [sub.subject for sub in program.trainingprogramsubjects_set.all()]

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'subject']