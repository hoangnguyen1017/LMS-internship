# learning/views.py
from django.shortcuts import render
from course.models import Course  # Import the Course model
from certification.models import Certification  # Import the Certification model
from learning_path.models import LearningPath

# def my_learning_view(request):
#     # context setup
#     return render(request, 'mylearning/my_learning.html')

def index(request):
    # Retrieve all published courses
    courses = Course.objects.filter(published=True)

    # Prepare data to be passed to the template
    course_data = []
    for course in courses:
        # Calculate the completion percentage based on your logic
        completion_percentage = course.get_completion_percent(request.user)  # Assuming user is authenticated

        # Assuming rating is a field in your Course model
        rating = course.rating if hasattr(course, 'rating') else 0  # Fallback to 0 if rating doesn't exist

        # Create a list of stars based on the rating
        stars = [1 for _ in range(rating)] + [0 for _ in range(5 - rating)]  # 1 for filled stars, 0 for empty stars

        course_data.append({
            'title': course.course_name,
            'description': course.description,
            'image_url': course.image.url if course.image else './assets/img/default_course_image.png',
            'completion_percentage': completion_percentage,
            'stars': stars,  # Pass the stars list to the template
        })
        
    return render(request, 'index.html', {'courses': course_data})

def learning_paths(request):
    learning_paths = LearningPath.objects.filter(creator=request.user)  # Fetching learning paths for the logged-in user
    return render(request, 'learningPaths.html', {'learning_paths': learning_paths})

def certification(request):
    # Retrieve certifications for the logged-in user
    user_certifications = Certification.objects.filter(user=request.user)
    return render(request, 'certification.html', {'certifications': user_certifications})


def archived(request):
    return render(request, 'archived.html')

def learning_tools(request):
    return render(request, 'learningTools.html')
