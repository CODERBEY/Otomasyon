from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from departments.models import Department

User = get_user_model()

class Page(models.Model):
    STATUS_CHOICES = (
        ('draft', _('Taslak')),
        ('published', _('Yayinda')),
        ('archived', _('Arsivlenmis')),
    )
    
    title = models.CharField(_('Sayfa Basligi'), max_length=200)
    slug = models.SlugField(_('URL Adi'), max_length=200, unique=True)
    description = models.TextField(_('Aciklama'), blank=True)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='draft')
    is_homepage = models.BooleanField(_('Ana Sayfa'), default=False)
    layout = models.JSONField(_('Sayfa Duzeni'), default=dict)
    requires_auth = models.BooleanField(_('Kimlik Dogrulama Gerekli'), default=False)
    departments = models.ManyToManyField(Department, blank=True, related_name='pages')
    created_at = models.DateTimeField(_('Olusturma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Guncelleme Tarihi'), auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_pages')
    
    class Meta:
        verbose_name = _('sayfa')
        verbose_name_plural = _('sayfalar')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class Widget(models.Model):
    TYPE_CHOICES = (
        ('text', _('Metin')),
        ('html', _('HTML')),
        ('image', _('Resim')),
        ('button', _('Buton')),
        ('form', _('Form')),
        ('card', _('Kart')),
        ('list', _('Liste')),
        ('table', _('Tablo')),
        ('chart', _('Grafik')),
        ('automation', _('Otomasyon')),
    )
    
    name = models.CharField(_('Widget Adi'), max_length=100)
    widget_type = models.CharField(_('Widget Tipi'), max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(_('Aciklama'), blank=True)
    configuration = models.JSONField(_('Yapilandirma'), default=dict)
    content = models.TextField(_('Icerik'), blank=True)
    is_global = models.BooleanField(_('Global Widget'), default=False)
    created_at = models.DateTimeField(_('Olusturma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Guncelleme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('widget')
        verbose_name_plural = _('widgetlar')
    
    def __str__(self):
        return f"{self.name} ({self.get_widget_type_display()})"

class PageWidget(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='page_widgets')
    widget = models.ForeignKey(Widget, on_delete=models.CASCADE, related_name='page_widgets')
    position = models.JSONField(_('Konum'), default=dict)
    order = models.PositiveSmallIntegerField(_('Sira'), default=0)
    
    class Meta:
        verbose_name = _('sayfa widget')
        verbose_name_plural = _('sayfa widgetlari')
        ordering = ['page', 'order']
    
    def __str__(self):
        return f"{self.page.title} - {self.widget.name}"
