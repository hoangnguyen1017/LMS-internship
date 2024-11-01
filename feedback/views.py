from django.shortcuts import render, redirect, get_object_or_404
from .forms import InstructorFeedbackForm, CourseFeedbackForm, TrainingProgramFeedbackForm
from .models import InstructorFeedback, CourseFeedback, TrainingProgramFeedback
from course.models import Course
from training_program.models import TrainingProgram
from user.models import User
from module_group.models import ModuleGroup, Module
from django.contrib import messages
from django.core.paginator import Paginator

'''def feedback_list(request):
    module_groups = ModuleGroup.objects.all()
    modules = Module.objects.all()
    instructor_feedbacks = InstructorFeedback.objects.all()
    course_feedbacks = CourseFeedback.objects.all()
    training_feedbacks = TrainingProgramFeedback.objects.all()

    return render(request, 'feedback_list.html', {
        'instructor_feedbacks': instructor_feedbacks,
        'course_feedbacks': course_feedbacks,
        'training_feedbacks': training_feedbacks,
        'module_groups': module_groups,
        'modules': modules
    })'''


def feedback_list(request):
    module_groups = ModuleGroup.objects.all()
    modules = Module.objects.all()
    instructor_feedbacks = InstructorFeedback.objects.all()
    course_feedbacks = CourseFeedback.objects.all()
    training_feedbacks = TrainingProgramFeedback.objects.all()

    # Fetch instructors and courses
    instructors = User.objects.all()  # Assuming you have a role model for instructors
    courses = Course.objects.all()
    training_programs = TrainingProgram.objects.all()

    return render(request, 'feedback_list.html', {
        'instructor_feedbacks': instructor_feedbacks,
        'course_feedbacks': course_feedbacks,
        'training_feedbacks': training_feedbacks,
        'module_groups': module_groups,
        'modules': modules,
        'instructors': instructors,
        'courses': courses,
        'training_programs': training_programs  # Add training programs as well
    })

def give_instructor_feedback(request, instructor_id):
    instructor = User.objects.get(pk=instructor_id)
    if request.method == 'POST':
        form = InstructorFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user
            feedback.instructor = instructor
            feedback.save()
            return redirect('feedback:feedback_success')
    else:
        form = InstructorFeedbackForm()
    return render(request, 'feedback_Instructor.html', {'form': form, 'instructor': instructor})

def give_course_feedback(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.method == 'POST':
        form = CourseFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user
            feedback.course = course
            feedback.save()
            return redirect('course:course_detail', pk=course.id)
    else:
        form = CourseFeedbackForm()

    # Fetch the 5 newest feedback entries for this course
    latest_feedbacks = CourseFeedback.objects.filter(course=course).order_by('-created_at')[:5]

    return render(request, 'feedback_Course.html', {
        'form': form,
        'course': course,
        'latest_feedbacks': latest_feedbacks
    })

def give_training_program_feedback(request, training_program_id):
    training_program = TrainingProgram.objects.get(pk=training_program_id)
    if request.method == 'POST':
        form = TrainingProgramFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user
            feedback.training_program = training_program
            feedback.save()
            return redirect('feedback:feedback_success')
    else:
        form = TrainingProgramFeedbackForm()
    return render(request, 'feedback_Program.html', {'form': form, 'training_program': training_program})

def feedback_success(request):
    return render(request, 'feedback_success.html')

def instructor_feedback_detail(request, feedback_id):
    feedback = InstructorFeedback.objects.get(pk=feedback_id)
    return render(request, 'feedback_detail.html', {'feedback': feedback, 'type': 'Instructor'})

def course_feedback_detail(request, feedback_id):
    feedback = CourseFeedback.objects.get(pk=feedback_id)
    return render(request, 'feedback_detail.html', {'feedback': feedback, 'type': 'Course'})

def program_feedback_detail(request, feedback_id):
    feedback = TrainingProgramFeedback.objects.get(pk=feedback_id)
    return render(request, 'feedback_detail.html', {'feedback': feedback, 'type': 'Training Program'})

def course_all_feedback(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    all_feedbacks = CourseFeedback.objects.filter(course=course).order_by('-created_at')

    # Pagination
    paginator = Paginator(all_feedbacks, 10)  # Show 10 feedbacks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'feedback_course_list.html', {
        'course': course,
        'page_obj': page_obj,
    })