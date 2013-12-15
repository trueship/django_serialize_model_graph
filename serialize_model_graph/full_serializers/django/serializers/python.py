"""
Full Python serializer for Django.

Applied patch from http://code.google.com/p/wadofstuff/issues/detail?id=4
by stur...@gmail.com, Apr 7, 2009.
"""

from __future__ import unicode_literals

import base
from django.core.serializers import base as rbase
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_unicode, is_protected_type, smart_text
from django.db import DEFAULT_DB_ALIAS, models
from django.conf import settings
from django.utils import six
from django.core.serializers.python import _get_model


class Serializer(base.Serializer):
    """
    Python serializer for Django modelled after Ruby on Rails.
    Default behaviour is to serialize only model fields with the exception
    of ForeignKey and ManyToMany fields which must be explicitly added in the
    ``relations`` argument.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize instance attributes.
        """
        self._fields = None
        self._extras = None
        self.objects = []
        super(Serializer, self).__init__(*args, **kwargs)

    def start_serialization(self):
        """
        Called when serializing of the queryset starts.
        """
        self._fields = None
        self._extras = None
        self.objects = []

    def end_serialization(self):
        """
        Called when serializing of the queryset ends.
        """
        pass

    def start_object(self, obj):
        """
        Called when serializing of an object starts.
        """
        self._fields = {}
        self._extras = {}

    def end_object(self, obj):
        """
        Called when serializing of an object ends.
        """
        self.objects.append({
            "model"  : smart_unicode(obj._meta),
            "pk"     : smart_unicode(obj._get_pk_val(), strings_only=True),
            "fields" : self._fields
        })
        if self._extras:
            self.objects[-1]["extras"] = self._extras
        self._fields = None
        self._extras = None

    def handle_field(self, obj, field):
        """
        Called to handle each individual (non-relational) field on an object.
        """
        value = field._get_val_from_obj(obj)
        # Protected types (i.e., primitives like None, numbers, dates,
        # and Decimals) are passed through as is. All other values are
        # converted to string first.
        if is_protected_type(value):
            self._fields[field.name] = value
        else:
            self._fields[field.name] = field.value_to_string(obj)

    def handle_fk_field(self, obj, field):
        """
        Called to handle a ForeignKey field.
        Recursively serializes relations specified in the 'relations' option.
        """
        fname = field.name
        try:
            related = getattr(obj, fname)
        except field.rel.to.DoesNotExist:
            self._fields[fname] = getattr(obj, field.attname)
        else:
            if related is not None:
                if fname in self.relations or 'all_fks' in self.relations and not fname in self.fk_excludes:
                    # perform full serialization of FK
                    serializer = Serializer()
                    options = {}
                    if isinstance(self.relations, dict):
                        if isinstance(self.relations[fname], dict):
                            options = self.relations[fname]
                    self._fields[fname] = serializer.serialize([related],
                        **options)[0]
                else:
                    # emulate the original behaviour and serialize the pk value
                    if self.use_natural_keys and hasattr(related, 'natural_key'):
                        related = related.natural_key()
                    else:
                        if field.rel.field_name == related._meta.pk.name:
                            # Related to remote object via primary key
                            related = related._get_pk_val()
                        else:
                            # Related to remote object via other field
                            related = smart_unicode(getattr(related,
                                field.rel.field_name), strings_only=True)
                    self._fields[fname] = related
            else:
                self._fields[fname] = smart_unicode(related, strings_only=True)

    def handle_m2m_field(self, obj, field):
        """
        Called to handle a ManyToManyField.
        Recursively serializes relations specified in the 'relations' option.
        """
        if field.rel.through._meta.auto_created:
            fname = field.name
            if fname in self.relations:
                # perform full serialization of M2M
                serializer = Serializer()
                options = {}
                if isinstance(self.relations, dict):
                    if isinstance(self.relations[fname], dict):
                        options = self.relations[fname]
                self._fields[fname] = [
                    serializer.serialize([related], **options)[0]
                       for related in getattr(obj, fname).iterator()]
            else:
                # emulate the original behaviour and serialize to a list of
                # primary key values
                if self.use_natural_keys and hasattr(field.rel.to, 'natural_key'):
                    m2m_value = lambda value: value.natural_key()
                else:
                    m2m_value = lambda value: smart_unicode(
                        value._get_pk_val(), strings_only=True)
                self._fields[fname] = [m2m_value(related)
                    for related in getattr(obj, fname).iterator()]

    def getvalue(self):
        """
        Return the fully serialized queryset (or None if the output stream is
        not seekable).
        """
        return self.objects

    def handle_extra_field(self, obj, field):
        """
        Return "extra" fields that the user specifies.
        Can be a property or callable that takes no arguments.
        """
        if hasattr(obj, field):
            extra = getattr(obj, field)
            if callable(extra):
                self._extras[field] = smart_unicode(extra(), strings_only=True)
            else:
                self._extras[field] = smart_unicode(extra, strings_only=True)

    # Reverse serialization code

    def handle_related_m2m_field(self, obj, field_name):
        """Called to handle 'reverse' m2m RelatedObjects
        Recursively serializes relations specified in the 'relations' option.
        """
        fname = field_name

        if field_name in self.relations:
            # perform full serialization of M2M
            serializer = Serializer()
            options = {}
            if isinstance(self.relations, dict):
                if isinstance(self.relations[field_name], dict):
                    options = self.relations[field_name]
            self._fields[fname] = [
                serializer.serialize([related], **options)[0]
                    for related in getattr(obj, fname).iterator()]
        else:
            pass
            # we don't really want to do this to reverse relations unless
            # explicitly requested in relations option
            #
            # emulate the original behaviour and serialize to a list of ids
            # self._fields[fname] = [
            # smart_unicode(related._get_pk_val(), strings_only=True)
            # for related in getattr(obj, fname).iterator()]

    def handle_related_fk_field(self, obj, field_name):
        """Called to handle 'reverse' fk serialization.
        Recursively serializes relations specified in the 'relations' option.
        """
        fname = field_name
        try:
            related = getattr(obj, fname)
        except ObjectDoesNotExist:
            return

        if related is not None:
            if field_name in self.relations:
                # perform full serialization of FK
                serializer = Serializer()
                options = {}
                if isinstance(self.relations, dict):
                    if isinstance(self.relations[field_name], dict):
                        options = self.relations[field_name]
                # Handle reverse foreign key lookups that recurse on the model
                if isinstance(related, models.Manager):
                    # Related fields arrive here as querysets not modelfields
                    self._fields[fname] = serializer.serialize(related.all(),
                        **options)
                else:
                    self._fields[fname] = serializer.serialize([related],
                        **options)[0]
            else:
                pass
                # we don't really want to do this to reverse relations unless
                # explicitly requested in relations option
                #
                # emulate the original behaviour and serialize to a list of ids
                # self._fields[fname] = [
                # smart_unicode(related._get_pk_val(), strings_only=True)
                # for related in getattr(obj, fname).iterator()]
        else:
            self._fields[fname] = smart_unicode(related, strings_only=True)


def Deserializer(object_list, **options):
    """
    Deserialize simple Python objects back into Django ORM instances.

    It's expected that you pass the Python objects themselves (instead of a
    stream or a string) to the constructor
    """
    db = options.get('using', DEFAULT_DB_ALIAS)
    ignore = options.get('ignorenonexistent', False)

    models.get_apps()
    for d in object_list:
        # Look up the model and starting build a dict of data for it.
        Model = _get_model(d["model"])
        data = {Model._meta.pk.attname: Model._meta.pk.to_python(d["pk"])}
        m2m_data = {}
        model_fields = Model._meta.get_all_field_names()

        # Handle each field
        for (field_name, field_value) in six.iteritems(d["fields"]):

            if ignore and field_name not in model_fields:
                # skip fields no longer on model
                continue

            if isinstance(field_value, str):
                field_value = smart_text(field_value, options.get("encoding", settings.DEFAULT_CHARSET), strings_only=True)

            field = Model._meta.get_field_by_name(field_name)[0]
            # Handle M2M relations
            field_rel = getattr(field, 'rel', None)
            if field_rel:
                field_rel_to = field_rel.to
                if isinstance(field_rel, models.ManyToManyRel):
                    if hasattr(field_rel_to._default_manager, 'get_by_natural_key'):
                        def m2m_convert(value):
                            if hasattr(value, '__iter__') and not isinstance(value, six.text_type):
                                return field_rel_to._default_manager.db_manager(db).get_by_natural_key(*value).pk
                            else:
                                return smart_text(field_rel_to._meta.pk.to_python(value))
                    else:
                        m2m_convert = lambda v: smart_text(field.rel.to._meta.pk.to_python(v))
                    m2m_data[field.name] = [m2m_convert(pk) for pk in field_value]

                # Handle FK fields
                elif isinstance(field_rel, models.ManyToOneRel):
                    if field_value is not None:
                        if isinstance(field_value, dict):
                            #handles relations inside a dict
                            data[field.name] = list(Deserializer([field_value], **options))[0].object
                        else:
                            if hasattr(field_rel_to._default_manager, 'get_by_natural_key'):
                                if hasattr(field_value, '__iter__') and not isinstance(field_value, six.text_type):
                                    obj = field_rel_to._default_manager.db_manager(db).get_by_natural_key(*field_value)
                                    value = getattr(obj, field_rel.field_name)
                                    # If this is a natural foreign key to an object that
                                    # has a FK/O2O as the foreign key, use the FK value
                                    if field_rel_to._meta.pk.rel:
                                        value = value.pk
                                else:
                                    value = field_rel_to._meta.get_field(field_rel.field_name).to_python(field_value)
                                data[field.attname] = value
                            else:
                                data[field.attname] = field_rel_to._meta.get_field(field_rel.field_name).to_python(field_value)
                    else:
                        data[field.attname] = None

            # Handle all other fields
            elif hasattr(field, "get_accessor_name"):
                if isinstance(field_value, dict):
                    data[field.get_accessor_name()] = list(Deserializer([field_value], **options))[0].object
                else:
                    raise NotImplementedError
            else:
                data[field.name] = field.to_python(field_value)

        yield rbase.DeserializedObject(Model(**data), m2m_data)
