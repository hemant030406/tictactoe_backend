from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Room(AbstractUser):
    username = models.CharField(max_length=100,unique = True)
    code = models.CharField(max_length=100)
    moves = models.JSONField(default=dict)
    scores = models.JSONField(default={
        'O': 0,
        'X': 0
    })
    undo_stack = models.JSONField(default=list)
    messages = models.JSONField(default=list)
    users = models.JSONField(default = list)
    turns = models.JSONField(default = dict)

    def __str__(self) -> str:
        return f'{self.username} {self.code} {self.moves} {self.scores} {self.undo_stack}'