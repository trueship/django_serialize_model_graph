from test_app.models import Entity, RelatedEntity, DeepRelatedEntity


def create_entity(**kw):
    rv = Entity(**kw)
    rv.save()
    return rv


def create_related_entity(**kw):
    rv = RelatedEntity(**kw)
    rv.save()
    return rv


def create_deep_related_entity(**kw):
    rv = DeepRelatedEntity(**kw)
    rv.save()
    return rv
