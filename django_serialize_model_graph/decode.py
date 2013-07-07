import json
import logging

from django.core import serializers

log = logging.getLogger(__name__)


def decode(encoded_entity):
    datas = [encoded_entity.entity_data] + encoded_entity.related_entities_datas
    model_objects = list(serializers.deserialize('json', json.dumps(datas)))
    bind_related_objects(model_objects)
    model_object_index = encoded_entity_index(encoded_entity, model_objects)
    model_object = model_objects.pop(model_object_index)
    del model_objects  # since it's meaning changed after pop
    return model_object


def encoded_entity_index(encoded_entity, model_objects):
    log.debug(encoded_entity)
    log.debug(model_objects)
    for i, deserialized_model_object in enumerate(model_objects):
        model_object = deserialized_model_object.object
        if model_object_corresponds_encoded_entity(model_object, encoded_entity):
            return i
    return None


def model_object_corresponds_encoded_entity(model_object, encoded_entity):
    model_object_class = unicode(model_object.__class__.__name__).lower()
    encoded_entity_class = encoded_entity.get_entity_model()
    if model_object_class == encoded_entity_class:
        if model_object.pk == encoded_entity.get_entity_pk():
            return True
    return False


def bind_related_objects(model_objects):
    """Searches through flat list of model instances for relation and
    "binds" them, so later you can use relations without querying database.

    """
    pass
