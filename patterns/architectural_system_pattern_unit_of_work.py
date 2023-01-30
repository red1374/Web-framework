from threading import local


# -- Architectural system pattern - UnitOfWork
class UnitOfWork:
    """
    UNIT OF WORK pattern
    """

    current = local()

    def __init__(self):
        """ List of objects for insert update and delete operations """
        self.new_objects = []
        self.dirty_objects = []
        self.removed_objects = []

    def set_mapper_registry(self, MapperRegistry):
        self.MapperRegistry = MapperRegistry

    def register_new(self, obj):
        self.new_objects.append(obj)

    def register_dirty(self, obj):
        self.dirty_objects.append(obj)

    def register_removed(self, obj):
        self.removed_objects.append(obj)

    def commit(self):
        self.insert_new()
        self.update_dirty()
        self.delete_removed()

        self.new_objects.clear()
        self.dirty_objects.clear()
        self.removed_objects.clear()

    def insert_new(self):
        """ Call insert method of given object model """
        for obj in self.new_objects:
            self.MapperRegistry.get_mapper(obj).insert(obj)

    def update_dirty(self):
        """ Call update method of given object model """
        for obj in self.dirty_objects:
            self.MapperRegistry.get_mapper(obj).update(obj)

    def delete_removed(self):
        """ Call delete method of given object model """
        for obj in self.removed_objects:
            self.MapperRegistry.get_mapper(obj).delete(obj)

    @staticmethod
    def new_current():
        __class__.set_current(UnitOfWork())

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

    def mark_dirty(self):
        """ Registration for update operation """
        UnitOfWork.get_current().register_dirty(self)

    def mark_removed(self):
        """ Registration for delete operation """
        UnitOfWork.get_current().register_removed(self)
