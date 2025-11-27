# views.py dosyanın en altına ekle:

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .serializers import UserCreateSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

# 1. Yeni Kullanıcı Oluşturma (Sadece Adminler)
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # İstersen IsAdminUser yapabilirsin
def api_create_user(request):
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Serializer create metodunda generated_password'ü response'a eklemiştik
        return Response({
            "message": "Kullanıcı oluşturuldu!",
            "username": user.username,
            "generated_password": getattr(user, 'generated_password', 'Hata')
        }, status=201)
    return Response(serializer.errors, status=400)

# 2. Kullanıcıları Listeleme
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_list_users(request):
    users = User.objects.all().values('id', 'username', 'surname', 'role', 'group_number', 'is_online')
    return Response(list(users))
