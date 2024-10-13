from django.contrib import admin
from .models import Role

class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name',)
    search_fields = ('role_name',)
    filter_horizontal = ('permissions', 'modules')  # Cho phép chọn nhiều quyền và module

# Đăng ký mô hình Role với admin
admin.site.register(Role, RoleAdmin)