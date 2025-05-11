from django import forms
from .models import Automation, AutomationExecution
from departments.models import Department
import json

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
                 'entry_point', 'parameters', 'departments', 'project_path',
                 'input_fields', 'output_format', 'ui_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fa-robot'}),
            'entry_point': forms.TextInput(attrs={'class': 'form-control'}),
            'parameters': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'project_path': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'external_projects.departman_a.excel_processor.main'}),
            'input_fields': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': '[{"name": "input_file", "type": "file", "label": "Excel Dosyası", "required": true}]'}),
            'output_format': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'json'}),
            'ui_type': forms.Select(attrs={'class': 'form-control'}),
            'usage_guide': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
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
            'project_path': 'Proje Yolu',
            'input_fields': 'Giriş Alanları (JSON)',
            'output_format': 'Çıktı Formatı',
            'ui_type': 'Arayüz Tipi',
            'usage_guide': 'Kullanım Kılavuzu',
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

class DynamicAutomationForm(forms.Form):
    def __init__(self, automation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # input_fields JSON'dan form alanları oluştur
        for field in automation.input_fields:
            field_type = field.get('type', 'text')
            required = field.get('required', False)
            label = field.get('label', field['name'])
            help_text = field.get('help_text', '')
            
            if field_type == 'text':
                self.fields[field['name']] = forms.CharField(
                    label=label,
                    required=required,
                    help_text=help_text,
                    widget=forms.TextInput(attrs={'class': 'form-control'})
                )
            elif field_type == 'textarea':
                self.fields[field['name']] = forms.CharField(
                    label=label,
                    required=required,
                    help_text=help_text,
                    widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
                )
            elif field_type == 'number':
                self.fields[field['name']] = forms.IntegerField(
                    label=label,
                    required=required,
                    help_text=help_text,
                    widget=forms.NumberInput(attrs={'class': 'form-control'})
                )
            elif field_type == 'file':
                self.fields[field['name']] = forms.FileField(
                    label=label,
                    required=required,
                    help_text=help_text,
                    widget=forms.FileInput(attrs={'class': 'form-control'})
                )
            elif field_type == 'select':
                choices = [(opt, opt) for opt in field.get('options', [])]
                self.fields[field['name']] = forms.ChoiceField(
                    label=label,
                    required=required,
                    help_text=help_text,
                    choices=choices,
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
            elif field_type == 'checkbox':
                self.fields[field['name']] = forms.BooleanField(
                    label=label,
                    required=required,
                    help_text=help_text,
                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
                )
            elif field_type == 'date':
                self.fields[field['name']] = forms.DateField(
                    label=label,
                    required=required,
                    help_text=help_text,
                    widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
                )
            elif field_type == 'email':
                self.fields[field['name']] = forms.EmailField(
                    label=label,
                    required=required,
                    help_text=help_text,
                    widget=forms.EmailInput(attrs={'class': 'form-control'})
                )