import json
import logging

from django.test import TestCase
from django.core import serializers
from django_serialize_model_graph import encode, decode, encode_with_relatives
from django_serialize_model_graph.encode import find_entity_index
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
        entity = Entity()
        entity.save()
        related_entity = RelatedEntity(entity=entity)
        related_entity.save()
        encoded_entity = encode_with_relatives(entity)
        log.debug(encoded_entity.entity_data)
        entity.delete()
        self.assertEqual(RelatedEntity.objects.count(), 0)
        decoded_entity = decode(encoded_entity)

        log.debug(decoded_entity)
        self.assertTrue(isinstance(decoded_entity, Entity))
        self.assertEqual(len(decoded_entity.related_entities.all()), 2)


class TestFindEntityIndex(TestCase):
    def test_should_find_entity_in_parsed_data(self):
        entity = Entity(pk=1)
        parsed_data = self.get_parsed_data([RelatedEntity(pk=2), entity, RelatedEntity(pk=3)])
        index = find_entity_index(entity, parsed_data)
        self.assertEqual(index, 1)

    def get_parsed_data(self, entities):
        json_str = serializers.serialize('json', entities)
        parsed_data = json.loads(json_str)
        return parsed_data
