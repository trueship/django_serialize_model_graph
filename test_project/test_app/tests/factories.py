from test_app.models import Entity, RelatedEntity, DeepRelatedEntity
from test_app.models import SortEntity
from test_app.models import SortRelatedEntityA
from test_app.models import SortRelatedEntityB
from test_app.models import SortRelatedEntityC


def _create_object(model, kw):
    obj = model(**kw)
    obj.save()
    return obj


def create_entity(**kw):
    return _create_object(Entity, kw)


def create_related_entity(**kw):
    return _create_object(RelatedEntity, kw)


def create_deep_related_entity(**kw):
    return _create_object(DeepRelatedEntity, kw)


def create_sort_entity(**kw):
    return _create_object(SortEntity, kw)


def create_sort_related_entity_a(**kw):
    return _create_object(SortRelatedEntityA, kw)


def create_sort_related_entity_b(**kw):
    return _create_object(SortRelatedEntityB, kw)


def create_sort_related_entity_c(**kw):
    return _create_object(SortRelatedEntityC, kw)
