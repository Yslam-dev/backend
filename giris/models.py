from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ("teacher", "Teacher"),
        ("student", "Student"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    surname = models.CharField(max_length=50)
    group_number = models.CharField(max_length=4, blank=True, null=True)
    is_online = models.BooleanField(default=False)


    def __str__(self):
        return self.username

