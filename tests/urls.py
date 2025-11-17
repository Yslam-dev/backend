# =======================================================
# Файл: urls.py (Исправлено)
# =======================================================
from django.urls import path
from .views import (
    TestCreateView, TestListView, TestDeleteUpdateView,
    TestGivenCreateView, TestGivenListView, TestGivenDeleteUpdateView, # 🟢 ДОБАВЛЕНО
    TestHistoryCreateView, TestHistoryListView, TestHistoryDeleteUpdateView
)

urlpatterns = [
    path('tests/create/', TestCreateView.as_view(), name='test-create'),
    path('tests/list/', TestListView.as_view(), name='test-list'),
    path('tests/<int:pk>/', TestDeleteUpdateView.as_view(), name='test-update-delete'),

    path('tests/give/create/', TestGivenCreateView.as_view(), name='test-give-create'),
    path('tests/give/list/', TestGivenListView.as_view(), name='test-give-list'),
    
    # 🟢 ДОБАВЛЕН НЕДОСТАЮЩИЙ МАРШРУТ для DELETE
    path('tests/give/<int:pk>/', TestGivenDeleteUpdateView.as_view(), name='test-give-update-delete'), 

    path('tests/history/create/', TestHistoryCreateView.as_view(), name='test-history-create'),
    path('tests/history/list/', TestHistoryListView.as_view(), name='test-history-list'),
    path('tests/history/<int:pk>/', TestHistoryDeleteUpdateView.as_view(), name='test-history-update-delete'),
]