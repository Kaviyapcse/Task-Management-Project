from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICE = (
        (1, "Admin"),
        (2, "User")
    )

    username = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=32)
    is_active = models.BooleanField(default=False)
    is_logout = models.BooleanField(default=False)
    logout_at = models.DateTimeField(null=True)
    business = models.CharField(max_length=32, null=True)
    role_type = models.IntegerField(choices=ROLE_CHOICE, default=ROLE_CHOICE[0][1])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password', 'username']

    def __str__(self):
        return self.email


class Task(models.Model):

    PRIORITY_CHOICES = (
        ('low', 'LOW'),
        ('medium', 'MEDIUM'),
        ('high', 'HIGH')
    )

    STATUS_CHOICES = (
        ('to-do', 'TO-DO'),
        ('in-progress', 'IN-PROGRESS'),
        ('done', 'DONE')
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField(null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to-do')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, null=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title
