class EncodedEntity(object):
    """Represent django-model encoded entity and (possibly) it's
    related data.

    """
    def __init__(self, entity_data, related_entities_datas=None):
        """Constructor.

        :param entity_data:
            represents result of django encode operation on main entity
        :type entity_data: dict
        :param related_entities_datas:
            represents result of
        :type related_entities_datas: list of dict
        """
        if related_entities_datas is None:
            related_entities_datas = []
        self.entity_data = entity_data
        self.related_entities_datas = related_entities_datas

    def __repr__(self):
        return u'<EncodedEntity {} {}>'.format(self.entity_data, self.related_entities_datas)

    def get_entity_pk(self):
        return self.entity_data['pk']

    def get_entity_model(self):
        return_value = self.entity_data['model'].split('.')[1]
        return return_value

    def to_dict(self):
        return_value = {
            'entity_data': self.entity_data,
            'related_entities_datas': self.related_entities_datas,
        }
        return return_value

    @classmethod
    def from_dict(cls, d):
        return_value = cls(d['entity_data'], d.get('related_entities_datas'))
        return return_value
