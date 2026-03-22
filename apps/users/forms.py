from django import forms
from unfold.forms import UserCreationForm, UserChangeForm   # ← aquí está la diferencia
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "name", "lastname")

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ("email", "name", "lastname", "image", "is_active", "is_staff")