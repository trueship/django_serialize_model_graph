.. Django Serialize Model Graph documentation master file, created by
   sphinx-quickstart on Wed Jul 10 23:08:52 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Django Serialize Model Graph's documentation!
========================================================

- Project on bitbucket: https://bitbucket.org/k_bx/django_serialize_model_graph
- Project on GitHub: https://github.com/trueship/django_serialize_model_graph
- PyPi page: https://pypi.python.org/pypi/django_serialize_model_graph

Django Serialize Model Graph lets you quickly serialize your Django
object and its relatives into some dictionary and store it, say, in
MongoDB, and then later extract it and use just as if it hasn't gone
anywhere! Here are some example models:

.. code-block:: python

    class Entity(models.Model):
        key = models.CharField(max_length=50)


    class RelatedEntity(models.Model):
        text = models.TextField()
        entity = models.ForeignKey(Entity, related_name='related_entities')

So, here's how to use `django_serialize_model_graph` for encoding end
decoding a single entity:

.. code-block:: python

    entity = Entity()
    encoded_entity = encode(entity)
    decoded_entity = decode(encoded_entity)

And here's how to encode and decode entity and its relatives:

.. code-block:: python

    # create some data
    entity = Entity()
    entity.save()
    related_entity = RelatedEntity(entity=entity)
    related_entity.save()
    related_entity = RelatedEntity(entity=entity)
    related_entity.save()

    print len(RelatedEntity.objects.all()  # prints '2'
    encoded_entity = encode_with_relatives(entity)
    entity.delete()  # oops, deleted
    print RelatedEntity.objects.count()  # prints '0'

    # decode! magic happens!
    decoded_entity = decode(encoded_entity)

    print isinstance(decoded_entity, Entity)  # prints 'True'
    print len(decoded_entity.related_entities.all())  #prints '2'

To convert the encoded value to a dict (to store in MongoDB, for example),
you should do this:

.. code-block:: python

    encoded_entity = encode_with_relatives(entity)
    encoded_dict = encoded_entity.to_dict()

To decode from a dict you do:

.. code-block:: python

    entity = decode_from_dict(encoded_dict)


How it works
============

To encode and decode entities, `django_serialize_model_graph` uses
Django's `serialization mechanisms
<https://docs.djangoproject.com/en/dev/topics/serialization/>`_. To
get "related objects", it uses django's
`django.db.models.deletion.Collector`, which works when you do
`entity.delete()`. Its main strength is that it looks for objects
that relate to the original object via `ForeignKey` (with
`on_delete=CASCADE`, which is the default) and also collects them (and
their relatives). So, semantics of `django_serialize_model_graph`
should match default Django semantics for object deletion, which seems
natural.

The `entity.related_entities.all()` works in a bit of a hardcore manner, by
substituting `Entity.__class__.related_entities` descriptor for its
own proxy. If you know better ways -- please share them with me.

..
   Contents:

   .. toctree::
      :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

