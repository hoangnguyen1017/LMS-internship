from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from .models import AssessmentType
from .forms import AssessmentTypeForm

class AssessmentTypeListView(View):
    def get(self, request):
        assessment_types = AssessmentType.objects.all()
        return render(request, 'assessmenttype/assessment_type_list.html', {'assessment_types': assessment_types})

class AssessmentTypeCreateView(View):
    def get(self, request):
        form = AssessmentTypeForm()
        return render(request, 'assessmenttype/assessment_type_form.html', {'form': form})

    def post(self, request):
        form = AssessmentTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('assessment:assessmenttype_list'))
        return render(request, 'assessmenttype/assessment_type_form.html', {'form': form})

class AssessmentTypeUpdateView(View):
    def get(self, request, pk):
        assessment_type = get_object_or_404(AssessmentType, pk=pk)
        form = AssessmentTypeForm(instance=assessment_type)
        return render(request, 'assessmenttype/assessment_type_form.html', {'form': form})

    def post(self, request, pk):
        assessment_type = get_object_or_404(AssessmentType, pk=pk)
        form = AssessmentTypeForm(request.POST, instance=assessment_type)
        if form.is_valid():
            form.save()
            return redirect(reverse('assessment:assessmenttype_list'))
        return render(request, 'assessmenttype/assessment_type_form.html', {'form': form})

class AssessmentTypeDeleteView(View):
    def get(self, request, pk):
        assessment_type = get_object_or_404(AssessmentType, pk=pk)
        assessment_type.delete()
        return redirect(reverse('assessment:assessmenttype_list'))
