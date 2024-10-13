from django import forms
from .models import Subject

# Form for creating and editing subjects
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'description']

