from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    # Убираем username и email из списка
    list_display = (
        'role',
        'username',
        'surname',
        'group_number',
        'online_status',
    )

    # Фильтры
    list_filter = (
        'role',
        'group_number',
        'is_staff',
        'is_superuser',
        'is_active',
    )

    # Поиск
    search_fields = (
        'surname',
        'group_number',
    )

    # Сортировка
    ordering = ('surname',)

    # Форма редактирования — без username, email, is_online, adres
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'username',
                    'password',
                    'role',
                    'surname',
                    'group_number',
                ),
            },
        ),
    )

    # Форма создания — без username, email, is_online, adres
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'surname',
                    'password1',
                    'password2',
                    'role',                    
                    'group_number',
                ),
            },
        ),
    )

    @admin.display(description='Статус', ordering='is_online')
    def online_status(self, obj):
        color = '#16a34a' if obj.is_online else '#9ca3af'
        text = 'Онлайн' if obj.is_online else 'Оффлайн'
        return format_html(
            '<span style="display:inline-flex;align-items:center;">'
            '<span style="width:8px;height:8px;border-radius:50%;background:{};display:inline-block;margin-right:6px;"></span>'
            '{}</span>',
            color, text
        )
