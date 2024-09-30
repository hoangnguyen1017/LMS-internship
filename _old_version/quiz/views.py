from django.shortcuts import render, get_object_or_404, redirect
from .models import Quiz, Question, Answer
from .forms import QuizForm, QuestionForm, AnswerForm

# Quiz views
def quiz_list(request):
    quizzes = Quiz.objects.all()
    return render(request, 'quiz_list.html', {'quizzes': quizzes})

def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    return render(request, 'quiz_detail.html', {'quiz': quiz})

def quiz_add(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('quiz_list')
    else:
        form = QuizForm()
    return render(request, 'quiz_form.html', {'form': form})

def quiz_edit(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            return redirect('quiz_list')
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'quiz_form.html', {'form': form})

def quiz_delete(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.method == 'POST':
        quiz.delete()
        return redirect('quiz_list')
    return render(request, 'quiz_confirm_delete.html', {'quiz': quiz})
