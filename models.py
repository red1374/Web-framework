from app.model import Model
from patterns.сreational_patterns import User, CoursePrototype


class Student(Model, User):
    table_name = 'student'
    fields = ('id', 'name')

    def courses_ids(self, mapper):
        return [item.course_id for item in mapper.find({'student_id': self.id})]


class Category(Model):
    """ Category class """
    table_name = 'category'
    fields = ('id', 'name', 'parent_id')

    def courses(self, mapper):
        return mapper.find({'category_id': self.id})


class Course(Model, CoursePrototype):
    table_name = 'course'
    fields = ('id', 'name', 'category_id', 'cType')
    types = [
        {
            'code': 'record',
            'name': 'Record',
        }, {
            'code': 'interactive',
            'name': 'Interactive',
        }
    ]

    @property
    def type(self):
        return self.cType

    @staticmethod
    def get_course_types():
        return Course.types


class StudentCourses(Model):
    table_name = 'student_courses'
    fields = ('id', 'student_id', 'course_id')
