from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email adresi gereklidir'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser is_staff=True olmalidir.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser is_superuser=True olmalidir.'))
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('Email Adresi'), unique=True)
    first_name = models.CharField(_('Ad'), max_length=30)
    last_name = models.CharField(_('Soyad'), max_length=30)
    is_active = models.BooleanField(_('Aktif'), default=True)
    is_staff = models.BooleanField(_('Personel'), default=False)
    date_joined = models.DateTimeField(_('Kayit Tarihi'), default=timezone.now)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('kullanici')
        verbose_name_plural = _('kullanicilar')
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name
