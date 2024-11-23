from django.shortcuts import render, get_object_or_404, redirect
from role.models import Role, RoleModule
from role.forms import RoleForm, ExcelImportForm
import pandas as pd
from django.contrib import messages
from django.http import HttpResponse
import openpyxl
from module_group.models import ModuleGroup, Module
from django.contrib.auth.models import Permission
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from user.models import Profile
from .admin import RoleResource
from tablib import Dataset
from django.core.files.uploadedfile import UploadedFile

def role_list(request):
    roles = Role.objects.all()  # Lấy danh sách tất cả các role
    role_modules = RoleModule.objects.all()  # Lấy tất cả RoleModule (Role - Module liên kết)

    form = ExcelImportForm()  # Form nhập liệu Excel (nếu có)

    return render(request, 'role_list.html', {
        'roles': roles,
        'form': form,
        'role_modules': role_modules
    })


def role_add(request, role_id=None):
    if role_id:  # Nếu đang chỉnh sửa một role hiện có
        role = get_object_or_404(Role, id=role_id)
        form = RoleForm(request.POST or None, instance=role)
    else:  # Nếu đang tạo mới một role
        role = None
        form = RoleForm(request.POST or None)

    all_modules = Module.objects.all()  # Lấy tất cả các module

    if request.method == 'POST':
        if form.is_valid():
            new_role = form.save()  # Lưu role
            selected_modules_ids = request.POST.getlist('modules')  # Lấy danh sách module được chọn

            # Cập nhật RoleModule (thêm hoặc xóa các module liên quan)
            RoleModule.objects.filter(role=new_role).delete()  # Xóa các liên kết cũ
            for module_id in selected_modules_ids:
                module = Module.objects.get(id=module_id)
                RoleModule.objects.create(role=new_role, module=module)

            # Thông báo thành công và chuyển hướng
            messages.success(request, 'Role and associated modules have been successfully added/updated.')
            return redirect('role:role_list')

    # Xác định các module đã được chọn (nếu đang chỉnh sửa)
    selected_modules = (
        RoleModule.objects.filter(role=role).values_list('module', flat=True) if role else []
    )

    context = {
        'form': form,
        'all_modules': all_modules,
        'selected_modules': selected_modules,
    }
    return render(request, 'role_form.html', context)

def role_edit(request, pk):
    role = get_object_or_404(Role, pk=pk)  # Lấy role cần chỉnh sửa
    form = RoleForm(request.POST or None, instance=role)  # Tạo form liên kết với role
    all_modules = Module.objects.all()  # Lấy danh sách tất cả module

    if request.method == 'POST':
        if form.is_valid():
            updated_role = form.save()  # Lưu role

            # Lấy danh sách module được chọn từ form
            selected_modules_ids = request.POST.getlist('modules')

            # Cập nhật RoleModule (xóa các liên kết cũ và thêm mới)
            RoleModule.objects.filter(role=updated_role).delete()  # Xóa liên kết cũ
            for module_id in selected_modules_ids:
                module = Module.objects.get(id=module_id)
                RoleModule.objects.create(role=updated_role, module=module)

            # Thông báo thành công và chuyển hướng
            messages.success(request, 'Role and associated modules have been successfully updated.')
            return redirect('role:role_list')

    # Lấy danh sách module đã được chọn để hiển thị
    selected_modules = RoleModule.objects.filter(role=role).values_list('module', flat=True)

    context = {
        'form': form,
        'all_modules': all_modules,
        'selected_modules': selected_modules,
    }
    return render(request, 'role_form.html', context)


def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.delete()
        return redirect('role:role_list')
    return render(request, 'role_confirm_delete.html', {'role': role})


def export_roles(request):
    # Tạo resource
    resource = RoleResource()
    queryset = Role.objects.all()

    # Xuất dữ liệu
    dataset = resource.export(queryset)

    # Tạo phản hồi với định dạng Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=lms_roles.xlsx'

    # Ghi dữ liệu vào phản hồi dưới dạng XLSX
    response.write(dataset.xlsx)  # Đảm bảo sử dụng đúng phương thức để xuất ra xlsx

    return response



def import_roles(request):
    resource = RoleResource()

    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')

        # Kiểm tra xem file có được tải lên không
        if not uploaded_file:
            messages.error(request, "Không tìm thấy tệp tin để nhập.")
            return redirect('role:role_list')

        if uploaded_file.size == 0:  # Kiểm tra nếu tệp rỗng
            messages.error(request, "Tệp không được để trống.")
            return redirect('role:role_list')

        file_format = uploaded_file.name.split('.')[-1].lower()
        dataset = Dataset()

        # Xử lý định dạng tệp
        formats = {
            'csv': lambda: dataset.load(uploaded_file.read().decode('utf-8'), format='csv'),
            'json': lambda: dataset.load(uploaded_file.read().decode('utf-8'), format='json'),
            'yaml': lambda: dataset.load(uploaded_file.read().decode('utf-8'), format='yaml'),
            'tsv': lambda: dataset.load(uploaded_file.read().decode('utf-8'), format='tsv'),
            'xlsx': lambda: dataset.load(uploaded_file.read(), format='xlsx'),
        }

        # Kiểm tra và xử lý tệp
        try:
            if file_format in formats:
                formats[file_format]()  # Gọi hàm xử lý định dạng
            else:
                messages.error(request, "Định dạng tệp không hợp lệ. Hỗ trợ các định dạng: csv, json, yaml, tsv, xlsx.")
                return redirect('role:role_list')
        except Exception as e:
            messages.error(request, f"Lỗi khi đọc tệp: {e}")
            return redirect('role:role_list')

        # Kiểm tra và nhập dữ liệu
        result = resource.import_data(dataset, dry_run=True)

        if not result.has_validation_errors():
            resource.import_data(dataset, dry_run=False)
            messages.success(request, "Người dùng đã được nhập thành công!")
        else:
            invalid_rows = result.invalid_rows
            error_messages = [f"Lỗi tại hàng {row['row']}: {row['error']}" for row in invalid_rows]
            messages.error(request, "Có lỗi khi nhập người dùng:\n" + "\n".join(error_messages))

        return redirect('role:role_list')

    messages.error(request, "Không thể nhập người dùng.")
    return redirect('role:role_list')


@login_required
def select_role(request):
    if request.method == 'POST':
        selected_role_name = request.POST.get('role')  # Lấy role_name thay vì id
        if selected_role_name:
            try:
                role = Role.objects.get(role_name=selected_role_name)
                if request.user.is_superuser:
                    request.session['temporary_role'] = role.role_name
                    messages.success(request, "Vai trò tạm thời đã được lưu.")
                else:
                    profile = Profile.objects.get(user=request.user)
                    profile.role = role
                    profile.save()
                    messages.success(request, "Vai trò đã được cập nhật.")
            except Role.DoesNotExist:
                messages.error(request, "Vai trò không tồn tại.")
            except Profile.DoesNotExist:
                messages.error(request, "User này chưa có hồ sơ.")
        else:
            messages.warning(request, "Vui lòng chọn một vai trò.")
    return redirect('main:home')



@login_required
@user_passes_test(lambda u: u.is_superuser)
def reset_role(request):
    if request.method == 'POST':
        # Xóa role tạm thời khỏi session
        if 'temporary_role' in request.session:
            del request.session['temporary_role']
            messages.success(request, "Vai trò tạm thời đã được đặt lại. Bạn đã khôi phục quyền superuser.")
        else:
            messages.info(request, "Không có vai trò tạm thời nào để đặt lại.")

    return redirect('main:home')


def role_permissions(request, role_id):
    role = get_object_or_404(Role, id=role_id)

    specific_permissions = Role._meta.permissions
    all_permissions = Permission.objects.filter(
        codename__in=[codename for codename, _ in specific_permissions]
    )
    
    all_modules = Module.objects.all()
    selected_modules = role.modules.all()
    
    if request.method == "POST":
        selected_permissions = request.POST.getlist('permissions')
        selected_modules_ids = request.POST.getlist('modules')
        
        # Update permissions and modules for the role
        role.permissions.set(Permission.objects.filter(id__in=selected_permissions))
        role.modules.set(Module.objects.filter(id__in=selected_modules_ids))
        role.save()

        # Add a success message
        messages.success(request, 'Permissions and modules updated successfully.')

        # Redirect to role list after saving
        return redirect('role:role_list')

    context = {
        'role': role,
        'all_permissions': all_permissions,
        'selected_permissions': role.permissions.all(),
        'all_modules': all_modules,
        'selected_modules': selected_modules,
    }
    return render(request, 'role_permission.html', context)
