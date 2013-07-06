from django.test import TestCase

from django_serialize_model_graph import encode, decode, encode_with_relatives
from test_app.models import Entity, RelatedEntity


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
        encoded_entities = encode_with_relatives(entity)
        entity.delete()
        self.assertEqual(RelatedEntity.objects.count(), 0)
        decoded_entities = map(decode, encoded_entities)

        self.assertEqual(len(decoded_entities), 2)
        # related_text = decoded_entity.related_entities.all()[0].text
        # self.assertEqual(related_text, 'some text')
