from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
# Используем новые модели
from .models import Test, Question, TestGive, TestHistory
# Используем новые сериализаторы
from .serializers import TestCreateSerializer, QuestionSerializer, TestGiveSerializer, TestHistorySerializer

class TestCreateView(generics.CreateAPIView):
    serializer_class = TestCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'teacher':
            raise PermissionDenied("Dine mugallymlar test duzup bilyar")
        serializer.save(teacher=self.request.user)

class TestListView(generics.ListAPIView):
    # Теперь TestListView будет отдавать тесты вместе с вложенными вопросами
    serializer_class = TestCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            # Используем select_related для оптимизации запроса
            return Test.objects.filter(teacher=user).prefetch_related('questions').order_by('-create_at')
        
class TestDeleteUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Test.objects.all()
    serializer_class = TestCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if self.request.user != obj.teacher:
            raise PermissionDenied("Bu testin duzujisi sen dal!")
        return obj
            
class TestGivenCreateView(generics.CreateAPIView):
    serializer_class = TestGiveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'teacher':
            raise PermissionDenied("Dine mugallymlar ugradyp bilyar")
        serializer.save(teacher = self.request.user)

class TestGivenListView(generics.ListAPIView):
    serializer_class = TestGiveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        User = self.request.user
        if User.role == 'student':
            return TestGive.objects.filter(given_group = User.group_number)

class TestHistoryCreateView(generics.CreateAPIView):
    serializer_class = TestHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

class TestHistoryListView(generics.ListAPIView):
    serializer_class = TestHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        User = self.request.user
        if User.role == 'teacher':
            return TestHistory.objects.filter(test_information__teacher=User)
        elif User.role == 'student':
            return TestHistory.objects.filter(student=User)
        
class TestHistoryDeleteUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestHistory.objects.all()
    serializer_class = TestHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if self.request.user != obj.test_information.teacher:
            raise PermissionDenied("Sen bu testin taryhyny uygedip yada pozup bilmersin")
        return obj
