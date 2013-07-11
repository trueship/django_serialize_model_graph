from django.db import models


class Entity(models.Model):
    key = models.CharField(max_length=50)

    def __unicode__(self):
        return (u"pk={}, key={}, pyid={}"
                .format(self.pk, repr(self.key), id(self)))


class RelatedEntity(models.Model):
    text = models.TextField()
    entity = models.ForeignKey(Entity, related_name='related_entities')

    def __unicode__(self):
        return (u"pk={}, text={}, entity_id={}"
                .format(self.pk, self.text, self.entity_id))


class DeepRelatedEntity(models.Model):
    text = models.TextField()
    related_entity = models.ForeignKey(RelatedEntity, related_name='deep_related_entities')


class Entity2(models.Model):
    data = models.CharField(max_length=50)


class RelatedEntity2(models.Model):
    some_data = models.TextField()
    different_name_link = models.ForeignKey(Entity2)
