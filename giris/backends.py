# giris/backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class RoleBasedBackend(BaseBackend):
    """
    Логин зависит от роли:
    - Студент: username + surname + group_number + password
    - Учитель: username + surname + password
    """
    def authenticate(self, request, username=None, surname=None, password=None, group_number=None, **kwargs):
        try:
            # Сначала ищем пользователя по username и surname
            user = User.objects.get(username=username, surname=surname)
        except User.DoesNotExist:
            return None

        # Проверяем пароль
        if not user.check_password(password):
            return None

        # Если студент — проверяем group_number
        if user.role == "student":
            if user.group_number != group_number:
                return None

        # Если учитель — group_number не проверяем
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
