from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from departments.models import Department  # Bu satırı ekleyin

User = get_user_model()

class Automation(models.Model):
    STATUS_CHOICES = (
        ('active', _('Aktif')),
        ('inactive', _('Pasif')),
        ('development', _('Gelistirme')),
        ('testing', _('Test')),
    )
    
    TYPE_CHOICES = (
        ('api', _('API Tabanli')),
        ('script', _('Script Tabanli')),
        ('workflow', _('Is Akisi')),
        ('integration', _('Entegrasyon')),
        ('report', _('Rapor')),
    )
    
    name = models.CharField(_('Otomasyon Adi'), max_length=100)
    code = models.CharField(_('Otomasyon Kodu'), max_length=50, unique=True)
    description = models.TextField(_('Aciklama'))
    type = models.CharField(_('Otomasyon Tipi'), max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='development')
    icon = models.CharField(_('Ikon'), max_length=50, blank=True)
    entry_point = models.CharField(_('Giris Noktasi'), max_length=255)
    parameters = models.JSONField(_('Parametreler'), default=dict, blank=True)
    departments = models.ManyToManyField(Department, related_name='automations', blank=True)  # Bu satırı ekleyin
    created_at = models.DateTimeField(_('Olusturma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Guncelleme Tarihi'), auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_automations')
    
    class Meta:
        verbose_name = _('otomasyon')
        verbose_name_plural = _('otomasyonlar')
        ordering = ['name']
    
    def __str__(self):
        return self.name

# Geri kalan kod aynı kalacak...

class AutomationExecution(models.Model):
    STATUS_CHOICES = (
        ('pending', _('Bekliyor')),
        ('running', _('Calisiyor')),
        ('completed', _('Tamamlandi')),
        ('failed', _('Basarisiz')),
        ('cancelled', _('Iptal Edildi')),
    )
    
    automation = models.ForeignKey(Automation, on_delete=models.CASCADE, related_name='executions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='automation_executions')
    parameters = models.JSONField(_('Parametreler'), default=dict, blank=True)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='pending')
    result = models.JSONField(_('Sonuc'), null=True, blank=True)
    error_message = models.TextField(_('Hata Mesaji'), blank=True)
    started_at = models.DateTimeField(_('Baslama Zamani'), auto_now_add=True)
    completed_at = models.DateTimeField(_('Tamamlanma Zamani'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('otomasyon calistirma')
        verbose_name_plural = _('otomasyon calistirmalari')
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.automation.name} - {self.started_at}"
