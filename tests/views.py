from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Test, Question, TestGive, TestHistory
from .serializers import TestCreateSerializer, QuestionSerializer, TestGiveSerializer, TestHistorySerializer
from django.shortcuts import get_object_or_404
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
            # Учитель видит только свои тесты
            return Test.objects.filter(teacher=user).prefetch_related('questions').order_by('-create_at')
        # Для учеников можно оставить пустой QuerySet или добавить логику
        return Test.objects.none()


class TestDeleteUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Test.objects.all()
    serializer_class = TestCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if self.request.user != obj.teacher:
            raise PermissionDenied("Bu testin duzujisi sen dal!")
        return obj

---
## VIEWS FOR TESTGIVE (Test bermek/wagty)

class TestGivenCreateView(generics.CreateAPIView):
    serializer_class = TestGiveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'teacher':
            raise PermissionDenied("Dine mugallymlar test bellap bilyar")
        
        # Проверка, что учитель, назначающий тест, является его создателем
        test_id = self.request.data.get('test')
        try:
            test = Test.objects.get(pk=test_id)
        except Test.DoesNotExist:
            raise PermissionDenied("Test tapylmady")
            
        if test.teacher != user:
            raise PermissionDenied("Sen bu testi bellenman bilyan!")
            
        serializer.save(teacher=user)


class TestGivenListView(generics.ListAPIView):
    serializer_class = TestGiveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            # Учитель видит все свои назначенные тесты
            return TestGive.objects.filter(teacher=user).order_by('-start_date')
        elif user.role == 'student':
            # Ученик видит все назначенные ему тесты (активные или пройденные)
            return TestGive.objects.filter(student_groups__in=user.groups.all()).order_by('-start_date')
        return TestGive.objects.none()


class TestGivenDeleteUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestGive.objects.all()
    serializer_class = TestGiveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if self.request.user != obj.teacher:
            raise PermissionDenied("Bu bellenen testin duzujisi sen dal!")
        return obj

---
## VIEWS FOR TESTHISTORY (Test netijeleri)

class TestHistoryCreateView(generics.CreateAPIView):
    serializer_class = TestHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'student':
            raise PermissionDenied("Dine okuwçylar netijelerini girizip bilyar")
            
        # Дополнительная логика (например, проверка, что тест еще не пройден)
        test_give_id = self.request.data.get('test_give')
        
        # Проверка, что ученик имеет право проходить этот TestGive
        try:
            test_give = TestGive.objects.get(pk=test_give_id)
        except TestGive.DoesNotExist:
            raise PermissionDenied("Bellenen test tapylmady")

        if not test_give.student_groups.filter(id__in=user.groups.all()).exists():
             raise PermissionDenied("Size bu test bellenen dal")

        # Проверка, не прошел ли ученик этот тест уже
        if TestHistory.objects.filter(student=user, test_give=test_give).exists():
            raise PermissionDenied("Siz bu testi eyyam gecen!")

        serializer.save(student=user)


class TestHistoryListView(generics.ListAPIView):
    serializer_class = TestHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            # Учитель видит все результаты для тестов, которые он создал
            return TestHistory.objects.filter(test_give__teacher=user).select_related('student', 'test_give').order_by('-create_at')
        elif user.role == 'student':
            # Ученик видит только свои результаты
            return TestHistory.objects.filter(student=user).select_related('test_give').order_by('-create_at')
        return TestHistory.objects.none()


class TestHistoryDeleteUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestHistory.objects.all()
    serializer_class = TestHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        # Только создатель записи (ученик) или учитель, который выдал тест, может ее видеть/удалить
        if user.role == 'student':
            if user != obj.student:
                raise PermissionDenied("Bu sizin netijeniz dal!")
        elif user.role == 'teacher':
            if user != obj.test_give.teacher:
                raise PermissionDenied("Bu sizin bellenen testiniz dal!")
        else: # Другие роли не имеют доступа
            raise PermissionDenied("Giris rugsat berilen dal")
        return obj


class TestUserView(generics.ListAPIView):
    serializer_class = TestHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Получение результатов для конкретного ученика (pk - это user_id)
        user_id = self.kwargs['pk']
        current_user = self.request.user
        
        # Только учитель может просматривать результаты других
        if current_user.role == 'teacher':
            # Фильтруем результаты, чтобы убедиться, что они относятся к тесту, выданному этим учителем
            return TestHistory.objects.filter(
                student__id=user_id,
                test_give__teacher=current_user
            ).select_related('student', 'test_give').order_by('-create_at')
            
        # Ученик может видеть только свои результаты
        elif current_user.role == 'student' and current_user.pk == user_id:
            return TestHistory.objects.filter(student=current_user).select_related('test_give').order_by('-create_at')
            
        raise PermissionDenied("Giris rugsat berilen dal")


class TestToparView(generics.ListAPIView):
    serializer_class = TestHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Получение результатов для конкретной группы (pk - это test_give_id)
        test_give_id = self.kwargs['pk']
        current_user = self.request.user
        
        # Только учитель может просматривать результаты по выданному им тесту
        if current_user.role == 'teacher':
            # Проверка, что test_give принадлежит этому учителю
            test_give = get_object_or_404(TestGive, pk=test_give_id, teacher=current_user)
            
            return TestHistory.objects.filter(
                test_give=test_give
            ).select_related('student').order_by('student__last_name', 'student__first_name')

        raise PermissionDenied("Giris rugsat berilen dal")
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
