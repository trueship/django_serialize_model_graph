from django.db import models


class Entity(models.Model):
    key = models.CharField(max_length=50)
