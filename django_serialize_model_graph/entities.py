class EncodedEntity(object):
    """Represent django-model encoded entity and (possibly) it's
    related data.

    """
    def __init__(self, entity_data, related_entities_datas=[]):
        """Constructor.

        :param entity_data:
            represents result of django encode operation on main entity
        :type entity_data: dict
        :param related_entities_datas:
            represents result of
        :type related_entities_datas: list of dict
        """
        self.entity_data = entity_data
        self.related_entities_datas = related_entities_datas

    def __repr__(self):
        return u'<EncodedEntity {} {}>'.format(self.entity_data, self.related_entities_datas)

    def get_entity_pk(self):
        return self.entity_data['pk']

    def get_entity_model(self):
        return_value = self.entity_data['model'].split('.')[1]
        return return_value
