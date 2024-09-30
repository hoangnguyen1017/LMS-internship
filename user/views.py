from django.shortcuts import render, get_object_or_404, redirect
from .models import User, UserProfile, Role, UserPersonalization
from .forms import UserForm, UserProfileForm, ExcelImportForm
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse
import bcrypt
import openpyxl
import pandas as pd

learning_paths = {
    'Technology': {
        'Visual': 'Learn through videos.',
        'Auditory': 'Listen to podcasts.',
        'Reading/Writing': 'Read books.',
        'Kinesthetic': 'Hands-on projects.'
    },
    'Art': {
        'Visual': 'Attend art courses.',
        'Auditory': 'Listen to art interviews.',
        'Reading/Writing': 'Study art history.',
        'Kinesthetic': 'Practice art creation.'
    },
    'Business': {
        'Visual': 'Watch business case studies.',
        'Auditory': 'Listen to business lectures.',
        'Reading/Writing': 'Read business books.',
        'Kinesthetic': 'Engage in business projects.'
    }
}

def recommend_courses(user):

    interests = user.profile.interests.lower().split(', ') if user.profile and user.profile.interests else []
    learning_style = user.profile.learning_style or "Visual"  

    recommended_courses = set()  
    personalized_learning_path = []

    for interest in interests:
        if "technology" in interest:
            recommended_courses.update(["Introduction to AI", "Advanced Python Programming"])
            category = "Technology"
        elif "art" in interest:
            recommended_courses.update(["Introduction to Painting", "Digital Art Creation"])
            category = "Art"
        elif "business" in interest:
            recommended_courses.update(["Business Strategy 101", "Financial Management"])
            category = "Business"
        else:
            category = None
        
        if category and category in learning_paths and learning_style in learning_paths[category]:
            personalized_learning_path.append(learning_paths[category][learning_style])

    if not personalized_learning_path:
        personalized_learning_path = ["Dựa trên sở thích và phong cách học tập của bạn."]
    
    return list(recommended_courses), personalized_learning_path, learning_style

def save_personalization_data(user):
    recommended_courses, personalized_learning_path, learning_style = recommend_courses(user)

    personalization, created = UserPersonalization.objects.get_or_create(user=user)
    personalization.recommended_courses = ', '.join(recommended_courses)
    personalization.personalized_learning_path = ', '.join(personalized_learning_path) 
    personalization.learning_style = learning_style
    personalization.save()

def user_list(request):
    query = request.GET.get('q', '')
    selected_role = request.GET.get('role', '')

    users = User.objects.all()
    roles = Role.objects.all()

    if query and selected_role:
        users = users.filter(
            Q(full_name__icontains=query) | Q(username__icontains=query),
            role__role_name=selected_role
        )
    elif query: 
        users = users.filter(
            Q(full_name__icontains=query) | Q(username__icontains=query)
        )
    elif selected_role: 
        users = users.filter(role__role_name=selected_role)

    not_found = not users.exists()

    return render(request, 'user_list.html', {
        'users': users,
        'query': query,
        'roles': roles,
        'selected_role': selected_role,
        'not_found': not_found,
    })

def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile = user.profile if hasattr(user, 'profile') else None
    personalization = UserPersonalization.objects.filter(user=user).first()

    return render(request, 'user_detail.html', {
        'user': user,
        'profile': profile,
        'personalization': personalization,
    })

def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile = UserProfile.objects.filter(user=user).first()

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user

            interests = request.POST.getlist('interests')  
            profile.interests = ', '.join(interests)  
            profile.save()
            
            # Lưu dữ liệu cá nhân hóa
            save_personalization_data(user)
            messages.success(request, "Cập nhật người dùng thành công!")
            return redirect('user:user_list')
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile) if profile else UserProfileForm()

    return render(request, 'user_form.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def user_add(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user

            interests = request.POST.getlist('interests') 
            profile.interests = ', '.join(interests)  
            profile.save()

            # Lưu dữ liệu cá nhân hóa
            save_personalization_data(user)
            messages.success(request, "Thêm người dùng thành công!")
            return redirect('user:user_list')
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'user_form.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Đã xóa người dùng thành công!")
        return redirect('user:user_list')  
    
    return render(request, 'user_confirm_delete.html', {'user': user})


def export_users(request):

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=lms_users.xlsx'
    
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Users'
    
    columns = [
        'username', 'password', 'email', 'full_name', 'role_id', 'role_name', 'profile_picture_url',
        'bio', 'interests', 'learning_style', 'preferred_language'
    ]
    worksheet.append(columns)
    users = User.objects.all()

    for user in users:
        profile = getattr(user, 'profile', None)
        worksheet.append([
            user.username,
            '*********',
            user.email,
            user.full_name,
            user.role.id if user.role else '',
            user.role.role_name if user.role else '',
            user.profile_picture_url,
            getattr(profile, 'bio', ''),
            getattr(profile, 'interests', ''),
            getattr(profile, 'learning_style', ''),
            getattr(profile, 'preferred_language', '')
        ])

    workbook.save(response)

    return response

    

def import_users(request):
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['excel_file']
            try:
                df = pd.read_excel(uploaded_file)
                users_imported = 0  
                for index, row in df.iterrows():
                    username = row.get("username")
                    password = str(row.get("password"))
                    email = row.get("email")
                    full_name = row.get("full_name")
                    role_id = row.get("role_id")
                    profile_picture_url = row.get("profile_picture_url", "")

                    bio = row.get("bio", "")
                    interests = row.get("interests", "")
                    learning_style = row.get("learning_style", "")
                    preferred_language = row.get("preferred_language", "")

                    user = User(
                        username=username,
                        password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                        email=email,
                        full_name=full_name,
                        role_id=role_id,
                        profile_picture_url=profile_picture_url
                    )
                    user.save()

                    user_profile = UserProfile(
                        user=user,
                        bio=bio,
                        interests=interests,
                        learning_style=learning_style,
                        preferred_language=preferred_language
                    )
                    user_profile.save()
                    save_personalization_data(user)
                    users_imported += 1
                
                messages.success(request, f"Đã nhập thành công {users_imported} người dùng!")
                return redirect('user:user_list')

            except Exception as e:
                messages.error(request, f"Đã xảy ra lỗi khi nhập dữ liệu: {str(e)}")
    else:
        form = ExcelImportForm()

    return render(request, 'user_list.html', {'form': form})