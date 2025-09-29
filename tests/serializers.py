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
        fields = ['question_text', 'correct_answer', 'answers'] 

class TestCreateSerializer(serializers.ModelSerializer):
    # Используем TestCreateSerializer для создания и TestListView (для отдачи вопросов)
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Test
        fields = ['id','theme', 'number_question', 'create_at', 'teacher', 'questions'] 
        read_only_fields = ['teacher'] # Защита поля учителя
        # Можно добавить depth=1 для получения имени учителя
        depth = 1

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        test = Test.objects.create(**validated_data)
        for question_data in questions_data:
            Question.objects.create(test=test, **question_data)
        return test

# =================================================================
# 2. ИСПРАВЛЕННЫЙ TestGiveSerializer (Добавлен depth=1)
# =================================================================

class TestGiveSerializer(serializers.ModelSerializer):
    """
    Сериализатор для TestGive.
    - Принимает test ID для создания.
    - Отдает вложенный объект Test для отображения темы (test_information).
    """
    
    # Read-only поле для отдачи полной информации о тесте (тема, количество вопросов и т.д.)
    # Используем TestCreateSerializer, который включает вопросы (если нужно) и тему.
    test_information = TestCreateSerializer(source='test', read_only=True)
    
    # Поле 'test' для приема ID теста при создании (запись)
    test = serializers.PrimaryKeyRelatedField(
        queryset=Test.objects.all(), 
        write_only=True # Это поле только для записи, чтобы не ломать depth=1 логику при отдаче
    )
    
    # Учитель read-only
    teacher = serializers.SlugRelatedField(
        slug_field='username', 
        read_only=True
    )

    class Meta:
        model = TestGive
        # Включаем все нужные поля для чтения (кроме 'test', которое теперь write-only)
        fields = [
            'id', 'duration_minutes', 'number_given', 'given_group', 
            'teacher', 'test', 'test_information'
        ]
        # Важно: 

# =================================================================
# 3. ИСПРАВЛЕННЫЙ TestHistorySerializer 
# =================================================================

class TestHistorySerializer(serializers.ModelSerializer):
    """
    Возвращает TestHistory с информацией о TestGive и Test.
    TestGive и TestInformation будут отображены вложенными.
    """
    class Meta:
        model = TestHistory
        fields = '__all__'
        read_only_fields = ['user']
        # 🟢 КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Добавляем depth=1. 
        # Это важно для отображения 'theme' в истории.
        depth = 1