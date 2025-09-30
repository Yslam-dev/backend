from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Test, Question, TestGive, TestHistory
from .serializers import TestCreateSerializer, QuestionSerializer, TestGiveSerializer, TestHistorySerializer
import random
import logging

# Инициализация логгера для отладки
logger = logging.getLogger(__name__)


# =================================================================
# VIEWS FOR TEST (Mugallym) - (Без изменений)
# =================================================================

class TestCreateView(generics.CreateAPIView):
    serializer_class = TestCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'teacher':
            raise PermissionDenied("Dine mugallymlar test duzup bilyar")
        serializer.save(teacher=self.request.user)


class TestListView(generics.ListAPIView):
    serializer_class = TestCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
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


# =================================================================
# VIEWS FOR TESTGIVE (Mugallym/Okuwcy)
# =================================================================

class TestGivenCreateView(generics.CreateAPIView):
    serializer_class = TestGiveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'teacher':
            raise PermissionDenied("Dine mugallymlar ugradyp bilyar")

        test_instance = serializer.validated_data['test']
        number_given = serializer.validated_data['number_given']
        
        all_questions = list(test_instance.questions.all())

        if number_given >= len(all_questions):
            selected_questions = all_questions
        else:
            selected_questions = random.sample(all_questions, number_given)

        test_give_instance = serializer.save(teacher=self.request.user)
        test_give_instance.given_questions.set(selected_questions)


class TestGivenListView(generics.ListAPIView):
    serializer_class = TestGiveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        User = self.request.user
        if User.role == 'student':
            # Оптимизация для получения связанных данных
            return TestGive.objects.filter(given_group=User.group_number)\
                .select_related('test', 'teacher')\
                .prefetch_related('given_questions')\
                .order_by("-id")


class TestGivenDeleteUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestGive.objects.all()
    serializer_class = TestGiveSerializer
    permission_classes = [permissions.IsAuthenticated]


# =================================================================
# VIEWS FOR TESTHISTORY (Taryh)
# =================================================================

class TestHistoryCreateView(generics.CreateAPIView):
    serializer_class = TestHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Сохраняем залогиненного пользователя как 'user' в TestHistory
        serializer.save(user=self.request.user)


class TestHistoryListView(generics.ListAPIView):
    serializer_class = TestHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        logged_in_user = self.request.user
        
        # 1. Сценарий для учителя
        if logged_in_user.role == 'teacher':
            return TestHistory.objects.filter(test_information__teacher=logged_in_user).order_by("-id")
        
        # 2. Сценарий для студента (вызывается из okuwcy.jsx)
        elif logged_in_user.role == 'student':
            
            # Получаем ID пользователя из параметра запроса 'user'
            user_id_from_query = self.request.query_params.get('user')
            
            if not user_id_from_query or user_id_from_query.lower() == 'undefined':
                 return TestHistory.objects.none()

            # Проверка безопасности: Убеждаемся, что студент запрашивает ТОЛЬКО свои данные
            if str(logged_in_user.id) != user_id_from_query:
                # logger.warning(f"SECURITY ALERT: User {logged_in_user.id} tried to access history of {user_id_from_query}")
                raise PermissionDenied("Siz dine oz netijelerinizi gorup bilersiniz.")
            
            # 🟢 КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Фильтруем по ID и добавляем оптимизацию
            try:
                # Фильтруем по user_id и оптимизируем запросы
                return TestHistory.objects.filter(user_id=int(user_id_from_query))\
                    .select_related('user', 'test_information__teacher')\
                    .order_by("-id")
            except ValueError:
                # logger.error(f"Invalid user ID format: {user_id_from_query}")
                return TestHistory.objects.none()

        # Для любой другой роли
        return TestHistory.objects.none()


class TestHistoryDeleteUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestHistory.objects.all()
    serializer_class = TestHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        # Разрешаем удалять/обновлять только учителю, который создал тест
        if self.request.user != obj.test_information.teacher:
            raise PermissionDenied("Sen bu testin taryhyny uygedip yada pozup bilmersin")
        return obj
