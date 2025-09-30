from rest_framework import serializers
from .models import Test, Question, TestGive, TestHistory
from django.contrib.auth import get_user_model

User = get_user_model()

# =================================================================
# 1. QUESTION SERIALIZER
# =================================================================

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        # Поле answers должно быть видимо, чтобы студент мог выбирать ответы
        fields = ['id', 'question_text', 'correct_answer', 'answers'] 

class TestCreateSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Test
        fields = ['id','theme', 'number_question', 'create_at', 'teacher', 'questions'] 
        read_only_fields = ['teacher'] 
        depth = 1 

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        test = Test.objects.create(**validated_data)
        for question_data in questions_data:
            Question.objects.create(test=test, **question_data)
        return test

# =================================================================
# 2. TESTGIVE SERIALIZER (для активных тестов)
# =================================================================

class TestGiveSerializer(serializers.ModelSerializer):
    """
    Сериализатор для TestGive.
    Отдает ограниченный список вопросов через given_questions.
    """
    
    given_questions = QuestionSerializer(many=True, read_only=True)
    
    # Добавляем тему (theme) и ID оригинального теста (test_id)
    test_theme = serializers.CharField(source='test.theme', read_only=True)
    test_id = serializers.IntegerField(source='test.id', read_only=True)
    
    # Поле 'test' для приема ID теста при создании (запись)
    test = serializers.PrimaryKeyRelatedField(
        queryset=Test.objects.all(), 
        write_only=True 
    )
    
    teacher = serializers.SlugRelatedField(
        slug_field='username', 
        read_only=True
    )

    class Meta:
        model = TestGive
        fields = [
            'id', 'duration_minutes', 'number_given', 'given_group', 
            'teacher', 'test', 'test_theme', 'test_id', 'given_questions'
        ]

# =================================================================
# 3. TESTHISTORY SERIALIZER (для истории тестов)
# =================================================================

class TestHistorySerializer(serializers.ModelSerializer):
    """
    Возвращает TestHistory с информацией о TestGive и Test.
    """
    
    # Прямое извлечение темы
    test_theme = serializers.CharField(source='test_information.theme', read_only=True)
    # Прямое извлечение имени учителя
    teacher_username = serializers.CharField(source='test_information.teacher.username', read_only=True)
    
    # ID пользователя для отладки
    user_id = serializers.IntegerField(source='user.id', read_only=True) 
    
    class Meta:
        model = TestHistory
        fields = '__all__'
        read_only_fields = ['user']
