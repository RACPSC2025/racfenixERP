from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.urls import reverse
import hashlib
from unfold.admin import ModelAdmin
from unfold.forms import UserCreationForm, UserChangeForm, AdminPasswordChangeForm
from unfold.decorators import display
from .models import User

# ─────────────────────────────────────────────────────────
# AVATAR HELPERS
# ─────────────────────────────────────────────────────────
# Pares de colores para gradientes de avatar (estilo premium)
AVATAR_COLORS = [
    ("#8b5cf6", "#6d28d9"),  # Violeta
    ("#3b82f6", "#1d4ed8"),  # Azul
    ("#10b981", "#059669"),  # Esmeralda
    ("#f59e0b", "#d97706"),  # Ámbar
    ("#ec4899", "#db2777"),  # Rosa
    ("#06b6d4", "#0891b2"),  # Cian
    ("#84cc16", "#65a30d"),  # Lima
    ("#f43f5e", "#e11d48"),  # Rojo-rosa
]


def _get_avatar_gradient(email):
    """Genera un gradiente consistente basado en el hash del email."""
    idx = int(hashlib.md5(email.encode()).hexdigest(), 16) % len(AVATAR_COLORS)
    c1, c2 = AVATAR_COLORS[idx]
    return f"background: linear-gradient(135deg, {c1}, {c2});"


def _get_initials(user):
    """Obtiene las iniciales del usuario (máximo 2 caracteres)."""
    initials = ""
    if user.name:
        initials += user.name[0].upper()
    if user.lastname:
        initials += user.lastname[0].upper()
    return initials or user.email[0].upper()


# ─────────────────────────────────────────────────────────
# DESREGISTRAR MODELOS POR DEFECTO
# ─────────────────────────────────────────────────────────
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


# ─────────────────────────────────────────────────────────
# GROUP ADMIN
# ─────────────────────────────────────────────────────────
@admin.register(Group)
class GroupAdmin(ModelAdmin):
    """Administración de grupos con Unfold"""
    list_display = ["name"]
    search_fields = ["name"]
    filter_horizontal = ("permissions",)
    
    fieldsets = (
        (None, {"fields": ("name",)}),
        ("Permissions", {
            "fields": ("permissions",),
            "classes": ("wide",),
        }),
    )


# ─────────────────────────────────────────────────────────
# USER ADMIN — DISEÑO PREMIUM ESTILO DASHBOARD
# ─────────────────────────────────────────────────────────
@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """Administración de usuarios con diseño premium tipo Material Dashboard"""

    # Formularios
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    # ── Vista de lista (columnas de la tabla) ──
    list_display = [
        "display_member",
        "display_email",
        "display_role",
        "display_is_staff",
        "display_is_superuser",
        "display_is_active",
        "display_last_login",
        "display_actions",
    ]
    list_filter = ["is_staff", "is_active", "groups"]
    search_fields = ["email", "name", "lastname"]
    ordering = ["email"]
    list_per_page = 25

    # ── Fieldsets para edición ──
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal information", {"fields": ("name", "lastname")}),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
    )

    # ── Fieldsets para creación ──
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

    # Prefetch groups para evitar N+1 en display_role
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("groups")

    # ─────────────────────────────────────────────────────
    # COLUMNAS PERSONALIZADAS CON DISEÑO PREMIUM
    # ─────────────────────────────────────────────────────

    @display(description="Member", ordering="name")
    def display_member(self, obj):
        """
        Columna 'Member': Avatar con iniciales + Nombre completo.
        El email se muestra en su propia columna separada.
        """
        initials = _get_initials(obj)
        gradient = _get_avatar_gradient(obj.email)
        full_name = obj.get_full_name() or obj.email.split("@")[0]

        return format_html(
            '<div style="display:flex; align-items:center; gap:12px; padding:4px 0;">'
            '  <div class="user-avatar" style="{}">{}</div>'
            '  <span class="user-name">{}</span>'
            '</div>',
            gradient, initials, full_name,
        )

    @display(description="Email", ordering="email")
    def display_email(self, obj):
        """Columna 'Email' separada con estilo sutil."""
        return format_html(
            '<span class="user-email">{}</span>',
            obj.email,
        )

    @display(description="Role", ordering="is_staff")
    def display_role(self, obj):
        """
        Columna 'Role': Tipo de rol + Grupos asignados
        Muestra la jerarquía del usuario y sus grupos.
        """
        if obj.is_superuser:
            role = "Administrator"
        elif obj.is_staff:
            role = "Staff"
        else:
            role = "User"

        groups = ", ".join(g.name for g in obj.groups.all()[:3])
        if not groups:
            groups = "Sin grupo"

        return format_html(
            '<div style="display:flex; flex-direction:column;">'
            '  <span class="user-role">{}</span>'
            '  <span class="user-group">{}</span>'
            '</div>',
            role, groups,
        )

    @display(description="Staff", boolean=True)
    def display_is_staff(self, obj):
        """Check/cross para indicar si es Staff"""
        return obj.is_staff

    @display(description="Superuser", boolean=True)
    def display_is_superuser(self, obj):
        """Check/cross para indicar si es Superuser"""
        return obj.is_superuser

    @display(description="Status")
    def display_is_active(self, obj):
        """Badge de estado con relleno estilo pastel consistente"""
        if obj.is_active:
            badge_class = "badge-pastel-green"
            label = "ACTIVO"
            icon = "check_circle"
        else:
            badge_class = "badge-pastel-red"
            label = "INACTIVO"
            icon = "cancel"

        return format_html(
            '<div class="flex items-center justify-center gap-1.5 px-3 py-1 rounded-full font-bold text-[10px] min-w-[100px] border border-transparent {}">'
            '  <span class="material-symbols-outlined" style="font-size:14px;">{}</span>'
            '  <span class="tracking-widest uppercase">{}</span>'
            '</div>',
            badge_class, icon, label
        )

    @display(description="Last Login", ordering="last_login")
    def display_last_login(self, obj):
        """Columna de último login con formato DD/MM/YY"""
        if obj.last_login:
            return format_html(
                '<span class="user-date">{}</span>',
                obj.last_login.strftime("%d/%m/%y"),
            )
        return format_html(
            '<span class="user-date user-date--never">Never</span>',
        )

    @display(description="Actions")
    def display_actions(self, obj):
        """
        Botones de Editar y Eliminar directamente en la fila.
        Eliminar muestra confirmación antes de proceder.
        """
        edit_url = reverse("admin:users_user_change", args=[obj.pk])
        delete_url = reverse("admin:users_user_delete", args=[obj.pk])

        return format_html(
            '<div style="display:flex; align-items:center; gap:6px;">'
            '  <a href="{}" class="action-btn action-btn--edit" title="Editar">'
            '    <span class="material-symbols-outlined" style="font-size:18px;">edit</span>'
            '  </a>'
            '  <a href="{}" class="action-btn action-btn--delete" title="Eliminar"'
            '     onclick="return confirm(\'¿Estás seguro de que deseas eliminar al usuario {}? Esta acción no se puede deshacer.\');">'
            '    <span class="material-symbols-outlined" style="font-size:18px;">delete</span>'
            '  </a>'
            '</div>',
            edit_url, delete_url, obj.email,
        )

# ── SOCIAL ACCOUNTS (ALLAUTH) ──
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
try:
    admin.site.unregister(SocialAccount)
    admin.site.unregister(SocialApp)
    admin.site.unregister(SocialToken)
except admin.sites.NotRegistered:
    pass

@admin.register(SocialAccount)
class SocialAccountAdmin(ModelAdmin):
    list_display = ("user", "provider", "uid", "last_login")
    list_filter = ("provider", "last_login")
    search_fields = ("user__email", "uid")
    fieldsets = (
        (None, {"fields": ("user", "provider", "uid")}),
        ("Extra Data", {"fields": ("extra_data",), "classes": ("collapse",)}),
    )

@admin.register(SocialApp)
class SocialAppAdmin(ModelAdmin):
    list_display = ("name", "provider", "client_id")
    list_filter = ("provider",)
    search_fields = ("name", "client_id")
    filter_horizontal = ("sites",)
    fieldsets = (
        ("Application details", {"fields": ("provider", "name", "client_id", "secret", "key")}),
        ("Sites", {"fields": ("sites",)}),
    )

@admin.register(SocialToken)
class SocialTokenAdmin(ModelAdmin):
    list_display = ("app", "account", "display_token", "expires_at")
    list_filter = ("app", "expires_at")
    fieldsets = (
        (None, {"fields": ("app", "account")}),
        ("Token information", {"fields": ("token", "token_secret", "expires_at")}),
    )
    @display(description="Token")
    def display_token(self, obj):
        return f"{obj.token[:20]}..." if obj.token else "-"


# ─────────────────────────────────────────────────────────
# HISTORIAL DE ACCIONES (LOG ENTRY)
# ─────────────────────────────────────────────────────────
from django.contrib.admin.models import LogEntry

@admin.register(LogEntry)
class LogEntryAdmin(ModelAdmin):
    list_display = ("action_time_display", "user_display", "action_flag_display", "content_type_display", "object_repr_display")
    list_filter = ("action_time", "action_flag", "content_type")
    search_fields = ("object_repr", "change_message", "user__email")
    readonly_fields = ("action_time", "user", "content_type", "object_id", "object_repr", "action_flag", "change_message")
    list_per_page = 50

    @display(description="Fecha y Hora", ordering="action_time")
    def action_time_display(self, obj):
        return format_html(
            '<div class="flex items-center gap-2">'
            '  <span class="material-symbols-outlined text-gray-400" style="font-size:16px;">schedule</span>'
            '  <span class="font-medium text-gray-700 dark:text-gray-300">{}</span>'
            '</div>',
            obj.action_time.strftime("%d/%m/%Y %H:%M")
        )

    @display(description="Usuario", ordering="user")
    def user_display(self, obj):
        return format_html(
            '<div class="flex items-center gap-2">'
            '  <div class="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">'
            '    <span class="text-xs font-bold text-primary-600 dark:text-primary-400">{}</span>'
            '  </div>'
            '  <span class="font-semibold text-gray-900 dark:text-white">{}</span>'
            '</div>',
            obj.user.email[0].upper(),
            obj.user.email.split('@')[0]
        )

    @display(description="Acción Realizada")
    def action_flag_display(self, obj):
        # Usamos clases personalizadas definidas en styles.css para evitar que Tailwind las elimine
        styles = {
            1: ("add_circle", "CREADO", "badge-pastel-green"),
            2: ("edit_calendar", "EDITADO", "badge-pastel-blue"),
            3: ("delete_forever", "ELIMINADO", "badge-pastel-red"),
        }
        
        icon, label, badge_class = styles.get(obj.action_flag, ("help", "OTRO", "bg-gray-100 text-gray-700"))
        
        return format_html(
            '<div class="flex items-center justify-center gap-2 px-3 py-1.5 rounded-lg font-bold text-[10px] min-w-[120px] {}">'
            '  <span class="material-symbols-outlined" style="font-size:16px;">{}</span>'
            '  <span class="tracking-widest uppercase">{}</span>'
            '</div>',
            badge_class, icon, label
        )

    @display(description="Modelo / Módulo")
    def content_type_display(self, obj):
        return format_html(
            '<span class="px-2 py-1 rounded-md bg-gray-100 dark:bg-gray-800 text-xs font-mono text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-700">{}</span>',
            str(obj.content_type).upper()
        )

    @display(description="Objeto Afectado")
    def object_repr_display(self, obj):
        return format_html(
            '<div class="max-w-xs truncate font-medium text-primary-600 dark:text-primary-400">{}</div>',
            obj.object_repr
        )