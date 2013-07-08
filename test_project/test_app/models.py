from django.db import models


class Entity(models.Model):
    key = models.CharField(max_length=50)


class RelatedEntity(models.Model):
    text = models.TextField()
    entity = models.ForeignKey(Entity, related_name='related_entities')


class Entity2(models.Model):
    data = models.CharField(max_length=50)


class RelatedEntity2(models.Model):
    some_data = models.TextField()
    different_name_link = models.ForeignKey(Entity2)
