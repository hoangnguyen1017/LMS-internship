from django.shortcuts import render, get_object_or_404, redirect
from .models import Role, User, Quiz, Question, Answer, Module, UserModule, Category
from .forms import RoleForm, UserForm, QuizForm, QuestionForm, AnswerForm, AnswerFormSet, ModuleForm, UserModuleForm, SubjectForm, CategoryForm
from django.utils import timezone
from .models import TrainingProgram, Subject, TrainingProgramSubjects
from .forms import TrainingProgramForm, SubjectForm, TrainingProgramSubjectsForm

def home(request):
    return render(request, 'home.html')

def manage_subjects(request, program_id):
    program = get_object_or_404(TrainingProgram, pk=program_id)
    if request.method == 'POST':
        form = TrainingProgramSubjectsForm(request.POST, instance=program)
        if form.is_valid():
            # Save the form and update the subjects
            selected_subjects = form.cleaned_data['subjects']
            TrainingProgramSubjects.objects.filter(program=program).delete()
            for subject in selected_subjects:
                TrainingProgramSubjects.objects.create(program=program, subject=subject)
            return redirect('training_program_list')  # Or another success URL
    else:
        form = TrainingProgramSubjectsForm(instance=program)

    return render(request, 'training_program/manage_subjects.html', {'form': form, 'program': program})


# TrainingProgram Views
def training_program_list(request):
    programs = TrainingProgram.objects.all()
    return render(request, 'training_program/training_program_list.html', {'programs': programs})

def training_program_add(request):
    if request.method == 'POST':
        form = TrainingProgramForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('training_program_list')
    else:
        form = TrainingProgramForm()
    return render(request, 'training_program/training_program_form.html', {'form': form})

def training_program_edit(request, pk):
    program = get_object_or_404(TrainingProgram, pk=pk)
    if request.method == 'POST':
        form = TrainingProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            return redirect('training_program_list')
    else:
        form = TrainingProgramForm(instance=program)
    return render(request, 'training_program/training_program_form.html', {'form': form})

def training_program_delete(request, pk):
    program = get_object_or_404(TrainingProgram, pk=pk)
    if request.method == 'POST':
        program.delete()
        return redirect('training_program_list')
    return render(request, 'training_program/training_program_confirm_delete.html', {'program': program})

# Subject Views
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'subject/subject_list.html', {'subjects': subjects})

def subject_add(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subject_list')
    else:
        form = SubjectForm()
    return render(request, 'subject/subject_form.html', {'form': form})

def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            return redirect('subject_list')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'subject/subject_form.html', {'form': form})

def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        return redirect('subject_list')
    return render(request, 'subject/subject_confirm_delete.html', {'subject': subject})

# TrainingProgramSubjects Views
def training_program_subjects_add(request):
    if request.method == 'POST':
        form = TrainingProgramSubjectsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('training_program_list')
    else:
        form = TrainingProgramSubjectsForm()
    return render(request, 'training_program/training_program_subjects_form.html', {'form': form})


# QUIZ
# List all quizzes
def quiz_list(request):
    quizzes = Quiz.objects.all()
    return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes})

# View details of a specific quiz
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    return render(request, 'quiz/quiz_detail.html', {'quiz': quiz})

# Add a new quiz
def quiz_add(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('quiz_list')
    else:
        form = QuizForm()
    return render(request, 'quiz/quiz_form.html', {'form': form})

# Edit an existing quiz
def quiz_edit(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            return redirect('quiz_list')
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'quiz/quiz_form.html', {'form': form})

# Delete a quiz
def quiz_delete(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.method == 'POST':
        quiz.delete()
        return redirect('quiz_list')
    return render(request, 'quiz/quiz_confirm_delete.html', {'quiz': quiz})


# ======================= QUESTION
# List all questions
def question_list(request):
    questions = Question.objects.all()
    return render(request, 'question/question_list.html', {'questions': questions})

# View details of a specific question
def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    return render(request, 'question/question_detail.html', {'question': question})

def question_add(request):
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            # Save the question
            question = question_form.save()

            # Get the answers from the POST data
            answer_texts = request.POST.getlist('answer_text[]')
            is_corrects = request.POST.getlist('is_correct[]')

            # Check if lengths match
            if len(answer_texts) != len(is_corrects):
                # Handle mismatch error, e.g., return an error response or log it
                return render(request, 'question/question_add.html', {
                    'question_form': question_form,
                    'error': 'Mismatch between answer texts and correctness flags'
                })

            # Save the answers associated with the question
            for i in range(len(answer_texts)):
                Answer.objects.create(
                    question=question,
                    text=answer_texts[i],
                    is_correct=is_corrects[i].lower() == 'true'  # Corrected comparison
                )

            return redirect('questions_list')  # Redirect to the list of questions or any other page

    else:
        question_form = QuestionForm()

    return render(request, 'question/question_add.html', {'question_form': question_form})

#Add answers to the question
def answer_add(request, question_pk):
    question = get_object_or_404(Question, pk=question_pk)
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.save()
            return redirect('question_detail', pk=question.pk)
    else:
        form = AnswerForm()
    return render(request, 'question/answer_form.html', {'form': form, 'question': question})

# Edit an existing question
def question_edit(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('question_list')
    else:
        form = QuestionForm(instance=question)
    return render(request, 'question/question_form.html', {'form': form})

# Delete a question
def question_delete(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        question.delete()
        return redirect('question_list')
    return render(request, 'question/question_confirm_delete.html', {'question': question})

#Answer_edit
def answer_edit(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    if request.method == 'POST':
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            form.save()
            return redirect('question_detail', pk=answer.question.pk)
    else:
        form = AnswerForm(instance=answer)
    return render(request, 'answers/answer_form.html', {'form': form, 'answer': answer})

#Answer delete
def answer_delete(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    question_id = answer.question.id
    if request.method == 'POST':
        answer.delete()
        return redirect('question_detail', pk=question_id)
    return render(request, 'answers/answer_confirm_delete.html', {'answer': answer})

# View for Subject Detail
def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    return render(request, 'question/subject_detail.html', {'subject': subject})

# View for Category Detail
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    return render(request, 'question/category_detail.html', {'category': category})

#======== USER
# List of users
def user_list(request):
    users = User.objects.all()
    return render(request, 'user/user_list.html', {'users': users})

# User details
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'user/user_detail.html', {'user': user})

# Add new user
def user_add(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm()
    return render(request, 'user/user_form.html', {'form': form})

# Edit existing user
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'user/user_form.html', {'form': form})


#ROLE
# List of roles
def role_list(request):
    roles = Role.objects.all()
    return render(request, 'role/role_list.html', {'roles': roles})

# Role details (optional, if you want to have details view)
def role_detail(request, pk):
    role = get_object_or_404(Role, pk=pk)
    return render(request, 'role/role_detail.html', {'role': role})

# Add new role
def role_add(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('role_list')
    else:
        form = RoleForm()
    return render(request, 'role/role_form.html', {'form': form})

# Edit role
def role_edit(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            return redirect('role_list')
    else:
        form = RoleForm(instance=role)
    return render(request, 'role/role_form.html', {'form': form})

# Delete role
def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.delete()
        return redirect('role_list')
    return render(request, 'role/role_confirm_delete.html', {'role': role})

#======== MODULE
# List of modules
def module_list(request):
    modules = Module.objects.all()
    return render(request, 'module/module_list.html', {'modules': modules})


# Add a new module
def module_add(request):
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('module_list')
    else:
        form = ModuleForm()
    return render(request, 'module/module_form.html', {'form': form})

# Edit an existing module
def module_edit(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            return redirect('module_list')
    else:
        form = ModuleForm(instance=module)
    return render(request, 'module/module_form.html', {'form': form})

# Delete a module
def module_delete(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        module.delete()
        return redirect('module_list')
    return render(request, 'module/module_confirm_delete.html', {'module': module})

#======== USER MODULE
# List user-module assignments
def user_module_list(request):
    user_modules = UserModule.objects.all()
    return render(request, 'user_module/user_module_list.html', {'user_modules': user_modules})

# Assign a module to a user
def user_module_add(request):
    if request.method == 'POST':
        form = UserModuleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_module_list')
    else:
        form = UserModuleForm()
    return render(request, 'user_module/user_module_form.html', {'form': form})

# Edit user-module assignment
def user_module_edit(request, pk):
    user_module = get_object_or_404(UserModule, pk=pk)
    if request.method == 'POST':
        form = UserModuleForm(request.POST, instance=user_module)
        if form.is_valid():
            form.save()
            return redirect('user_module_list')
    else:
        form = UserModuleForm(instance=user_module)
    return render(request, 'user_module/user_module_form.html', {'form': form})

# Delete user-module assignment
def user_module_delete(request, pk):
    user_module = get_object_or_404(UserModule, pk=pk)
    if request.method == 'POST':
        user_module.delete()
        return redirect('user_module_list')
    return render(request, 'user_module/user_module_confirm_delete.html', {'user_module': user_module})

#======== CATEGORY 

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category/category_list.html', {'categories': categories})

def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'category/category_form.html', {'form': form})

def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category/category_form.html', {'form': form})

def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'category/category_confirm_delete.html', {'category': category})


#======== SUBJECT
# List of subjects
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'subject/subject_list.html', {'subjects': subjects})

# Add a new subject
def subject_add(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subject_list')
    else:
        form = SubjectForm()
    return render(request, 'subject/subject_form.html', {'form': form})

# Edit an existing subject
def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            return redirect('subject_list')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'subject/subject_form.html', {'form': form})

# Delete a subject
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        return redirect('subject_list')
    return render(request, 'subject/subject_confirm_delete.html', {'subject': subject})
