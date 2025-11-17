from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.hashers import make_password
from .models import User
from .utils import generate_password

class CustomUserAdmin(UserAdmin):
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

    def save_model(self, request, obj, form, change):
        # Если создаётся новый пользователь — генерируем пароль
        if not change:
            password = generate_password(6)
            obj.password = make_password(password)
            obj.generated_password = password
            print("Generated password:", password)  # видно в консоли сервера

        super().save_model(request, obj, form, change)

admin.site.register(User, CustomUserAdmin)
