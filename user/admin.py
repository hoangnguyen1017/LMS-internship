from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models import User, Profile
from .forms import UserForm, UserEditForm
from .widgets import PasswordWidget

from .models import User, Profile 
from import_export import resources
from import_export.admin import ImportExportModelAdmin

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

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = True
    verbose_name_plural = 'Profile'

class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource
    list_display = ('student_code', 'user', 'enrolled_courses_display')
    search_fields = ('student_code', 'user__username', 'user__email', 'user__first_name', 'user__last_name')
    inlines = [ProfileInline]

    def enrolled_courses_display(self, obj):
        return ", ".join(course.course_name for course in obj.enrolled_courses.all())  
    enrolled_courses_display.short_description = 'Enrolled Courses'


admin.site.register(Student, StudentAdmin)