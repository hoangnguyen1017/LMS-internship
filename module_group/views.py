from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Module, ModuleGroup
from .forms import ModuleForm, ModuleGroupForm, ExcelImportForm
import pandas as pd
import openpyxl
from django.db.models import Q

# MODULE GROUP VIEWS
from functools import wraps

def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('main:login')  # Chuyển hướng đến trang đăng nhập
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required

def module_group_list(request):
    module_groups = ModuleGroup.objects.all()
    form = ExcelImportForm()
    return render(request, 'module_group_list.html', {'module_groups': module_groups, 'form': form})

def module_group_detail(request, pk):
    module_group = get_object_or_404(ModuleGroup, pk=pk)
    return render(request, 'module_group_detail.html', {'module_group': module_group})

def module_group_add(request):
    if request.method == 'POST':
        form = ModuleGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('module_group:module_group_list')
    else:
        form = ModuleGroupForm()
    return render(request, 'module_group_form.html', {'form': form})

def module_group_edit(request, pk):
    module_group = get_object_or_404(ModuleGroup, pk=pk)
    if request.method == 'POST':
        form = ModuleGroupForm(request.POST, instance=module_group)
        if form.is_valid():
            form.save()
            return redirect('module_group:module_group_list')
    else:
        form = ModuleGroupForm(instance=module_group)
    return render(request, 'module_group_form.html', {'form': form})

def module_group_delete(request, pk):
    module_group = get_object_or_404(ModuleGroup, pk=pk)
    if request.method == 'POST':
        module_group.delete()
        return redirect('module_group:module_group_list')
    return render(request, 'module_group_confirm_delete.html', {'module_group': module_group})

# EXPORT AND IMPORT MODULE GROUPS

def export_module_groups(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=lms_module_groups.xlsx'
    
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Module_Group'
    
    # Define the columns
    columns = ['group_name']
    worksheet.append(columns)
    
    # Fetch all ModuleGroups and write to the Excel file
    for module_group in ModuleGroup.objects.all():
        worksheet.append([module_group.group_name])
    
    workbook.save(response)
    return response

def import_module_groups(request):
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['excel_file']
            try:
                df = pd.read_excel(uploaded_file)
                module_group_imported = 0

                for index, row in df.iterrows():
                    group_name = row.get("group_name")
                    if not ModuleGroup.objects.filter(group_name=group_name).exists():
                        ModuleGroup.objects.create(group_name=group_name)
                        module_group_imported += 1
                    else:
                        messages.warning(request, f"Module Group '{group_name}' already exists. Skipping.")

                if module_group_imported > 0:
                    messages.success(request, f"{module_group_imported} module groups imported successfully!")
                else:
                    messages.warning(request, "No module groups were imported.")

            except Exception as e:
                messages.error(request, f"An error occurred during import: {e}")
            return redirect('module_group:module_group_list')
    else:
        form = ExcelImportForm()
    return render(request, 'module_group_list.html', {'form': form})


# MODULE VIEWS

def module_list(request):
    query = request.GET.get('q')
    if query:
        modules = Module.objects.filter(
            Q(module_name__icontains=query) |
            Q(module_group__group_name__icontains=query)
        )
    else:
        modules = Module.objects.all()

    module_groups = ModuleGroup.objects.all()
    form = ExcelImportForm()
    return render(request, 'module_list.html', {'module_groups': module_groups, 'modules': modules, 'form': form})

def module_detail(request, pk):
    module = get_object_or_404(Module, pk=pk)
    return render(request, 'module_detail.html', {'module': module})

def module_add(request):
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('module_group:module_list')
    else:
        form = ModuleForm()
    return render(request, 'module_form.html', {'form': form})

def module_edit(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            return redirect('module_group:module_list')
    else:
        form = ModuleForm(instance=module)
    return render(request, 'module_form.html', {'form': form})

def module_delete(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        module.delete()
        return redirect('module_group:module_list')
    return render(request, 'module_confirm_delete.html', {'module': module})

# EXPORT AND IMPORT MODULES

def export_modules(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=lms_modules.xlsx'
    
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Modules'
    
    # Define the columns
    columns = ['module_name', 'module_url', 'icon', 'module_group_id', 'module_group_name']
    worksheet.append(columns)
    
    # Fetch all modules and write to the Excel file
    for module in Module.objects.all():
        worksheet.append([module.module_name, module.module_url, module.icon, module.module_group.id, module.module_group.group_name])
    
    workbook.save(response)
    return response

def import_modules(request):
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['excel_file']
            try:
                df = pd.read_excel(uploaded_file)
                module_imported = 0

                for index, row in df.iterrows():
                    module_name = row['module_name']
                    module_url = row['module_url']
                    icon = row['icon']
                    module_group_id = row['module_group_id']

                    if not Module.objects.filter(module_name=module_name).exists():
                        try:
                            module_group = ModuleGroup.objects.get(id=module_group_id)
                            Module.objects.create(
                                module_name=module_name,
                                module_url=module_url,
                                icon=icon,
                                module_group=module_group
                            )
                            module_imported += 1
                        except ModuleGroup.DoesNotExist:
                            messages.warning(request, f"ModuleGroup with ID '{module_group_id}' does not exist. Skipping module '{module_name}'.")
                    else:
                        messages.warning(request, f"Module '{module_name}' already exists. Skipping.")

                if module_imported > 0:
                    messages.success(request, f"{module_imported} modules imported successfully!")
                else:
                    messages.warning(request, "No modules were imported.")

            except Exception as e:
                messages.error(request, f"An error occurred during import: {e}")
            return redirect('module_group:module_list')
    else:
        form = ExcelImportForm()
    return render(request, 'module_list.html', {'form': form})
