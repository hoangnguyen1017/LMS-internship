# enrollment/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import EnrollmentForm, AdminEnrollmentForm
from course.models import Enrollment, Course
from django.contrib.auth.decorators import user_passes_test
from collaboration_group.models import CollaborationGroup, GroupMember
from django.db import IntegrityError

@user_passes_test(lambda u: u.is_superuser)  # Restrict access to superusers only
def enrollment_list_admin(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    all_enrollments = Enrollment.objects.all()  # Fetch all enrollments for admin view
    return render(request, 'enrollment/admin_enroll_list.html', {
        'enrollments': enrollments,
        'all_enrollments': all_enrollments,
    })

def admin_enroll_users(request):
    groups = CollaborationGroup.objects.all()
    courses = Course.objects.all()  # Fetch all courses
    selected_group_id = request.GET.get('group')
    group_members = []

    if selected_group_id:
        # Fetch members of the selected group
        group_members = GroupMember.objects.filter(group_id=selected_group_id)

    if request.method == 'POST':
        print('come to post')
        selected_users = request.POST.getlist('users')
        course_id = request.POST.get('course')
        print(f'Selected Users: {selected_users}, Course ID: {course_id}')

        if selected_users and course_id:
            for user_id in selected_users:
                print(f'Enrolling User ID: {user_id} in Course ID: {course_id}')
                try:
                    Enrollment.objects.create(student_id=user_id, course_id=course_id)
                except IntegrityError as e:
                    messages.warning(request, f"User ID {user_id} is already enrolled in this course.")
                    print(f"IntegrityError for User ID: {user_id} - {e}")
            messages.success(request, "Selected users have been enrolled successfully.")
            
            # Instead of redirecting immediately, you might render the same template to check for updates.
            return redirect('group_enrollment:admin_enroll_users')


    return render(request, 'enrollment/admin_enroll_users.html', {
        'groups': groups,
        'selected_group_id': selected_group_id,
        'group_members': group_members,
        'courses': courses,  # Pass the list of courses to the template
    })


def enroll_student(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']  # Assuming your form has a field for the course
            # Check if the student is already enrolled in this course
            if Enrollment.objects.filter(student=request.user, course=course).exists():
                messages.error(request, f'You are already enrolled in {course.course_name}.')
                return redirect('group_enrollment:enrollment_list')

            # Create the enrollment since the student is not already enrolled
            enrollment = form.save(commit=False)
            enrollment.student = request.user  # Assuming the user is logged in
            enrollment.save()
            messages.success(request, f'You have successfully enrolled in {course.course_name}.')
            return redirect('group_enrollment:enrollment_list')
    else:
        form = EnrollmentForm()

    return render(request, 'enrollment/enroll_student.html', {'form': form})

def enrollment_list(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, 'enrollment/enrollment_list.html', {'enrollments': enrollments})

def edit_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    if request.method == 'POST':
        form = EnrollmentForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            messages.success(request, f'Enrollment for {enrollment.course.course_name} updated successfully.')
            return redirect('enrollment:enrollment_list')
    else:
        form = EnrollmentForm(instance=enrollment)

    return render(request, 'enrollment/enroll_student.html', {'form': form})

def delete_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    enrollment.delete()
    messages.success(request, f'Enrollment for {enrollment.course.course_name} deleted successfully.')
    return redirect('enrollment:enrollment_list')
