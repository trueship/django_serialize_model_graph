from test_app.models import *


def _create_object(model, **kw):
    obj = model(**kw)
    obj.save()
    return obj


def create_entity(**kw):
    if 'fk_entity' not in kw:
        kw['fk_entity'] = _create_object(FKEntity, value='FK Value')

    if 'o2o_entity' not in kw:
        kw['o2o_entity'] = _create_object(OneFromEntity, value='Value')
    return _create_object(Entity, **kw)


def create_related_entity(**kw):
    return _create_object(RelatedEntity, **kw)


def create_deep_related_entity(**kw):
    return _create_object(DeepRelatedEntity, **kw)


def create_sort_entity(**kw):
    return _create_object(SortEntity, **kw)


def create_sort_related_entity_a(**kw):
    return _create_object(SortRelatedEntityA, **kw)


def create_sort_related_entity_b(**kw):
    return _create_object(SortRelatedEntityB, **kw)


def create_sort_related_entity_c(**kw):
    return _create_object(SortRelatedEntityC, **kw)


def create_O2O_to_entity(**kw):
    return _create_object(OneToEntity, **kw)
