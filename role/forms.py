from django import forms
from .models import Role

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = [
            'role_name',
            'can_view_admin_dashboard',
            'can_view_manager_dashboard',
            'can_view_user_dashboard',
            'can_edit_roles',           # Thêm trường mới
            'can_view_users',           # Thêm trường mới
        ]
        widgets = {
            'role_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter role name'
            }),
            'can_view_admin_dashboard': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'can_view_manager_dashboard': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'can_view_user_dashboard': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'can_edit_roles': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'can_view_users': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        # Tùy chỉnh label cho các trường
        self.fields['role_name'].label = "Role Name"
        self.fields['can_view_admin_dashboard'].label = "Can View Admin Dashboard"
        self.fields['can_view_manager_dashboard'].label = "Can View Manager Dashboard"
        self.fields['can_view_user_dashboard'].label = "Can View User Dashboard"
        self.fields['can_edit_roles'].label = "Can Edit Roles"
        self.fields['can_view_users'].label = "Can View Users"

class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File", widget=forms.ClearableFileInput(attrs={
        'class': 'form-control-file'
    }))
