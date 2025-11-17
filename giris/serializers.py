from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from .utils import generate_password

User = get_user_model()

class UserCreateSerializer(serializers.ModelSerializer):
    generated_password = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['username', 'surname', 'role', 'group_number', 'generated_password']

    def create(self, validated_data):
        # 1. Генерируем пароль
        password = generate_password(6)

        # 2. Сохраняем user'a
        user = User(**validated_data)
        user.password = make_password(password)
        user.save()

        # 3. Добавляем сгенерированный пароль в response
        user.generated_password = password  
        return user
