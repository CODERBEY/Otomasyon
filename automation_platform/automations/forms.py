from django import forms
from .models import Automation, AutomationExecution
from departments.models import Department

class AutomationForm(forms.ModelForm):
    departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Departmanlar'
    )
    
    class Meta:
        model = Automation
        fields = ['name', 'code', 'description', 'type', 'status', 'icon', 
                 'entry_point', 'parameters', 'departments']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fa-robot'}),
            'entry_point': forms.TextInput(attrs={'class': 'form-control'}),
            'parameters': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'name': 'Otomasyon Adi',
            'code': 'Otomasyon Kodu',
            'description': 'Aciklama',
            'type': 'Otomasyon Tipi',
            'status': 'Durum',
            'icon': 'Ikon',
            'entry_point': 'Giris Noktasi',
            'parameters': 'Parametreler (JSON)',
        }

class AutomationExecutionForm(forms.Form):
    parameters = forms.JSONField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': '{"param1": "value1", "param2": "value2"}'
        }),
        label='Parametreler'
    )