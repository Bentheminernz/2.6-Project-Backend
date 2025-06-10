from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    username = models.CharField(
        max_length=30,
        unique=True,
        help_text="Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.",
        validators=[AbstractUser.username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    email = models.EmailField(unique=True)

    def name(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.username

    def __str__(self):
        return self.username