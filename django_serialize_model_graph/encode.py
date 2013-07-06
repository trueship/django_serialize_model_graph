import json

from django.core import serializers


def encode(entity):
    json_str = serializers.serialize('json', [entity])
    data = json.loads(json_str)[0]
    return data


def encode_with_relatives(entity):
    pass
