from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from .models import TrainingProgram, Subject, TrainingProgramSubjects
from .forms import TrainingProgramSubjectsForm

# Create your views here.
def manage_subjects(request, program_id):
    program = get_object_or_404(TrainingProgram, pk=program_id)
    if request.method == 'POST':
        form = TrainingProgramSubjectsForm(request.POST, instance=program)
        if form.is_valid():
            selected_subjects = form.cleaned_data['subjects']
            TrainingProgramSubjects.objects.filter(program=program).delete()
            for subject in selected_subjects:
                TrainingProgramSubjects.objects.create(program=program, subject=subject)
            return redirect('training_program_list')
    else:
        form = TrainingProgramSubjectsForm(instance=program)
    return render(request, 'manage_subjects.html', {'form': form, 'program': program})

