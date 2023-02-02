import os.path
from sqlite3 import connect

from app.model import Model


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

    def get_last_id(self):
        query = f'SELECT id FROM {self.table_name} ORDER BY id DESC LIMIT 1'
        self.cursor.execute(query)

        id, = self.cursor.fetchone()
        print(id)
        return id if id else 0


# -- Architectural system pattern - Data Mapper
class MapperRegistry:
    mappers = {}

    @staticmethod
    def get_current_mapper(name):
        return Mapper(MapperRegistry.mappers[name], connection)

    @staticmethod
    def set_mapper(model):
        MapperRegistry.mappers[model.__name__] = model


class DbCommitException(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')


class RecordNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')


class TableNameIsEmpty(Exception):
    def __init__(self, model_name):
        super().__init__(model_name)
        self.model_name = model_name

    def __str__(self):
        return f'Table name is empty for model "{self.model_name}"!'


class FieldsListRequired(Exception):
    def __init__(self, model_name):
        super().__init__(model_name)
        self.model_name = model_name

    def __str__(self):
        return f'The fields list must not be empty. Model "{self.model_name}"!'


path = os.path.join('db', 'patterns.sqlite')
connection = connect(path)
