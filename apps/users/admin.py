from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from unfold.forms import UserCreationForm, UserChangeForm, AdminPasswordChangeForm
from .models import User

# Desregistrar modelos por defecto para evitar conflictos
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


@admin.register(Group)
class GroupAdmin(ModelAdmin):
    """Administración de grupos con Unfold"""
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """Administración de usuarios con Django Unfold"""
    
    # Formularios correctos
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm  # ← Nombre correcto
    
    # Vista de lista (SIN espacios en los strings)
    list_display = ["email", "name", "lastname", "is_staff", "is_active"]
    list_filter = ["is_staff", "is_active"]
    search_fields = ["email", "name", "lastname"]
    ordering = ["email"]
    list_per_page = 25
    
    # Fieldsets para edición (campos exactos del modelo)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal information", {"fields": ("name", "lastname")}),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
    )
    
    # Fieldsets para creación
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "name", "lastname", 
                "password1", "password2", 
                "is_staff", "is_active", "is_superuser", "groups", "user_permissions"
            ),
        }),
    )
    
    # Configuración adicional
    filter_horizontal = ("groups", "user_permissions")
    readonly_fields = ["last_login"]