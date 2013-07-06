Django Serialize Model Graph
============================

With `django_serialize_model_graph`, you can serialize your model (and
it's relatives) into some data structure that can be stored somewhere,
and then re-stored later. This library uses django's
[serialization][0] abilities, and it's `.delete`'s `Collector` for
collecting relative objects.

API is simple set of `encode`, `encode_with_relatives` and `decode`
functions currently. Take a look at `test_project/test_app/tests/` for
various usages.

[0]: https://docs.djangoproject.com/en/dev/topics/serialization/
