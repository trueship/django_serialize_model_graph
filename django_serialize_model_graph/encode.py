import json

from django.core import serializers
from django.db import router
from django.db.models.deletion import Collector


def encode(entity):
    """Encode a single object."""
    json_str = serializers.serialize('json', [entity])
    data = json.loads(json_str)[0]
    return data


def encode_with_relatives(entity):
    """Encode entity and it's relatives.

    Unlike simple :func:`encode`, this function gathers not only main
    entity, but also it's relatives, which point into this entity via
    `ForeignKey` attribute which `on_delete` is set to `CASCADE`
    option (default in django).

    So, you can say, that this function gathers same objects, which
    would be deleted if you'd call `entity.delete()`, which seems to
    make sense as a default option for "graph of object and it's
    relatives".

    :returns: list(entities)

    """
    def always_false(*args, **kw):
        return False

    using = router.db_for_write(entity.__class__, instance=entity)
    collector = Collector(using=using)
    collector.can_fast_delete = always_false
    collector.collect([entity])
    return_value = []
    for model, instances in collector.data.items():
        for instance in instances:
            return_value.append(encode(instance))
    return return_value
