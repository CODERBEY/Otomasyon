from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

class ErrorLog(models.Model):
    SEVERITY_LEVELS = (
        ('debug', _('Debug')),
        ('info', _('Bilgi')),
        ('warning', _('Uyari')),
        ('error', _('Hata')),
        ('critical', _('Kritik')),
    )
    
    ERROR_TYPES = (
        ('system', _('Sistem Hatasi')),
        ('database', _('Veritabani Hatasi')),
        ('api', _('API Hatasi')),
        ('automation', _('Otomasyon Hatasi')),
        ('authentication', _('Kimlik Dogrulama Hatasi')),
        ('permission', _('Yetki Hatasi')),
        ('validation', _('Dogrulama Hatasi')),
        ('network', _('Ag Hatasi')),
        ('custom', _('Ozel Hata')),
    )
    
    STATUS_CHOICES = (
        ('new', _('Yeni')),
        ('acknowledged', _('Goruldu')),
        ('investigating', _('Inceleniyor')),
        ('resolved', _('Cozuldu')),
        ('ignored', _('Yoksayildi')),
        ('recurring', _('Tekrarlayan')),
    )
    
    error_id = models.CharField(_('Hata ID'), max_length=100, unique=True, db_index=True)
    error_type = models.CharField(_('Hata Tipi'), max_length=20, choices=ERROR_TYPES)
    severity = models.CharField(_('Onem Derecesi'), max_length=10, choices=SEVERITY_LEVELS)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='new')
    message = models.TextField(_('Hata Mesaji'))
    exception_type = models.CharField(_('Istisna Tipi'), max_length=200)
    traceback = models.TextField(_('Hata Izi'))
    file_path = models.CharField(_('Dosya Yolu'), max_length=500)
    function_name = models.CharField(_('Fonksiyon Adi'), max_length=200)
    line_number = models.IntegerField(_('Satir Numarasi'))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='error_logs')
    ip_address = models.GenericIPAddressField(_('IP Adresi'), null=True, blank=True)
    user_agent = models.TextField(_('Kullanici Tarayicisi'), blank=True)
    url = models.URLField(_('URL'), max_length=500, blank=True)
    occurrence_count = models.IntegerField(_('Tekrar Sayisi'), default=1)
    first_seen = models.DateTimeField(_('Ilk Gorulme'), auto_now_add=True)
    last_seen = models.DateTimeField(_('Son Gorulme'), auto_now=True)
    resolved_at = models.DateTimeField(_('Cozum Tarihi'), null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_errors')
    
    class Meta:
        verbose_name = _('hata kaydi')
        verbose_name_plural = _('hata kayitlari')
        ordering = ['-last_seen']
    
    def __str__(self):
        return f"{self.error_type} - {self.message[:50]}"
