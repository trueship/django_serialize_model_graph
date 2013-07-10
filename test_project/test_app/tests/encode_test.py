import json
import logging

from django.test import TestCase
from django.core import serializers
from django_serialize_model_graph import encode, decode, encode_with_relatives
from django_serialize_model_graph.encode import find_entity_index
from test_app.tests.factories import create_entity, create_related_entity
from test_app.models import Entity, RelatedEntity

log = logging.getLogger(__name__)


class TestEncode(TestCase):
    def test_should_encode_and_decode_simple_model(self):
        entity = Entity()
        encoded_entity = encode(entity)
        decoded_entity = decode(encoded_entity)
        self.assertEqual(type(decoded_entity), Entity)

    def test_should_encode_and_decode_field_value(self):
        entity = Entity(key="value")
        encoded_entity = encode(entity)
        decoded_entity = decode(encoded_entity)

        self.assertEqual(decoded_entity.key, "value")


class TestEncodeWithRelatives(TestCase):
    def test_should_encode_with_simple_relative(self):
        entity = create_entity()
        create_related_entity(entity=entity)
        create_related_entity(entity=entity)
        self.assertEqual(len(RelatedEntity.objects.all()), 2)
        encoded_entity = encode_with_relatives(entity)
        log.debug(encoded_entity.entity_data)
        entity.delete()
        self.assertEqual(RelatedEntity.objects.count(), 0)
        decoded_entity = decode(encoded_entity)

        log.debug(decoded_entity)
        self.assertTrue(isinstance(decoded_entity, Entity))
        self.assertEqual(len(decoded_entity.related_entities.all()), 2)

    def test_when_mocking_related_descriptor_should_keep_old_select_working(self):
        existing_entity = create_entity()
        create_related_entity(entity=existing_entity)
        create_related_entity(entity=existing_entity)
        entity_to_serialize = create_entity()
        create_related_entity(entity=entity_to_serialize)
        create_related_entity(entity=entity_to_serialize)
        self.assertEqual(existing_entity.related_entities.count(), 2)
        encoded_entity = encode_with_relatives(entity_to_serialize)
        entity_to_serialize.delete()
        decoded_entity = decode(encoded_entity)
        self.assertEqual(decoded_entity.related_entities.count(), 2)
        self.assertEqual(existing_entity.related_entities.count(), 2)


class TestFindEntityIndex(TestCase):
    def test_should_find_entity_in_parsed_data(self):
        entity = Entity(pk=1)
        parsed_data = self.get_parsed_data(
            [RelatedEntity(pk=2), entity, RelatedEntity(pk=3)])
        index = find_entity_index(entity, parsed_data)
        self.assertEqual(index, 1)

    def get_parsed_data(self, entities):
        json_str = serializers.serialize('json', entities)
        parsed_data = json.loads(json_str)
        return parsed_data


class Descriptor(object):
    def __set__(self, obj, val):
        pass
        # print '> __set__'

    def __get__(self, obj, objtype):
        # print '> __get__'
        return 10


class ClassWithDescriptor(object):
    foo = Descriptor()


class MockDescriptor(object):
    def __set__(self, obj, val):
        # print '> __set__ in mock'
        pass

    def __get__(self, obj, objtype):
        # print '> __get__ in mock'
        return 20


class TestReplaceDescriptor(TestCase):
    def test_should_replace_simple_descriptor(self):
        instance = ClassWithDescriptor()

        setattr(instance.__class__, 'foo', MockDescriptor())

        self.assertEqual(instance.foo, 20)
