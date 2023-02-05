from threading import local

from app.exceptions import TableNameIsEmpty, FieldsListRequired, DbCommitException, DbUpdateException, DbDeleteException


class UnitOfWork:
    current = local()

    def __init__(self, connection):
        """ List of objects for insert update and delete operations """
        self.new_objects = []
        self.changed_objects = []
        self.removed_objects = []
        self.connection = connection

    def set_mapper_registry(self, MapperRegistry):
        self.MapperRegistry = MapperRegistry

    def register_new(self, obj):
        self.new_objects.append(obj)

    def register_changed(self, obj):
        self.changed_objects.append(obj)

    def register_removed(self, obj):
        self.removed_objects.append(obj)

    def commit(self):
        self.insert_new()
        self.update_changed()
        self.delete_removed()

        self.new_objects.clear()
        self.changed_objects.clear()
        self.removed_objects.clear()

    def insert_new(self):
        """ Call insert method of given object model """
        for obj in self.new_objects:
            try:
                self.MapperRegistry.get_current_mapper(
                    obj.__class__.__name__,
                    self.connection
                ).insert(obj)
            except Exception as e:
                print(e)

    def update_changed(self):
        """ Call update method of given object model """
        for obj in self.changed_objects:
            self.MapperRegistry.get_current_mapper(
                obj.__class__.__name__,
                self.connection
            ).update(obj)

    def delete_removed(self):
        """ Call delete method of given object model """
        for obj in self.removed_objects:
            self.MapperRegistry.get_current_mapper(
                obj.__class__.__name__,
                self.connection
            ).delete(obj)

    @staticmethod
    def new_current(connection):
        __class__.set_current(UnitOfWork(connection))

    @classmethod
    def set_current(cls, unit_of_work):
        cls.current.unit_of_work = unit_of_work

    @classmethod
    def get_current(cls):
        return cls.current.unit_of_work


class DomainObject:
    """ Models base class to add registration methods for operations with object"""
    def mark_new(self):
        """ Registration for insert operation """
        UnitOfWork.get_current().register_new(self)

    def mark_changed(self):
        """ Registration for update operation """
        UnitOfWork.get_current().register_changed(self)

    def mark_removed(self):
        """ Registration for delete operation """
        UnitOfWork.get_current().register_removed(self)


class Model(DomainObject):
    table_name = ''
    fields = ()

    def __init__(self, fields: dict):
        self.__set_fields(fields)

    def __set_fields(self, fields):
        for key in self.fields:
            if fields.get(key):
                setattr(self, key, fields.get(key))


class Mapper:
    """ Data Mapper pattern for given model """
    def __init__(self, model: Model, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.model = model
        self.table_name = self.__get_table_name(model)
        self.fields = self.__get_fields(model)

    def __get_table_name(self, model: Model) -> str:
        if not model.table_name:
            raise TableNameIsEmpty(model.__name__)
        return model.table_name

    def __get_fields(self, model: Model) -> tuple:
        if not model.fields:
            raise FieldsListRequired(model.__name__)
        return model.fields

    def all(self):
        query = f'SELECT { ", ".join(self.fields)} FROM {self.table_name}'
        self.cursor.execute(query)
        result = []
        for values in self.cursor.fetchall():
            fields = dict(zip(self.fields, values))
            record = self.model(fields)
            result.append(record)

        return result

    def find(self, params: dict, limit: int = 0):
        query = f'SELECT { ", ".join(self.fields)} FROM {self.table_name} WHERE '
        query += self.__get_where_params(params)
        if limit:
            query += f' LIMIT {limit}'
        self.cursor.execute(query)

        result = []
        for values in self.cursor.fetchall():
            fields = dict(zip(self.fields, values))
            record = self.model(fields)
            result.append(record)

        return result

    def get_one(self, params):
        result = self.find(params, 1)
        return result[0] if len(result) else None

    def insert(self, obj):
        query = f"INSERT INTO {self.table_name} (%s) VALUES (%s)"
        keys, values = self.__get_insert_params(obj)
        self.cursor.execute(query % (', '.join(keys), ', '.join(values)))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        query = f"UPDATE {self.table_name} SET "
        query += self.__get_set_params(obj)
        query += f"WHERE id='{obj.id}'"
        self.cursor.execute(query)
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        query = f"DELETE FROM {self.table_name} WHERE id=?"
        self.cursor.execute(query, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)

    def get_last_id(self):
        """ Get last inserted row id """
        query = f'SELECT id FROM {self.table_name} ORDER BY id DESC LIMIT 1'
        self.cursor.execute(query)

        item_id, = self.cursor.fetchone()
        return item_id if item_id else 0

    def __get_where_params(self, params: dict) -> str:
        result = []
        for key, value in params.items():
            if key in self.fields:
                if isinstance(value, list):
                    result.append(f"{key} IN ({','.join(value)})")
                else:
                    result.append(f"{key}='{value}'")

        return ' AND '.join(result)

    def __get_set_params(self, obj):
        result = [f"{key}='{getattr(obj, key)}'" for key in self.fields if hasattr(obj, key)]
        return ', '.join(result)

    def __get_insert_params(self, obj):
        result = [(key, f"'{getattr(obj, key)}'") for key in self.fields if hasattr(obj, key)]
        return zip(*result)


class MapperRegistry:
    """ Registry of model mappers """
    mappers = {}

    @staticmethod
    def get_current_mapper(name, connection):
        return Mapper(MapperRegistry.mappers[name], connection)

    @staticmethod
    def set_mapper(model):
        MapperRegistry.mappers[model.__name__] = model
