from django.test import TestCase

from django_serialize_model_graph.decode import bind_related_objects
from django_serialize_model_graph.decode import permutate_item_and_rest
from django_serialize_model_graph.decode import get_model_object_foreign_key_fields
from django_serialize_model_graph.decode import get_model_object_model_name
from django_serialize_model_graph.decode import foreign_key_field_points_to_model_object
from django_serialize_model_graph.decode import ForeignKeyField
from test_app.models import Entity, RelatedEntity
from test_app.models import Entity2, RelatedEntity2


class TestPermutateItemAndRest(TestCase):
    def test_should_do_simple_permutation(self):
        self.assertEqual(
            permutate_item_and_rest(['a', 'b', 'c']),
            [('a', ['b', 'c']), ('b', ['a', 'c']), ('c', ['a', 'b'])])


class TestBindRelatedObjects(TestCase):
    def test_when_passed_empty_list_should_do_nothing(self):
        bind_related_objects([])

    def test_when_passed_obj_with_related_should_bind(self):
        entity = Entity(pk=1)
        related_entity = RelatedEntity(entity_id=entity.pk)

        bind_related_objects([entity, related_entity])

        self.assertEqual(related_entity.entity, entity)
        self.assertIs(len(entity.related_entities.all()), 1)


class TestForeignKeyFieldPointsToModelObject(TestCase):
    def test_simple(self):
        entity = Entity(pk=1)
        related_entity = RelatedEntity(entity_id=entity.pk)
        foreign_key_field = ForeignKeyField(
            related_entity,
            'entity',
            'entity')

        self.assertTrue(
            foreign_key_field_points_to_model_object(
                foreign_key_field,
                entity))


class TestGetModelObjectForeignKeyFields(TestCase):
    def test_should_get_empty_list(self):
        entity = Entity()

        self.assertEqual(get_model_object_foreign_key_fields(entity), [])

    def test_should_get_one_field(self):
        related_entity = RelatedEntity(entity_id=3)

        foreign_key_fields = get_model_object_foreign_key_fields(related_entity)
        self.assertEqual(len(foreign_key_fields), 1)
        foreign_key_field = foreign_key_fields[0]
        self.assertEqual(foreign_key_field.field_name, 'entity')
        self.assertEqual(foreign_key_field.foreign_model_name, 'entity')
        self.assertEqual(foreign_key_field.related_pk, 3)

    def test_should_get_one_field_with_different_name(self):
        related_entity = RelatedEntity2(different_name_link_id=3)

        foreign_key_fields = get_model_object_foreign_key_fields(related_entity)
        self.assertEqual(len(foreign_key_fields), 1)
        foreign_key_field = foreign_key_fields[0]
        self.assertEqual(foreign_key_field.field_name, 'different_name_link')
        self.assertEqual(foreign_key_field.foreign_model_name, 'entity2')
        self.assertEqual(foreign_key_field.related_pk, 3)


class TestGetModelObjectModelName(TestCase):
    def test_should_get_model_object_model_name(self):
        model_object = RelatedEntity()

        self.assertEqual(get_model_object_model_name(model_object), 'relatedentity')
