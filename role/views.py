from django.shortcuts import render, get_object_or_404, redirect
from .models import Role
from .forms import RoleForm, ExcelImportForm
import pandas as pd
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
import openpyxl

def role_list(request):
    # Kiểm tra nếu người dùng có thuộc tính role
    if hasattr(request.user, 'role'):
        if not request.user.role.can_view_users:  # Kiểm tra quyền truy cập
            return HttpResponseForbidden("You do not have permission to view this page.")
    else:
        return HttpResponseForbidden("You do not have permission to view this page.")

    # Lấy danh sách các vai trò (Roles)
    roles = Role.objects.all()
    return render(request, 'role/role_list.html', {'roles': roles})

# Thêm vai trò mới
def role_add(request):
    # Kiểm tra quyền truy cập
    if not request.user.role.can_edit_roles:
        return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")
    
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save(commit=False)
            role.can_view_admin_dashboard = request.POST.get('can_view_admin_dashboard') == 'on'
            role.can_view_manager_dashboard = request.POST.get('can_view_manager_dashboard') == 'on'
            role.can_view_user_dashboard = request.POST.get('can_view_user_dashboard') == 'on'
            role.save()
            messages.success(request, 'Role added successfully!')
            return redirect('role:role_list')
    else:
        form = RoleForm()
    return render(request, 'role_form.html', {'form': form})

# Chỉnh sửa vai trò
def role_edit(request, pk):
    role = get_object_or_404(Role, pk=pk)
    
    # Kiểm tra quyền truy cập
    if not request.user.role.can_edit_roles:
        return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")
    
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            role = form.save(commit=False)
            role.can_view_admin_dashboard = request.POST.get('can_view_admin_dashboard') == 'on'
            role.can_view_manager_dashboard = request.POST.get('can_view_manager_dashboard') == 'on'
            role.can_view_user_dashboard = request.POST.get('can_view_user_dashboard') == 'on'
            role.save()
            messages.success(request, 'Role updated successfully!')
            return redirect('role:role_list')
    else:
        form = RoleForm(instance=role)
    return render(request, 'role_form.html', {'form': form})

# Xóa vai trò
def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)
    
    # Kiểm tra quyền truy cập
    if not request.user.role.can_edit_roles:
        return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")
    
    if request.method == 'POST':
        role.delete()
        messages.success(request, 'Role deleted successfully!')
        return redirect('role:role_list')
    return render(request, 'role_confirm_delete.html', {'role': role})

# Xuất vai trò ra Excel
def export_roles(request):
    # Kiểm tra quyền truy cập
    if not request.user.role.can_view_users:
        return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=lms_roles.xlsx'
    
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Roles'
    
    # Định nghĩa các cột
    columns = ['role_name', 'can_view_admin_dashboard', 'can_view_manager_dashboard', 'can_view_user_dashboard']
    worksheet.append(columns)
    
    # Lấy tất cả các vai trò và ghi vào file Excel
    for role in Role.objects.all():
        worksheet.append([role.role_name, role.can_view_admin_dashboard, role.can_view_manager_dashboard, role.can_view_user_dashboard])
    
    workbook.save(response)
    return response

# Nhập vai trò từ file Excel
def import_roles(request):
    # Kiểm tra quyền truy cập
    if not request.user.role.can_edit_roles:
        return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")
    
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['excel_file']
            try:
                df = pd.read_excel(uploaded_file)
                roles_imported = 0  # Counter for imported roles

                for index, row in df.iterrows():
                    role_name = row.get("role_name")  # Assuming you only need role_name

                    # Kiểm tra xem vai trò đã tồn tại hay chưa
                    if not Role.objects.filter(role_name=role_name).exists():
                        # Tạo và lưu vai trò mới
                        Role.objects.create(
                            role_name=role_name
                        )
                        roles_imported += 1
                    else:
                        messages.warning(request, f"Role '{role_name}' already exists. Skipping.")

                if roles_imported > 0:
                    messages.success(request, f"{roles_imported} roles imported successfully!")
                else:
                    messages.warning(request, "No roles were imported.")

            except Exception as e:
                messages.error(request, f"An error occurred during import: {e}")

            return redirect('role:role_list')
    else:
        form = ExcelImportForm()

    return render(request, 'role_list.html', {'form': form})

# Dashboard dành cho Admin
def admin_dashboard(request):
    if not request.user.role.can_view_admin_dashboard:
        return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")
    return render(request, 'admin_dashboard.html')

# Dashboard dành cho Manager
def manager_dashboard(request):
    if not request.user.role.can_view_manager_dashboard:
        return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")
    return render(request, 'manager_dashboard.html')

# Dashboard dành cho User
def user_dashboard(request):
    if not request.user.role.can_view_user_dashboard:
        return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")
    return render(request, 'user_dashboard.html')
