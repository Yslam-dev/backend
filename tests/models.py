from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Test(models.Model):
    theme = models.CharField(max_length=255)
    question = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)
    answer1 = models.CharField(max_length=255)
    answer2 = models.CharField(max_length=255)
    answer3 = models.CharField(max_length=255)
    number_question = models.IntegerField()
    create_at = models.DateTimeField(auto_now_add=True)
    

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tests')
    def __str__(self):
        return f"{self.theme} - {self.question}"

class TestGive(models.Model):
    duration_minutes = models.PositiveIntegerField()
    number_given = models.IntegerField()
    given_group = models.IntegerField()

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_teacher')
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
class TestHistory(models.Model):
    number_corrected = models.IntegerField()
    ball = models.IntegerField()

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student')
    give_information = models.ForeignKey(TestGive, on_delete=models.CASCADE, related_name='give_information')
    test_information = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='test_information')