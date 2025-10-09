from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
# Используем новые модели
from .models import Test, Question, TestGive, TestHistory
# Используем новые сериализаторы
from .serializers import TestCreateSerializer, QuestionSerializer, TestGiveSerializer, TestHistorySerializer
import random

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

        test_instance = serializer.validated_data['test']
        number_given = serializer.validated_data['number_given']
        
        # 1. Получаем все вопросы теста
        all_questions = list(test_instance.questions.all())

        # 2. Выбираем ограниченное случайное подмножество
        if number_given >= len(all_questions):
            selected_questions = all_questions
        else:
            selected_questions = random.sample(all_questions, number_given) # 👈 Вот где происходит ограничение!

        # 3. Сохраняем объект TestGive
        test_give_instance = serializer.save(teacher=self.request.user)
        
        # 4. 🟢 ФИКСИРУЕМ выбранные вопросы в новом поле
        test_give_instance.given_questions.set(selected_questions)


from rest_framework import generics, permissions
from .models import TestGive
from .serializers import TestGiveSerializer

class TestGivenListView(generics.ListAPIView):
    serializer_class = TestGiveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'student':
            # Проверяем, что группа у студента заполнена
            if not hasattr(user, 'group_number') or user.group_number is None:
                return TestGive.objects.none()

            return TestGive.objects.filter(
                given_group=user.group_number
            ).select_related('test', 'teacher').prefetch_related('test__questions')

        elif user.role == 'teacher':
            return TestGive.objects.filter(teacher=user).select_related('test', 'teacher').prefetch_related('test__questions')

        return TestGive.objects.none()


class TestGivenDeleteUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """
    Позволяет получить, обновить или удалить TestGive по ID.
    Используется фронтендом для удаления TestGive после завершения теста.
    """
    queryset = TestGive.objects.all()
    serializer_class = TestGiveSerializer
    permission_classes = [permissions.IsAuthenticated]
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
            return TestHistory.objects.filter(user=logged_in_user).order_by("-id")
            
            # 🛑 Исправление 500 Internal Server Error: Защита от ?user=undefined
            if not user_id_from_query or user_id_from_query.lower() == 'undefined':
                return TestHistory.objects.none()

            # 🛡️ Проверка безопасности: Убеждаемся, что студент запрашивает ТОЛЬКО свои данные
            if str(logged_in_user.id) != user_id_from_query:
                raise PermissionDenied("Siz dine oz netijelerinizi gorup bilersiniz.")
            
            # 🟢 Исправление FieldError: Используем корректное поле 'user'
            return TestHistory.objects.filter(user=user_id_from_query).order_by("-id")
        
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
