from patterns.architectural_system_pattern_unit_of_work import DomainObject


class Model(DomainObject):
    table_name = ''
    fields = ()

    def __init__(self, fields: dict):
        self.__set_fields(fields)

    def __set_fields(self, fields):
        for key in self.fields:
            if fields.get(key):
                setattr(self, key, fields.get(key))
