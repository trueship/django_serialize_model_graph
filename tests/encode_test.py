from unittest import TestCase

from django_serialize_model_graph import encode, decode

from .models import Entity


class TestEncode(TestCase):
    def test_should_encode_and_decode_simple_model(self):
        entity = Entity()
        encoded_entity = encode(entity)
        decoded_entity = decode(encode)
