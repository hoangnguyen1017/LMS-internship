from django.urls import path
from . import views

app_name = 'role'

urlpatterns = [
    # Danh sách các vai trò
    path('roles/', views.role_list, name='role_list'),
    
    # Thêm vai trò mới
    path('roles/create/', views.role_add, name='role_add'),
    
    # Chỉnh sửa vai trò
    path('roles/edit/<int:pk>/', views.role_edit, name='role_edit'),
    
    # Xóa vai trò
    path('roles/delete/<int:pk>/', views.role_delete, name='role_delete'),
    
    # Nhập vai trò từ file Excel
    path('import/', views.import_roles, name='import_roles'),
    
    # Xuất vai trò ra file Excel
    path('export/', views.export_roles, name='export_roles'),
]
