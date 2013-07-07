import json
import logging

from django.core import serializers

log = logging.getLogger(__name__)


def decode(encoded_entity):
    datas = [encoded_entity.entity_data] + encoded_entity.related_entities_datas
    model_objects = serializers.deserialize('json', json.dumps(datas))
    model_objects = list(model_objects)
    model_object = find_encoded_entity(encoded_entity, model_objects)
    return model_object


def find_encoded_entity(encoded_entity, model_objects):
    log.debug(encoded_entity)
    log.debug(model_objects)
    for deserialized_model_object in model_objects:
        model_object = deserialized_model_object.object
        if model_object_corresponds_encoded_entity(model_object, encoded_entity):
            return model_object
    return None


def model_object_corresponds_encoded_entity(model_object, encoded_entity):
    model_object_class = unicode(model_object.__class__.__name__).lower()
    encoded_entity_class = encoded_entity.get_entity_model()
    if model_object_class == encoded_entity_class:
        if model_object.pk == encoded_entity.get_entity_pk():
            return True
    return False
