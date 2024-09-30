from django.shortcuts import render, get_object_or_404, redirect
from .models import User, UserProfile, Role, UserPersonalization
from .forms import UserForm, UserProfileForm
from django.db.models import Q
from django.contrib import messages
import joblib
import pickle
# Định nghĩa lộ trình học tập cho các phong cách
learning_paths = [
    "Visual",
    "Auditory",
    "Logical",
]

# Tải mô hình từ file .pkl
model_path = r'C:\Users\ADMIN\Downloads\OJT\naive_bayes_model.pkl'
model = joblib.load(model_path)  # Cập nhật đường dẫn chính xác đến file model
vectorizer_path = r'C:\Users\ADMIN\Downloads\OJT\vectorizer.pkl'
vectorizer = joblib.load(vectorizer_path)  # Nếu bạn cũng lưu vectorizer

def recommend_courses(user):
    # Lấy thông tin sở thích và phong cách học tập của người dùng
    interests = user.profile.interests.lower().split(', ') if user.profile and user.profile.interests else []
    learning_style = user.profile.learning_style or "Visual"

    # Biến lưu khóa học được đề xuất
    recommended_courses = set()  # Sử dụng set để tránh trùng lặp khóa học
    personalized_learning_path = []  # Danh sách lộ trình học tập cá nhân hóa

    # Dự đoán khóa học dựa trên Learning Style và Interest
    for interest in interests:
        combined_input = f"{learning_style} {interest}"
        input_vector = vectorizer.transform([combined_input])
        predicted_course = model.predict(input_vector)[0]  # Dự đoán khóa học

        if predicted_course:
            recommended_courses.add(predicted_course)

    # Lấy danh sách phong cách học còn lại
    remaining_styles = [style for style in learning_paths if style != learning_style]

    # Thêm khóa học liên quan đến Learning Style và Interest vào personalized_learning_path
    for style in remaining_styles:
        courses_for_style = []  # Danh sách các khóa học cho phong cách hiện tại
        for interest in interests:
            combined_input = f"{style} {interest}"
            input_vector = vectorizer.transform([combined_input])
            related_course = model.predict(input_vector)[0]  # Dự đoán khóa học liên quan

            if related_course:
                courses_for_style.append(related_course)  # Thêm khóa học vào danh sách
        if courses_for_style:
            # Thêm phong cách học tập và các khóa học vào personalized_learning_path
            personalized_learning_path.append(f"{style}: " + " ".join(courses_for_style))
        

    return list(recommended_courses), personalized_learning_path, learning_style

def save_personalization_data(user):
    recommended_courses, personalized_learning_path, learning_style = recommend_courses(user)
    personalization, created = UserPersonalization.objects.get_or_create(user=user)
    personalization.recommended_courses = ', '.join(recommended_courses)
    personalization.personalized_learning_path = ', '.join(personalized_learning_path)  # Chuyển thành chuỗi
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
            # Xử lý nhiều lựa chọn cho 'interests'
            interests = request.POST.getlist('interests')  # Lấy danh sách các lựa chọn từ form
            profile.interests = ', '.join(interests)  # Lưu trữ dưới dạng chuỗi phân tách bằng dấu phẩy
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
            # Xử lý nhiều lựa chọn cho 'interests'
            interests = request.POST.getlist('interests')  # Lấy danh sách các lựa chọn từ form
            profile.interests = ', '.join(interests)  # Lưu trữ dưới dạng chuỗi phân tách bằng dấu phẩy
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
