from django.urls import path
from .views import api_login_jwt, user_info_api, api_create_user, api_list_users # Yeni view'leri import et
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('api/login_jwt/', api_login_jwt, name='api-login-jwt'),
    path('api/user/', user_info_api, name='user-info'),
    
    # Yeni eklenenler:
    path('api/create-user/', api_create_user, name='api-create-user'),
    path('api/list-users/', api_list_users, name='api-list-users'),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
