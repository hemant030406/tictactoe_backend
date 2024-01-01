from django.db import models

# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    arr = models.JSONField(default=[])