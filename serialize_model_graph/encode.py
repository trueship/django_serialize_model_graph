import json
import logging
from operator import attrgetter

from django.core import serializers
from django.db import router
from django.db.models.deletion import Collector

from serialize_model_graph.entities import EncodedEntity

log = logging.getLogger(__name__)


def encode(entity, **kwargs):
    """Encode a single object."""
    json_str = serializers.serialize('json', [entity], use_natural_keys=True, **kwargs)
    encoded_entity = EncodedEntity(entity_data=json.loads(json_str)[0])
    return encoded_entity


def encode_with_relatives(entity, **kwargs):
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
    entities, models = collect_related_instanses(entity, **kwargs)
    parsed_data = serializers.serialize('python', entities, use_natural_keys=True, **kwargs)
    return create_encoded_entity(parsed_data, entity)


def encode_with_full_relatives(entity, **kwargs):
    """ Can be used with custom-serializers, adds necessary fk_excludes
    to serialiser not to double some data when full serialization
    """
    entities, models = collect_related_instanses(entity, **kwargs)

    fk_excludes = kwargs.pop('fk_excludes', set())
    if fk_excludes:
        fk_excludes = set(fk_excludes)
    for model in models:
        fk_excludes.update(map(attrgetter('field.name'),
                           model._meta.get_all_related_objects()))
    kwargs['fk_excludes'] = fk_excludes
    parsed_data = serializers.serialize('python', entities, use_natural_keys=True, **kwargs)
    return create_encoded_entity(parsed_data, entity)


def collect_related_instanses(entity, **kwargs):
    def always_false(*args, **kw):
        return False

    exclude_models = kwargs.pop('exclude_models', [])
    using = router.db_for_write(entity.__class__, instance=entity)
    collector = Collector(using=using)
    collector.can_fast_delete = always_false
    collector.collect([entity])
    entities = []
    models = set()

    for model, instances in collector.data.items():
        if model not in exclude_models:
            entities.extend(instances)
            models.add(model)
    return entities, models


def create_encoded_entity(parsed_data, entity):
    entity_index = find_entity_index(entity, parsed_data)
    entity_data = parsed_data.pop(entity_index)
    related_entities_datas = parsed_data
    related_entities_datas = sort_related_entities_datas(related_entities_datas)
    encoded_entity = (
        EncodedEntity(entity_data=entity_data,
                      related_entities_datas=related_entities_datas))
    return encoded_entity


def sort_related_entities_datas(related_entities_datas):
    return sorted(related_entities_datas, key=lambda x: (x['model'], x['pk']))


def find_entity_index(entity, entity_datas):
    for i, entity_data in enumerate(entity_datas):
        entity_model_str = entity.__class__.__name__.lower()
        entity_data_model_str = entity_data['model'].split('.')[1]
        if entity_model_str == entity_data_model_str:
            return i
