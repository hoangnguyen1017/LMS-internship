from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models import User, Profile, Role
from .forms import UserForm, UserEditForm
from .widgets import PasswordWidget

class UserProfileResource(resources.ModelResource):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'profile__role__role_name',  
            'profile__profile_picture_url',
            'profile__bio',
            'profile__interests',
            'profile__learning_style',
            'profile__preferred_language',
        )

    def after_import(self, dataset, result, **kwargs):
        for row in dataset.dict:
            user_id = row.get('id')
            
            # Kiểm tra xem user_id có hợp lệ hay không
            if not user_id:
                continue  # Bỏ qua nếu user_id không tồn tại trong dòng
            
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                print(f"User with ID {user_id} does not exist. Skipping this entry.")
                continue  # Bỏ qua nếu không tìm thấy người dùng

            # Kiểm tra xem người dùng có phải là superuser không
            if user.is_superuser:
                continue  # Bỏ qua người dùng là superuser

            # Lấy hoặc tạo Role
            role_name = row.get('profile__role__role_name')
            if not role_name:
                role_name = "N/A"  # Gán "N/A" nếu không có role_name

            # Lấy hoặc tạo Role với role_name là "N/A"
            role, created = Role.objects.get_or_create(role_name=role_name)

            # Tạo thông tin cho Profile
            profile_data = {
                'role': role,  # Gán đối tượng Role
                'profile_picture_url': row.get('profile__profile_picture_url'),
                'bio': row.get('profile__bio'),
                'interests': row.get('profile__interests'),
                'learning_style': row.get('profile__learning_style'),
                'preferred_language': row.get('profile__preferred_language'),
            }

            # Lấy hoặc tạo Profile
            profile, created = Profile.objects.get_or_create(user=user, defaults=profile_data)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = True
    verbose_name_plural = 'Profile'

class CustomUserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    resource_class = UserProfileResource
    list_display = ('username', 'first_name', 'last_name', 'email', 'get_role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups')
    readonly_fields = ('date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Modules', {'fields': ('modules',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active', 'modules')}
        ),
    )
    filter_horizontal = ('groups', 'user_permissions', 'modules')

    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    inlines = [ProfileInline]

    def get_role(self, obj):
        return obj.profile.role.role_name if hasattr(obj, 'profile') and obj.profile.role else 'No Role'
    get_role.short_description = 'Role'

if User in admin.site._registry:
    admin.site.unregister(User)

admin.site.register(User, CustomUserAdmin)

from import_export import resources
from .models import Student

class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        fields = ('id', 'student_code', 'user__username', 'user__first_name', 'user__last_name', 'user__email', 'enrolled_courses')
        export_order = ('id', 'student_code', 'user__username', 'user__first_name', 'user__last_name', 'user__email', 'enrolled_courses')

class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource
    list_display = ('student_code', 'user', 'enrolled_courses_display')
    search_fields = ('student_code', 'user__username', 'user__email', 'user__first_name', 'user__last_name')
    inlines = [ProfileInline]

    def enrolled_courses_display(self, obj):
        return ", ".join(course.course_name for course in obj.enrolled_courses.all())  
    enrolled_courses_display.short_description = 'Enrolled Courses'

admin.site.register(Student, StudentAdmin)
