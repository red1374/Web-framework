import os
from sqlite3 import connect

from app.model import UnitOfWork, MapperRegistry


class Engine:
    db_name = ''
    DB_FOLDER_NAME = 'db'
    __connection = None

    """ Main project class """
    def __init__(self, db_name: str = ''):
        self.db_name = db_name
        self.__create_db_connection()

        UnitOfWork.new_current(self.__connection)
        UnitOfWork.get_current().set_mapper_registry(MapperRegistry)

    def __create_db_connection(self):
        db_path = os.path.join(self.DB_FOLDER_NAME, self.db_name)
        self.__connection = connect(db_path)

    @property
    def connection(self):
        return self.__connection
