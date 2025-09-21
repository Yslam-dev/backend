from django.urls import path
from .views import api_login_jwt, user_info_api
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('api/login_jwt/', api_login_jwt, name='api-login-jwt'),
    path('api/user/', user_info_api, name='user-info'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
