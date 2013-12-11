from django.test import TestCase

from serialize_model_graph.entities import EncodedEntity


class TestEncodedEntity(TestCase):
    def test_should_save_entity_to_dict_and_restore(self):
        encoded_entity = EncodedEntity({'a': 'b'})
        d = encoded_entity.to_dict()
        restored = EncodedEntity.from_dict(d)
        self.assertEqual(restored.entity_data, {'a': 'b'})

    def test_should_save_related_entities_datas(self):
        encoded_entity = EncodedEntity({'a': 'b'},
                                       related_entities_datas=[{'c': 'd'}])
        d = encoded_entity.to_dict()
        restored = EncodedEntity.from_dict(d)
        self.assertEqual(restored.entity_data, {'a': 'b'})
        self.assertEqual(restored.related_entities_datas, [{'c': 'd'}])
