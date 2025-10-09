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
    test_information = NestedTestSerializer(source='test', read_only=True)
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)

    class Meta:
        model = TestGive
        fields = ['id', 'duration_minutes', 'number_given', 'given_group', 'test_information', 'teacher_name']
        
# =================================================================
# 3. ИСПРАВЛЕННЫЙ TestHistorySerializer 
# =================================================================

class TestHistorySerializer(serializers.ModelSerializer):
    """
    Возвращает TestHistory с информацией о TestGive и Test.
    TestGive и TestInformation будут отображены вложенными.
    """
    
    # Добавляем прямые поля для темы и учителя, чтобы избежать излишних depth.
    test_theme = serializers.CharField(source='test_information.theme', read_only=True)
    teacher_username = serializers.CharField(source='test_information.teacher.username', read_only=True)
    
    class Meta:
        model = TestHistory
        fields = '__all__'
        read_only_fields = ['user']
        # ⚠️ УДАЛЕНО depth=1. Лучше явно указывать поля, как выше, 
        # чтобы избежать неконтролируемой рекурсии и загрузки всех вопросов. 
        # depth = 1
