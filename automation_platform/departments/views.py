from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department, DepartmentMember
from .forms import DepartmentForm

@login_required
def department_list(request):
    departments = Department.objects.all().order_by('name')
    return render(request, 'departments/department_list.html', {
        'departments': departments
    })

@login_required
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save(commit=False)
            department.created_by = request.user
            department.save()
            messages.success(request, 'Departman basariyla olusturuldu.')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    
    return render(request, 'departments/department_form.html', {
        'form': form,
        'title': 'Yeni Departman'
    })

@login_required
def department_detail(request, pk):
    department = get_object_or_404(Department, pk=pk)
    members = department.members.all()
    return render(request, 'departments/department_detail.html', {
        'department': department,
        'members': members
    })