import json
import logging

from django.test import TestCase
from django.core import serializers
from django.utils.unittest import skipIf
from django.test.utils import override_settings
from serialize_model_graph import (encode,
                                   decode, encode_with_relatives,
                                   encode_with_full_relatives)
from serialize_model_graph.encode import find_entity_index
from test_app.tests.factories import create_entity
from test_app.tests.factories import create_O2O_to_entity
from test_app.tests.factories import create_related_entity
from test_app.tests.factories import create_deep_related_entity
from test_app.tests.factories import create_sort_entity
from test_app.tests.factories import create_sort_related_entity_a
from test_app.tests.factories import create_sort_related_entity_b
from test_app.tests.factories import create_sort_related_entity_c
from test_app.models import Entity, RelatedEntity, FKEntity, OneFromEntity


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
        self.assertEqual(RelatedEntity.objects.all().count(), 2)
        encoded_entity = encode_with_relatives(entity)
        log.debug(encoded_entity.entity_data)
        entity.delete()
        self.assertEqual(RelatedEntity.objects.count(), 0)
        decoded_entity = decode(encoded_entity)

        log.debug(decoded_entity)
        self.assertTrue(isinstance(decoded_entity, Entity))
        self.assertEqual(len(decoded_entity.related_entities.all()), 2)
        self.assertEqual(RelatedEntity.objects.count(), 0)

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

    def test_should_deserialize_deep_related_entity(self):
        entity = create_entity()
        related_entity = create_related_entity(entity=entity)
        create_deep_related_entity(text='deep', related_entity=related_entity)

        encoded_entity = encode_with_relatives(entity)
        entity.delete()

        decoded_entity = decode(encoded_entity)
        deep_relateds = decoded_entity.related_entities.all()[0].deep_related_entities.all()
        self.assertEqual(len(deep_relateds), 1)
        self.assertEqual(deep_relateds[0].text, "deep")

    def test_should_sort_related_entities_by_model_name_and_pk(self):
        entity = create_sort_entity()
        create_sort_related_entity_a(entity=entity)
        create_sort_related_entity_b(entity=entity)
        create_sort_related_entity_c(entity=entity)
        create_sort_related_entity_c(entity=entity, pk=3)
        create_sort_related_entity_c(entity=entity, pk=2)
        encoded = encode_with_relatives(entity)

        pairs = [(x['model'], x['pk']) for x in encoded.related_entities_datas]
        self.assertEqual(pairs, [('test_app.sortrelatedentitya', 1),
                                 ('test_app.sortrelatedentityb', 1),
                                 ('test_app.sortrelatedentityc', 1),
                                 ('test_app.sortrelatedentityc', 2),
                                 ('test_app.sortrelatedentityc', 3)])


# @skipIf(not FULL_TEST, 'wadofstuff is not installed')
@override_settings(SERIALIZATION_MODULES={'json': 'serialize_model_graph.full_serializers.django.serializers.json',
                                          'python': 'serialize_model_graph.full_serializers.django.serializers.python'})
class TestFullEncode(TestCase):

    def test_full_encode_should_not_contain_entity_id_in_relatives(self):
        entity = create_entity()
        create_O2O_to_entity(entity=entity)
        create_related_entity(entity=entity)
        create_related_entity(entity=entity)
        self.assertEqual(RelatedEntity.objects.all().count(), 2)
        full_encoded_entity = encode_with_full_relatives(entity)
        encoded_entity = encode_with_relatives(entity)
        log.debug(encoded_entity.entity_data)
        log.debug(full_encoded_entity.entity_data)
        self.assertEqual(full_encoded_entity.entity_data,
                         encoded_entity.entity_data)
        self.assertEqual(full_encoded_entity.related_entities_datas,
                         encoded_entity.related_entities_datas)
        self.check_fk_relatives_in_data(full_encoded_entity)

        entity.delete()
        decoded_entity = decode(full_encoded_entity)
        log.debug(decoded_entity)
        self.assertTrue(isinstance(decoded_entity, Entity))
        self.assertEqual(len(decoded_entity.related_entities.all()), 2)
        self.assertEqual(RelatedEntity.objects.count(), 0)

    def test_full_encode_with_all_fks(self):
        entity = create_entity()
        create_O2O_to_entity(entity=entity)
        create_related_entity(entity=entity)
        fk_entity = FKEntity.objects.all()[0]
        self.assertEqual(RelatedEntity.objects.all().count(), 1)
        full_encoded_entity = encode_with_full_relatives(entity, relations=('all_fks',))
        self.check_fk_relatives_in_data(full_encoded_entity)
        entity.delete()
        fk_entity.delete()
        decoded_entity = decode(full_encoded_entity)
        self.assertTrue(isinstance(decoded_entity, Entity))
        self.assertEqual(decoded_entity.related_entities.count(), 1)
        self.assertTrue(isinstance(decoded_entity.fk_entity, FKEntity))
        self.assertFalse(FKEntity.objects.all())
        self.assertTrue(isinstance(decoded_entity.o2o_entity, OneFromEntity))

    def test_should_work_with_excludes(self):
        entity = create_entity()
        create_O2O_to_entity(entity=entity)
        create_related_entity(entity=entity)
        encoded_entity = encode_with_full_relatives(entity, relations=('all_fks',), excludes=('o2o_entity',))
        full_encoded_entity = encode_with_full_relatives(entity, relations=('all_fks',))
        self.assertFalse('o2o_entity' in encoded_entity.entity_data['fields'])
        self.assertTrue('o2o_entity' in full_encoded_entity.entity_data['fields'])
        self.check_entity_can_be_decoded(encoded_entity)

    def test_should_work_with_O2O_reverse(self):
        entity = create_entity()
        create_related_entity(entity=entity)
        encoded_entity = encode_with_full_relatives(entity, relations=('all_fks',), excludes=('o2o_to_entity',))
        self.check_fk_relatives_in_data(encoded_entity)
        self.check_entity_can_be_decoded(encoded_entity)

    def test_should_work_with_fk_excludes(self):
        entity = create_entity()
        create_O2O_to_entity(entity=entity)
        create_related_entity(entity=entity)
        encoded_entity = encode_with_full_relatives(entity, relations=('all_fks',), fk_excludes=('o2o_entity',))
        full_encoded_entity = encode_with_full_relatives(entity, relations=('all_fks',))
        self.assertTrue(isinstance(encoded_entity.entity_data['fields']['o2o_entity'], int))
        self.assertFalse(isinstance(full_encoded_entity.entity_data['fields']['o2o_entity'], int))
        self.check_entity_can_be_decoded(encoded_entity)

    def check_fk_relatives_in_data(self, encoded_entity):
        for relative in encoded_entity.related_entities_datas:
            entity_id = relative['fields']['entity']
            self.assertTrue(isinstance(entity_id, int))

    def check_entity_can_be_decoded(self, encoded_entity):
        decoded_entity = decode(encoded_entity)
        self.assertTrue(isinstance(decoded_entity, Entity))


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
