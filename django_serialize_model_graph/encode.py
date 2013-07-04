import json


def encode(entity):
    from django.core import serializers
    json_str = serializers.serialize('json', [entity])
    data = json.loads(json_str)[0]
    return data
