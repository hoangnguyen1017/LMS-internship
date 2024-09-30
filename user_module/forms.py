from django import forms
from .models import UserModule

class UserModuleForm(forms.ModelForm):
    class Meta:
        model = UserModule
        fields = ['user', 'module']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'module': forms.Select(attrs={'class': 'form-control'}),
        }
