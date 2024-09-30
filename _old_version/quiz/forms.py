from django import forms
from .models import Quiz

# Form for creating and editing quizzes
class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description']
