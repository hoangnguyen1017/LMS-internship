from django import forms
from .models import TrainingProgramSubjects, Subject

# Form for assigning subjects to training programs
class TrainingProgramSubjectsForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = TrainingProgramSubjects
        fields = ['subjects']

    def __init__(self, *args, **kwargs):
        program = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        if program:
            # Initialize the form with the existing subjects
            self.fields['subjects'].initial = [sub.subject for sub in program.trainingprogramsubjects_set.all()]
