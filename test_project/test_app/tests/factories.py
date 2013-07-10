from test_app.models import Entity, RelatedEntity


def create_entity(**kw):
    rv = Entity(**kw)
    rv.save()
    return rv


def create_related_entity(**kw):
    rv = RelatedEntity(**kw)
    rv.save()
    return rv
