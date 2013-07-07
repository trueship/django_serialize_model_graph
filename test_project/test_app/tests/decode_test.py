from django.test import TestCase

from django_serialize_model_graph.decode import bind_related_objects
from test_app.models import Entity, RelatedEntity


class TestBindRelatedObjects(TestCase):
    def test_when_passed_empty_list_should_do_nothing(self):
        bind_related_objects([])

    def test_when_passed_obj_with_related_should_bind(self):
        entity = Entity()
        related_entity = RelatedEntity(entity_id=entity.pk)

        bind_related_objects([entity, related_entity])

        self.assertIs(len(entity.related_entities.all()), 1)
        self.assertEqual(related_entity.entity, entity)
