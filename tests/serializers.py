from rest_framework import serializers
from .models import Test, TestGive, TestHistory

class TestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'
        read_only_fields = ['teacher' , 'create_at']

class TestGiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestGive
        fields = '__all__'

class TestHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TestHistory
        fields = '__all__'
        read_only_fields = ['user']
        depth = 1
    