from copy import deepcopy
from quopri import decodestring

from patterns.architectural_system_pattern_unit_of_work import DomainObject
from patterns.behavioral_patterns import Subject


class User:
    """ User class """
    def __init__(self, name):
        self.name = name


class Teacher(User):
    """ Teacher class """
    pass


class Student(User, DomainObject):
    """ Student class """
    auto_id = 1

    def __init__(self, name):
        self.id = Student.auto_id
        Student.auto_id += 1
        self.courses = []
        super().__init__(name)

    def clear_courses(self):
        self._delete_student_from_courses()
        self.courses = []

    def _delete_student_from_courses(self):
        for course in self.courses:
            for student in course.students:
                if self.id == student.id:
                    course.students.remove(student)
                    break


class UserFactory:
    """ User creation class of type factory method """
    types = {
        'student': Student,
        'teacher': Teacher,
    }

    @classmethod
    def create(cls, type_, name):
        """ Creation pattern factory method """
        return cls.types[type_](name)


class CoursePrototype:
    """ Courses creation pattern of Prototype type """
    def clone(self):
        return deepcopy(self)


class Course(CoursePrototype, Subject):
    auto_id = 1
    """ Course class """

    def __init__(self, name, category, field: str = ''):
        self.id = Course.auto_id
        Course.auto_id += 1
        self.name = name
        self.category = category
        self.category.courses.append(self)
        self.field = field
        self.students = []
        super().__init__()

    def __getitem__(self, item):
        return self.students[item]

    def add_student(self, student: Student):
        if self._add_new_student(student) and self._add_new_students_course(student):
            self.notify(f'"{student.name}" connected to a "{self.name}" course')

    def _add_new_student(self, new_student: Student):
        for student in self.students:
            if student.id == new_student.id:
                return False

        self.students.append(new_student)
        return True

    def _add_new_students_course(self, student: Student):
        for course in student.courses:
            if course.id == self.id:
                return False

        student.courses.append(self)
        return True


class InteractiveCourse(Course):
    """ Interactive course class """
    type = 'interactive'


class RecordCourse(Course):
    """ Recorded course class """
    type = 'record'


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
    def create_user(type_, name):
        return UserFactory.create(type_, name)

    @staticmethod
    def create_category(name, category=None):
        return Category(name, category)

    @staticmethod
    def create_course(type_, name, category, field: str = ''):
        return CourseFactory.create(type_, name, category, field)

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

    def get_course_by_name(self, name):
        for item in self.courses:
            if item.name == name:
                return item
        return None

    def find_course_by_name_and_category(self, name: str, category_id: int):
        for item in self.courses:
            if item.name == name:
                if item.category:
                    if item.category.id == category_id:
                        return item
                else:
                    return item

        return False

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

    def get_student(self, name) -> Student:
        for item in self.students:
            if item.name == name:
                return item
        return None

    def find_student_by_id(self, id: int):
        for item in self.students:
            if item.id == id:
                return item
        return None

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
