from rest_framework import serializers
from .models import Test, Question, TestGive, TestHistory

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        # 'answers' теперь будет принимать массив из 4 ответов
        fields = ['question_text', 'correct_answer', 'answers'] 

class TestCreateSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Test
        # 'questions' - это поле, которое мы будем ожидать от фронтенда
        fields = ['theme', 'number_question', 'questions'] 

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        test = Test.objects.create(**validated_data)
        for question_data in questions_data:
            Question.objects.create(test=test, **question_data)
        return test

class TestGiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestGive
        fields = '__all__'

class TestHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TestHistory
        fields = ['id', 'number_corrected', 'ball', 'user', 'give_information', 'test_information']
        read_only_fields = ['user']
        depth = 1
    
