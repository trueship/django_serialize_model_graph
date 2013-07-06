import json

from django.core import serializers


def decode(encoded_entity):
    model_objects = serializers.deserialize('json', json.dumps([encoded_entity]))
    model_objects = list(model_objects)
    model_object = model_objects[0].object
    return model_object
