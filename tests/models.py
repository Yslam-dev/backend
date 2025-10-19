from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Test(models.Model):
    theme = models.CharField(max_length=255)
    number_question = models.IntegerField()
    create_at = models.DateTimeField(auto_now_add=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tests')

    def __str__(self):
        return f"{self.theme} by {self.teacher.username}"

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)
    
    # Мы будем хранить все 4 ответа в одном поле типа JSON. 
    # Это удобно, так как не нужно создавать отдельные поля для каждого ответа.
    answers = models.JSONField() 

    def __str__(self):
        return self.question_text
class TestGive(models.Model):
    duration_minutes = models.PositiveIntegerField()
    number_given = models.IntegerField()
    given_group = models.IntegerField()

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_teacher')
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    given_questions = models.ManyToManyField(
        'Question', 
        related_name='given_to_tests',
        blank=True
    )
class TestHistory(models.Model):
    number_corrected = models.IntegerField()
    ball = models.IntegerField()

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student')
    give_information = models.ForeignKey(TestGive, on_delete=models.SET_NULL, null=True, blank=True, related_name='give_information')
    test_information = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='test_information')
    given_group = models.IntegerField(null=True, blank=True)

    # 🟢 Bu alan olmadan reviewQuestions frontende asla gelmez:
    review_questions = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.test_information.theme if self.test_information else 'No Test'}"
