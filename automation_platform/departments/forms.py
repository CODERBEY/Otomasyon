from django import forms
from .models import Department, DepartmentMember

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'description', 'parent', 'manager', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Departman Adi',
            'code': 'Departman Kodu',
            'description': 'Açiklama',
            'parent': 'Üst Departman',
            'manager': 'Departman Yöneticisi',
            'is_active': 'Aktif',
        }

class DepartmentMemberForm(forms.ModelForm):
    class Meta:
        model = DepartmentMember
        fields = ['user', 'is_primary']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'user': 'Kullanici',
            'is_primary': 'Ana Departman',
        }