from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.hashers import make_password
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .utils import generate_password

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    fieldsets = (
        (None, {'fields': ('username', 'surname', 'password')}),
        ('Permissions', {'fields': ('role', 'group_number', 'is_staff', 'is_active')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'surname', 'role', 'group_number'),
        }),
    )

    # Генерация пароля
    def save_model(self, request, obj, form, change):
        if not change:
            password = generate_password(6)
            obj.password = make_password(password)
        super().save_model(request, obj, form, change)

admin.site.register(User, CustomUserAdmin)
