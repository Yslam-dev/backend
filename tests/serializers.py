from rest_framework import serializers
# Предполагаем, что модели импортированы корректно
from .models import Test, Question, TestGive, TestHistory 
from django.contrib.auth import get_user_model

User = get_user_model()

# =================================================================
# 1. СЕРИАЛИЗАТОРЫ ДЛЯ TEST и QUESTION (Оставлены без изменений)
# =================================================================

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        # Поле answers должно быть видимо, чтобы студент мог выбирать ответы
        fields = ['id', 'question_text', 'correct_answer', 'answers'] 
        # Примечание: 'correct_answer' должен быть скрыт от студента в реальном приложении,
        # но для простоты оставляем его здесь.

class TestCreateSerializer(serializers.ModelSerializer):
    # Используем TestCreateSerializer для создания и TestListView (для отдачи вопросов)
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Test
        fields = ['id','theme', 'number_question', 'create_at', 'teacher', 'questions'] 
        read_only_fields = ['teacher'] # Защита поля учителя
        depth = 1 # Для получения имени учителя

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        test = Test.objects.create(**validated_data)
        for question_data in questions_data:
            Question.objects.create(test=test, **question_data)
        return test

# =================================================================
# 2. ИСПРАВЛЕННЫЙ TestGiveSerializer (для given_questions) 🚀
# =================================================================

class TestGiveSerializer(serializers.ModelSerializer):
    """
    Сериализатор для TestGive.
    - Принимает test ID для создания.
    - Отдает ограниченный список вопросов через given_questions.
    """
    
    # ❌ УДАЛЕНО: test_information (которое давало ВСЕ вопросы теста)
    # test_information = TestCreateSerializer(source='test', read_only=True)
    
    # 🟢 НОВОЕ ПОЛЕ: Теперь отдаем только ограниченный набор вопросов
    given_questions = QuestionSerializer(many=True, read_only=True)
    
    # Добавляем тему (theme) и ID оригинального теста (test_id) напрямую
    # для удобства фронтенда, так как test_information удалено
    test_theme = serializers.CharField(source='test.theme', read_only=True)
    test_id = serializers.IntegerField(source='test.id', read_only=True)
    
    # Поле 'test' для приема ID теста при создании (запись)
    test = serializers.PrimaryKeyRelatedField(
        queryset=Test.objects.all(), 
        write_only=True 
    )
    
    # Учитель read-only
    teacher = serializers.SlugRelatedField(
        slug_field='username', 
        read_only=True
    )

    class Meta:
        model = TestGive
        # Удаляем 'test_information' и добавляем новые поля
        fields = [
            'id', 'duration_minutes', 'number_given', 'given_group', 
            'teacher', 'test', 'test_theme', 'test_id', 'given_questions'
        ]
        # depth больше не нужен
        
# =================================================================
# 3. ИСПРАВЛЕННЫЙ TestHistorySerializer 
# =================================================================

class TestShortSerializer(serializers.ModelSerializer):
    teacher = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Test
        fields = ['id', 'theme', 'number_question', 'create_at', 'teacher']


class TestHistoryCreateView(generics.CreateAPIView):
    serializer_class = TestHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        give_info = serializer.validated_data.get('give_information')
        if give_info:
            test_info = give_info.test
        else:
            test_info = None
        serializer.save(user=self.request.user, test_information=test_info)


    class Meta:
        model = TestHistory
        fields = [
            "id",
            "number_corrected",
            "ball",
            "user",
            "test_information",  # теперь объект, а не просто ID
            "give_information",
            "review_questions",
            "created_at",
        ]
        read_only_fields = ["user"]


    def get_test_information(self, obj):
        if obj.test_information:
            return {
                "id": obj.test_information.id,
                "theme": obj.test_information.theme,
                "teacher": obj.test_information.teacher.username,
                "number_question": obj.test_information.number_question,
                "create_at": obj.test_information.create_at,  # 🟢 Добавлено
            }
        return None
