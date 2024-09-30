from django.shortcuts import render, get_object_or_404, redirect
from .models import Subject
from .forms import SubjectForm
from module_group.models import ModuleGroup

# Subject views
# def subject_list(request):
#     subjects = Subject.objects.all()
#     return render(request, 'subject_list.html', {'subjects': subjects})

def subject_list(request):
    module_groups = ModuleGroup.objects.all()
   # modules = Module.objects.all()
    subjects = Subject.objects.all()
    return render(request, 'subject_list.html', {
        'module_groups': module_groups,
      #  'modules': modules,
        'subjects': subjects,
    })


def subject_add(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subject:subject_list')
    else:
        form = SubjectForm()
    return render(request, 'subject_form.html', {'form': form})

def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            return redirect('subject:subject_list')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'subject_form.html', {'form': form})

def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        return redirect('subject:subject_list')
    return render(request, 'subject_confirm_delete.html', {'subject': subject})
