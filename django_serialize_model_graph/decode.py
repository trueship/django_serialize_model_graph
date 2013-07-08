import json
import logging

from django.core import serializers
from django.db.models.fields.related import ForeignKey

log = logging.getLogger(__name__)


def decode(encoded_entity):
    datas = [encoded_entity.entity_data] + encoded_entity.related_entities_datas
    model_objects = [x.object for x in list(serializers.deserialize('json', json.dumps(datas)))]
    bind_related_objects(model_objects)
    model_object_index = encoded_entity_index(encoded_entity, model_objects)
    model_object = model_objects.pop(model_object_index)
    del model_objects  # since it's meaning changed after pop
    return model_object


def encoded_entity_index(encoded_entity, model_objects):
    log.debug(encoded_entity)
    log.debug(model_objects)
    for i, model_object in enumerate(model_objects):
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
    for (obj, rest) in permutate_item_and_rest(model_objects):
        bind_related_objects_for_single(obj, rest)


def permutate_item_and_rest(objs):
    """Permutates list in pairs so that every object is once a head,
    and others are tail.

    Lie this:

    >>> obj1, obj2, obj3 = 'a', 'b', 'c'
    >>> permutate_item_and_rest([obj1, obj2, obj3])
    [(obj1, [obj2, obj3]), (obj2, [obj1, obj3]), (obj3, [obj1, obj2])]
    """
    def list_without_item(l, i):
        new_l = list(l)
        new_l.pop(i)
        return new_l
    return [(obj, list_without_item(objs, i)) for (i, obj) in enumerate(objs)]


def bind_related_objects_for_single(model_object, rest):
    foreign_key_fields = get_model_object_foreign_key_fields(model_object)
    [bind_related_objects_for_foreign_key(x, rest)
     for x in foreign_key_fields]


def get_model_object_foreign_key_fields(model_object):
    fields = model_object._meta.local_fields
    fields = [x for x in fields if isinstance(x, ForeignKey)]
    return_value = []
    for field in fields:
        return_value.append(
            ForeignKeyField(
                model_object,
                field.name,
                field.rel.to._meta.object_name.lower()))
    return return_value


def bind_related_objects_for_foreign_key(foreign_key_field, model_objects):
    for model_object in model_objects:
        if foreign_key_field_points_to_model_object(foreign_key_field, model_object):
            setattr(foreign_key_field.model_object, foreign_key_field.foreign_model_name, model_object)


def foreign_key_field_points_to_model_object(foreign_key_field, model_object):
    model_object_model_name = get_model_object_model_name(model_object)
    return (foreign_key_field.related_pk == model_object.pk
            and foreign_key_field.foreign_model_name == model_object_model_name)


def get_model_object_model_name(model_object):
    return model_object.__class__.__name__.lower()


class ForeignKeyField(object):
    def __init__(self, model_object, field_name, foreign_model_name):
        self.model_object = model_object
        self.field_name = field_name
        self.foreign_model_name = foreign_model_name
        self.related_pk = getattr(model_object, field_name + '_id')
        super(ForeignKeyField, self).__init__()
