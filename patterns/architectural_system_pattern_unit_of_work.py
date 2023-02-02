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
        self.changed_objects = []
        self.removed_objects = []

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
                self.MapperRegistry.get_current_mapper(obj.__class__.__name__).insert(obj)
            except Exception as e:
                print(e)

    def update_changed(self):
        """ Call update method of given object model """
        for obj in self.changed_objects:
            self.MapperRegistry.get_current_mapper(obj.__class__.__name__).update(obj)

    def delete_removed(self):
        """ Call delete method of given object model """
        for obj in self.removed_objects:
            self.MapperRegistry.get_current_mapper(obj.__class__.__name__).delete(obj)

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

    def mark_changed(self):
        """ Registration for update operation """
        UnitOfWork.get_current().register_changed(self)

    def mark_removed(self):
        """ Registration for delete operation """
        UnitOfWork.get_current().register_removed(self)
