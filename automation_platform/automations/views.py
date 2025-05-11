from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Automation, AutomationExecution
from .forms import AutomationForm, AutomationExecutionForm
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
        form = AutomationForm(request.POST)
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
    
    if request.method == 'POST':
        form = AutomationExecutionForm(request.POST)
        if form.is_valid():
            execution = AutomationExecution.objects.create(
                automation=automation,
                user=request.user,
                parameters=form.cleaned_data.get('parameters', {}),
                status='pending'
            )
            
            # Burada otomasyonu çalıştırma mantığı olacak
            # Şimdilik sadece başarılı olarak işaretleyelim
            execution.status = 'completed'
            execution.completed_at = timezone.now()
            execution.result = {'message': 'Otomasyon başarıyla çalıştırıldı.'}
            execution.save()
            
            messages.success(request, 'Otomasyon başarıyla çalıştırıldı.')
            return redirect('automation_detail', pk=automation.pk)
    else:
        form = AutomationExecutionForm()
    
    return render(request, 'automations/automation_execute.html', {
        'automation': automation,
        'form': form
    })