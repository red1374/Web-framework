from copy import deepcopy

from db.mappers import MapperRegistry
from patterns.architectural_system_pattern_unit_of_work import UnitOfWork
from patterns.behavioral_patterns import Subject


class User:
    """ User class """
    def __init__(self, name):
        self.name = name


class Teacher(User):
    """ Teacher class """
    pass


class UserFactory:
    """ User creational class of type factory method """
    types = {
        'teacher': Teacher,
    }

    @classmethod
    def create(cls, type_, name):
        """ Creational pattern factory method """
        return cls.types[type_](name)


class CoursePrototype:
    """ Courses creational pattern of Prototype type """
    def clone(self):
        return deepcopy(self)


class CoursePattern(CoursePrototype, Subject):
    auto_id = 1
    """ Course class """

    def __init__(self, name, category, field: str = ''):
        self.id = CoursePattern.auto_id
        CoursePattern.auto_id += 1
        self.name = name
        self.category = category
        self.category.courses.append(self)
        self.field = field
        self.students = []
        super().__init__()

    def __getitem__(self, item):
        return self.students[item]

    def add_student(self, student):
        if self._add_new_student(student) and self._add_new_students_course(student):
            self.notify(f'"{student.name}" connected to a "{self.name}" course')

    def _add_new_student(self, new_student):
        for student in self.students:
            if student.id == new_student.id:
                return False

        self.students.append(new_student)
        return True

    def _add_new_students_course(self, student):
        for course in student.courses:
            if course.id == self.id:
                return False

        student.courses.append(self)
        return True


class InteractiveCourse(CoursePattern):
    """ Interactive course class """
    type = 'interactive'


class RecordCourse(CoursePattern):
    """ Recorded course class """
    type = 'record'


class CourseFactory:
    """ Course creational pattern factory method """
    types = {
        'interactive': InteractiveCourse,
        'record': RecordCourse
    }

    @classmethod
    def create(cls, type_, name, category, field: str = ''):
        return cls.types[type_](name, category, field)


class Engine:
    """ Main project interface class """
    def __init__(self):
        UnitOfWork.new_current()
        UnitOfWork.get_current().set_mapper_registry(MapperRegistry)
        self.teachers = []

    # @staticmethod
    # def create_category(name, category=None):
    #     return Category(name, category)

    @staticmethod
    def create_course(type_, name, category, field: str = ''):
        return CourseFactory.create(type_, name, category, field)


class SingletonByName(type):
    """ Creational singleton pattern class """
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]
