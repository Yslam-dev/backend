from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "surname", "role", "group_number")

    # Отключаем проверку unique для username
    def clean_username(self):
        return self.cleaned_data["username"]


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("username", "surname", "role", "group_number")
