from user.models import Profile

def profile_completion_percentage(request):
    if request.user.is_authenticated:  # Kiểm tra nếu người dùng đã đăng nhập
        try:
            profile = Profile.objects.get(user=request.user)
            completion_percentage = profile.calculate_completion_percentage()
            return {'completion_percentage': completion_percentage}
        except Profile.DoesNotExist:
            return {'completion_percentage': 0}  # Trả về 0 nếu không có profile
    return {'completion_percentage': None}  # Trả về None nếu người dùng không đăng nhập
