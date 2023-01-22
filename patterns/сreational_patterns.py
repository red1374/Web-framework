import datetime
from copy import deepcopy
from quopri import decodestring


class User:
    """ User class """
    pass


class Teacher(User):
    """ Teacher class """
    pass


class Student(User):
    """ Student class """
    pass


class UserFactory:
    """ User creation class of type factory method """
    types = {
        'student': Student,
        'teacher': Teacher
    }

    @classmethod
    def create(cls, type_):
        """ Creation pattern factory method """
        return cls.types[type_]()


class CoursePrototype:
    """ Courses creation pattern of Prototype type """
    def clone(self):
        return deepcopy(self)


class Course(CoursePrototype):
    auto_id = 1
    """ Course class """

    def __init__(self, name, category, field: str = ''):
        self.id = Course.auto_id
        Course.auto_id += 1
        self.name = name
        self.category = category
        self.category.courses.append(self)
        self.field = field


class InteractiveCourse(Course):
    """ Interactive course class """
    pass


class RecordCourse(Course):
    """ Recorded course class """
    pass


class CourseFactory:
    """ Course creation pattern factory method """
    types = {
        'interactive': InteractiveCourse,
        'record': RecordCourse
    }

    @classmethod
    def create(cls, type_, name, category, field: str = ''):
        return cls.types[type_](name, category, field)


class Category:
    """ Category class """
    auto_id = 1

    def __init__(self, name, category):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.category = category
        self.courses = []

    def course_count(self):
        result = len(self.courses)
        if self.category:
            result += self.category.course_count()
        return result


class Engine:
    _course_types = [
        {
            'code': 'record',
            'name': 'Record',
        }, {
            'code': 'interactive',
            'name': 'Interactive',
        }
    ]

    """ Main project interface class """
    def __init__(self):
        self.teachers = []
        self.students = []
        self.courses = []
        self.categories = []

    @staticmethod
    def create_user(type_):
        return UserFactory.create(type_)

    @staticmethod
    def create_category(name, category=None):
        return Category(name, category)

    def find_category_by_id(self, id):
        for item in self.categories:
            if item.id == id:
                return item
        return None

    def find_category_by_name_and_parent(self, name, parent_id):
        for item in self.categories:
            if item.name == name:
                if item.category:
                    if item.category.id == parent_id:
                        return item
                else:
                    return item

        return False

    @staticmethod
    def create_course(type_, name, category, field: str = ''):
        return CourseFactory.create(type_, name, category, field)

    def get_course_by_name(self, name):
        for item in self.courses:
            if item.name == name:
                return item
        return None

    def find_course_by_id(self, id):
        for item in self.courses:
            if item.id == id:
                return item
        return None

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = decodestring(val_b)
        return val_decode_str.decode('UTF-8')

    def get_course_types(self) -> dict:
        return self._course_types


class SingletonByName(type):
    """ Creation singleton pattern class """
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


class Logger(metaclass=SingletonByName):
    """ Logger class """
    def __init__(self, name):
        self.name = name

    def log(self, message_type: str = 'info', text: str = ''):
        now = datetime.datetime.now()

        with open(f'{self.name}.log', 'a+') as f:
            f.write(f'{now:%Y-%m-%d %H:%M} [{message_type.upper()}]: {text}\n')
