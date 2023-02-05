from app.model import Model, Mapper


class Student(Model):
    table_name = 'student'
    fields = ('id', 'name')

    def courses_ids(self, mapper):
        return [item.course_id for item in mapper.find({'student_id': self.id})]


class Category(Model):
    table_name = 'category'
    fields = ('id', 'name', 'parent_id')

    def courses(self, mapper):
        return mapper.find({'category_id': self.id})


class Course(Model):
    table_name = 'course'
    fields = ('id', 'name', 'category_id', 'cType')

    @property
    def type(self):
        return self.cType

    @staticmethod
    def get_course_types(connection):
        course_types_mapper = Mapper(CourseTypes, connection)

        return [{'code': item.id, 'name': item.name} for item in course_types_mapper.all()]


class CourseTypes(Model):
    table_name = 'course_type'
    fields = ('id', 'name', 'code')


class StudentCourses(Model):
    table_name = 'student_courses'
    fields = ('id', 'student_id', 'course_id')
