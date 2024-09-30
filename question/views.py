from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Answer
from .forms import QuestionForm, AnswerForm
from module_group.models import ModuleGroup

# Question views
def question_list(request):
    module_groups = ModuleGroup.objects.all()
    questions = Question.objects.all()
    return render(request, 'question_list.html', {'questions': questions, 'module_groups':module_groups})

def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    return render(request, 'question_detail.html', {'question': question})

def question_add(request):
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save()
            answer_texts = request.POST.getlist('answer_text[]')
            is_corrects = request.POST.getlist('is_correct[]')
            if len(answer_texts) != len(is_corrects):
                return render(request, 'question_add.html', {
                    'question_form': question_form,
                    'error': 'Mismatch between answer texts and correctness flags'
                })
            for i in range(len(answer_texts)):
                Answer.objects.create(
                    question=question,
                    text=answer_texts[i],
                    is_correct=is_corrects[i].lower() == 'true'
                )
            return redirect('question_list')
    else:
        question_form = QuestionForm()
    return render(request, 'question_add.html', {'question_form': question_form})

def question_edit(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('question_list')
    else:
        form = QuestionForm(instance=question)
    return render(request, 'question_form.html', {'form': form})

def question_delete(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        question.delete()
        return redirect('question_list')
    return render(request, 'question_confirm_delete.html', {'question': question})
