from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from simple_history.models import HistoricalRecords

# Create your models here.
class UserManager(BaseUserManager):
    
    # Método privado para crear usuarios (usado por create_user y create_superuser)
    def _create_user(self, email, password=None, **extra_fields):
            
            if not email:
                raise ValueError('The Email field must be set')
            
            email = self.normalize_email(email)
            user = self.model(email=email, **extra_fields)
            
            if password:
                user.set_password(password)
            user.save(using=self._db)
            return user

    # Método público para crear usuarios normales
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    # Método público para crear superusuarios
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('Email', max_length=100, unique=True, 
                              error_messages={'unique': "A user with that email already exists."})
    name = models.CharField('Name', max_length=100, blank=True)
    lastname = models.CharField('Last Name', max_length=100, blank=True)
    is_active = models.BooleanField('Active', default=True)
    is_staff = models.BooleanField('Staff', default=False)
    # Auditoría
    history = HistoricalRecords()

    # Campos requeridos para login (allauth + Django)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # No pedimos username ni otros campos obligatorios

    # Manager
    objects = UserManager()

    # Meta y str
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['email']
    
    # El str se muestra en el admin y en otros lugares donde se muestre el objeto
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.name} {self.lastname}".strip()
    
    def get_short_name(self):
        return self.name or self.email