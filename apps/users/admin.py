from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from unfold.forms import UserCreationForm, UserChangeForm, AdminPasswordChangeForm
from unfold.decorators import display  # ← Importamos el decorador display de unfold para mejorar como se ven las columnas
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
    # Habilitamos busqueda y lista para que la tabla de grupos tampoco se vea simple
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """Administración de usuarios con Django Unfold"""
    
    # Formularios correctos
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm  # ← Nombre correcto
    
    # Vista de lista (SIN espacios en los strings)
    # Usamos nuestros nuevos métodos con decoradores en lugar de campos planos
    list_display = ["email", "name", "lastname", "display_is_staff", "display_is_active"]
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

    # --- Decoradores para mejorar el listado (Tabla) ---

    # El decorador @display permite dar atributos visuales en la tabla (boolean=True dibuja checks y cruces verdes/rojas)
    @display(description="Staff", boolean=True)
    def display_is_staff(self, obj):
        """Retorna el estado de staff y lo muestra como icono (check) gracias al decorador"""
        return obj.is_staff

    # El decorador con label={'texto': 'color'} convierte el texto devuelto en una etiqueta/badge (como la 2da foto)
    @display(description="Status", label={"ACTIVE": "success", "INACTIVE": "danger"})
    def display_is_active(self, obj):
        """Si el usuario está activo devuelve "ACTIVE", sino "INACTIVE" y Unfold le asigna un color"""
        return "ACTIVE" if obj.is_active else "INACTIVE"