from django.db import models


class Entity(models.Model):
    key = models.CharField(max_length=50)


class RelatedEntity(models.Model):
    text = models.TextField()
    entity = models.ForeignKey(Entity, related_name='related_entities')
