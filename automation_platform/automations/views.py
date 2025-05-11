from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from .models import Automation, AutomationExecution
from .forms import AutomationForm, AutomationExecutionForm, DynamicAutomationForm
from .runners import SafeProjectRunner
from departments.models import DepartmentMember

@login_required
def automation_list(request):
    # Kullanıcının departmanlarını al
    user_departments = DepartmentMember.objects.filter(
        user=request.user
    ).values_list('department', flat=True)
    
    # Kullanıcının erişebileceği otomasyonları filtrele
    automations = Automation.objects.filter(
        departments__in=user_departments
    ).distinct()
    
    # Eğer kullanıcı staff ise tüm otomasyonları göster
    if request.user.is_staff:
        automations = Automation.objects.all()
    
    return render(request, 'automations/automation_list.html', {
        'automations': automations
    })

@login_required
def automation_create(request):
    if not request.user.is_staff:
        messages.error(request, 'Bu işlem için yetkiniz yok.')
        return redirect('automation_list')
    
    if request.method == 'POST':
        form = AutomationForm(request.POST, request.FILES)
        if form.is_valid():
            automation = form.save(commit=False)
            automation.created_by = request.user
            automation.save()
            form.save_m2m()  # Many-to-many ilişkilerini kaydet
            messages.success(request, 'Otomasyon başarıyla oluşturuldu.')
            return redirect('automation_list')
    else:
        form = AutomationForm()
    
    return render(request, 'automations/automation_form.html', {
        'form': form,
        'title': 'Yeni Otomasyon'
    })

@login_required
def automation_detail(request, pk):
    automation = get_object_or_404(Automation, pk=pk)
    
    # Kullanıcının bu otomasyona erişim yetkisi var mı kontrol et
    user_departments = DepartmentMember.objects.filter(
        user=request.user
    ).values_list('department', flat=True)
    
    if not request.user.is_staff and not automation.departments.filter(id__in=user_departments).exists():
        messages.error(request, 'Bu otomasyona erişim yetkiniz yok.')
        return redirect('automation_list')
    
    executions = automation.executions.order_by('-started_at')[:10]
    
    return render(request, 'automations/automation_detail.html', {
        'automation': automation,
        'executions': executions
    })

@login_required
def automation_execute(request, pk):
    automation = get_object_or_404(Automation, pk=pk)
    
    # Kullanıcının bu otomasyona erişim yetkisi var mı kontrol et
    user_departments = DepartmentMember.objects.filter(
        user=request.user
    ).values_list('department', flat=True)
    
    if not request.user.is_staff and not automation.departments.filter(id__in=user_departments).exists():
        messages.error(request, 'Bu otomasyona erişim yetkiniz yok.')
        return redirect('automation_list')
    
    if request.method == 'POST':
        if automation.input_fields:
            # Dinamik form kullan
            form = DynamicAutomationForm(automation, request.POST, request.FILES)
        else:
            # Eski form kullan
            form = AutomationExecutionForm(request.POST)
        
        if form.is_valid():
            # Parametreleri hazırla
            parameters = {}
            user_files = {}
            
            for field_name, field_value in form.cleaned_data.items():
                if hasattr(field_value, 'read'):  # Dosya mı kontrol et
                    user_files[field_name] = field_value
                else:
                    parameters[field_name] = field_value
            
            # Execution kaydı oluştur
            execution = AutomationExecution.objects.create(
                automation=automation,
                user=request.user,
                parameters=parameters,
                status='running'
            )
            
            try:
                # Projeyi çalıştır
                if automation.project_path:
                    # Harici proje çalıştır
                    runner = SafeProjectRunner(automation, parameters, user_files)
                    result = runner.run()
                    
                    if result['status'] == 'success':
                        execution.status = 'completed'
                        execution.result = result.get('output', result)
                        execution.completed_at = timezone.now()
                        execution.save()
                        
                        # Sonuç sayfasına yönlendir
                        return redirect('automation_execution_result', execution_id=execution.id)
                    else:
                        execution.status = 'failed'
                        execution.error_message = result.get('error', 'Bilinmeyen hata')
                        messages.error(request, f'Hata: {execution.error_message}')
                else:
                    # Eski yöntem (dummy implementation)
                    execution.status = 'completed'
                    execution.result = {'message': 'Otomasyon başarıyla çalıştırıldı.'}
                    messages.success(request, 'Otomasyon başarıyla çalıştırıldı.')
                
            except Exception as e:
                execution.status = 'failed'
                execution.error_message = str(e)
                messages.error(request, f'Hata: {str(e)}')
            
            execution.completed_at = timezone.now()
            execution.save()
            
            return redirect('automation_detail', pk=automation.pk)
    else:
        if automation.input_fields:
            form = DynamicAutomationForm(automation)
        else:
            form = AutomationExecutionForm()
    
    return render(request, 'automations/automation_execute.html', {
        'automation': automation,
        'form': form
    })

@login_required
def automation_guide(request):
    return render(request, 'automations/automation_guide.html')

@login_required
def automation_usage_guide(request, pk):
    """Otomasyon kullanım kılavuzunu göster"""
    automation = get_object_or_404(Automation, pk=pk)
    
    # Yetki kontrolü
    user_departments = DepartmentMember.objects.filter(
        user=request.user
    ).values_list('department', flat=True)
    
    if not request.user.is_staff and not automation.departments.filter(id__in=user_departments).exists():
        messages.error(request, 'Bu kılavuza erişim yetkiniz yok.')
        return redirect('automation_list')
    
    return render(request, 'automations/automation_usage_guide.html', {
        'automation': automation
    })

@login_required
@require_http_methods(["GET"])
def automation_result(request, execution_id):
    """Çalıştırma sonucunu göster (API)"""
    execution = get_object_or_404(AutomationExecution, pk=execution_id)
    
    # Yetki kontrolü
    if execution.user != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Yetkiniz yok'}, status=403)
    
    return JsonResponse({
        'status': execution.status,
        'result': execution.result,
        'error_message': execution.error_message,
        'started_at': execution.started_at.isoformat(),
        'completed_at': execution.completed_at.isoformat() if execution.completed_at else None
    })

@login_required
def automation_execution_result(request, execution_id):
    """Çalıştırma sonuçlarını göster (HTML)"""
    execution = get_object_or_404(AutomationExecution, pk=execution_id)
    
    # Yetki kontrolü
    if execution.user != request.user and not request.user.is_staff:
        messages.error(request, 'Bu sonucu görüntüleme yetkiniz yok.')
        return redirect('automation_list')
    
    return render(request, 'automations/execution_result.html', {
        'execution': execution,
        'automation': execution.automation
    })