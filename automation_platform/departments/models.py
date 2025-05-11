from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User

class Department(models.Model):
    name = models.CharField(_('Departman Adi'), max_length=100, unique=True)
    code = models.CharField(_('Departman Kodu'), max_length=20, unique=True)
    description = models.TextField(_('Aciklama'), blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Olusturma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Guncelleme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('departman')
        verbose_name_plural = _('departmanlar')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class DepartmentMember(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='departments')
    is_primary = models.BooleanField(_('Ana Departman'), default=False)
    join_date = models.DateField(_('Katilim Tarihi'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('departman uyesi')
        verbose_name_plural = _('departman uyeleri')
        unique_together = ('department', 'user')
    
    def __str__(self):
        return f"{self.user} - {self.department}"
