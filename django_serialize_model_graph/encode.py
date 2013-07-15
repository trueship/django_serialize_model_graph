import json
import logging

from django.core import serializers
from django.db import router
from django.db.models.deletion import Collector

from django_serialize_model_graph.entities import EncodedEntity

log = logging.getLogger(__name__)


def encode(entity):
    """Encode a single object."""
    json_str = serializers.serialize('json', [entity])
    encoded_entity = EncodedEntity(entity_data=json.loads(json_str)[0])
    return encoded_entity


def encode_with_relatives(entity):
    """Encode entity and it's relatives.

    Unlike simple :func:`encode`, this function gathers not only main
    entity, but also its relatives, which point into this entity via
    `ForeignKey` attribute which `on_delete` is set to `CASCADE`
    option (default in django).

    So, you can say, that this function gathers same objects, which
    would be deleted if you'd call `entity.delete()`, which seems to
    make sense as a default option for "graph of object and its
    relatives".

    :returns: :class:`EncodedEntity` object

    """
    def always_false(*args, **kw):
        return False

    using = router.db_for_write(entity.__class__, instance=entity)
    collector = Collector(using=using)
    collector.can_fast_delete = always_false
    collector.collect([entity])

    entities = []
    for model, instances in collector.data.items():
        for instance in instances:
            entities.append(instance)

    json_str = serializers.serialize('json', entities)
    parsed_data = json.loads(json_str)
    entity_index = find_entity_index(entity, parsed_data)
    entity_data = parsed_data.pop(entity_index)
    related_entities_datas = parsed_data
    related_entities_datas = sort_related_entities_datas(related_entities_datas)
    encoded_entity = (
        EncodedEntity(entity_data=entity_data,
                      related_entities_datas=related_entities_datas))
    return encoded_entity


def sort_related_entities_datas(related_entities_datas):
    # return related_entities_datas
    return sorted(related_entities_datas, key=lambda x: (x['model'], x['pk']))


def find_entity_index(entity, entity_datas):
    for i, entity_data in enumerate(entity_datas):
        entity_model_str = entity.__class__.__name__.lower()
        entity_data_model_str = entity_data['model'].split('.')[1]
        if entity_model_str == entity_data_model_str:
            return i
