from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

# Функция создания JWT
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

# Логин и выдача JWT
@api_view(['POST'])
@permission_classes([AllowAny])
def api_login_jwt(request):
    username = request.data.get("username")
    password = request.data.get("password")
    role = request.data.get("role")
    group_number = request.data.get("group_number")

    if not username or not password:
        return Response({"message": "Отсутствует username или password"}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)
    if not user:
        return Response({"message": "Неверный логин или пароль"}, status=status.HTTP_401_UNAUTHORIZED)

    if role and user.role != role:
        return Response({"message": "Роль не совпадает"}, status=status.HTTP_403_FORBIDDEN)
    if role == "student" and group_number and user.group_number != group_number:
        return Response({"message": "Неверный номер группы"}, status=status.HTTP_403_FORBIDDEN)

    # Создаём токены
    tokens = get_tokens_for_user(user)

    # Помечаем онлайн
    user.is_online = True
    user.save(update_fields=['is_online'])

    return Response({
        "message": "Успешный вход",
        "access": tokens["access"],
        "refresh": tokens["refresh"],
        "user": {
            "surname": user.surname,
            "role": user.role,
            "group_number": user.group_number,
            "is_online": user.is_online,
        }
    })

# Получение информации о пользователе (защищено JWT)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info_api(request):
    user = request.user
    return Response({
        "surname": user.surname,
        "role": user.role,
        "group_number": user.group_number,
        "is_online": user.is_online,
    })