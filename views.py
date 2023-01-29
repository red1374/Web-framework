import os
from datetime import datetime

from app.logger import Logger
from app.request import Request
from app.response import Response
from app.view import View, ListView, TemplateView, CreateView
from app.jinja_engine import build_template
from patterns.behavioral_patterns import BaseSerializer, Notifier
from patterns.structural_patterns import Debug, AppRoute

from patterns.сreational_patterns import Engine

site = Engine()
logger = Logger('views')
notifyer = Notifier()
routes = []

# -- ToDo: Remove this temp solution after db integration
if not site.categories:
    new_category = site.create_category('Test', None)
    site.categories.append(new_category)

if not site.courses:
    new_course = site.create_course('record', 'Test course 1', new_category)
    new_course.observers.append(notifyer)
    site.courses.append(new_course)
    new_course = site.create_course('record', 'Test course 2', new_category)
    new_course.observers.append(notifyer)
    site.courses.append(new_course)

if not site.students:
    new_student = site.create_user('student', 'Test student')
    site.students.append(new_student)
# --------------------------------------------------------


@AppRoute(routes=routes, url='^$')
class HomePageTemplateView(TemplateView):
    template_name = 'main.html'

    @Debug(name='Home_page')
    def set_context_data(self):
        self.context = {
            'time': datetime.now(),
        }


class PageNotFound(View):
    """ View for 404 page """

    def get(self, *args, **kwargs) -> Response:
        body = build_template(self.request, {
            'title': 'Page not found',
        }, '404.html')
        return Response(self.request, status_code=404, body=body)


class SimplePage(View):
    """ View for simple text page """

    def get(self, *args, **kwargs) -> Response:
        if self.template_exists():
            body = build_template(self.request, {}, f'{self.request.url}.html')

            logger.log('info', f'Simple page rendered: {self.request.url}')
            return Response(self.request, status_code=200, body=body)
        else:
            # -- Return 404-page if template file not found ---
            view_object = PageNotFound(self.request)
            return view_object.get()

    def template_exists(self) -> bool:
        """ Check if template file exists """
        template_path = os.path.join(
            self.request.settings.get('BASE_DIR'),
            self.request.settings.get('TEMPLATE_DIR'),
            f'{self.request.url}.html'
        )

        return os.path.isfile(template_path)


@AppRoute(routes=routes, url='^/contacts')
class ContactsPageView(CreateView):
    template_name = 'contacts.html'
    MESSAGES_DIR = 'messages'

    def set_context_data(self):
        success = self.request.GET.get('success')
        success = success[0] if isinstance(success, list) else ""

        self.context = {
            'title': 'Contact us',
            'status': 'success' if success == 'Y' else ''
        }

        if not self.request.is_post:
            self.result['status'] = ''
        if success == 'Y' and not self.request.is_post:
            self.result['status'] = 'success'
        self.update_context_data(self.result)

    @Debug(name='Contacts_page:create_obj')
    def create_obj(self, data):
        """ Process contacts page data """
        has_error = False
        self.result['data']['topic'] = data.get('topic') if data.get('topic') else ''
        self.result['data']['name'] = data.get('name') if data.get('name') else ''
        self.result['data']['email'] = data.get('email') if data.get('email') else ''
        self.result['data']['text'] = data.get('text') if data.get('text') else ''

        if not self.result['data']['topic'] or not self.result['data']['name'] or \
                not self.result['data']['email'] or not self.result['data']['text']:
            has_error = True

        if not has_error:
            logger.log('debug', 'Save new message')
            self.save_result(self.result['data'])
            self.redirect_url = '/contacts/?success=Y'

    @Debug(name='Contacts_page:save_result')
    def save_result(self, data: dict):
        file_name = f'message_{datetime.now().strftime("%Y.%m.%d_%H_%M_%s")}.txt'
        file_path = os.path.join(self.request.settings.get('BASE_DIR'), self.MESSAGES_DIR, file_name)

        message = f'Name: {data.get("name")}\n' \
                  f'Topic: {data.get("topic")}\n' \
                  f'E-mail: {data.get("email")}\n' \
                  f'Text: {data.get("text")}\n'
        with open(file_path, 'w') as f:
            f.write(message)


@AppRoute(routes=routes, url='^/programs/\d+')
class CoursesListView(ListView):
    """ View for courses list page """

    template_name = 'courses.html'

    def set_context_data(self):
        category_id = int(self.request.extra.get('id')) \
            if self.request.extra.get('id') else None
        category = site.find_category_by_id(category_id)

        if category is None:
            self.redirect_url = '/404/'
            return {}

        self.set_queryset(category.courses if category else None)
        self.context = {
            'title': 'Courses' + (' of program ' + category.name if category else ''),
            'url_param': f'{category_id}/' if category_id else '',
            'id': category.id if category else None,
        }


@AppRoute(routes=routes, url='^/create_course')
class CreateCourseCreateView(CreateView):
    """ Create course view """
    template_name = "create_course.html"

    def set_context_data(self):
        categories = [item for item in site.categories if item.category is None]

        self.context = {
            'title': 'New course',
            'programs_list': categories,
            'types_list': site.get_course_types(),
        }
        if not self.request.is_post:
            self.result['status'] = ''
        self.update_context_data(self.result)

    def create_obj(self, data):
        """ Process course data """
        has_error = False

        self.result['data']['name'] = data.get('name') if data.get('name') else ''
        self.result['data']['type'] = data.get('type') if data.get('type') else ''
        self.result['data']['category_id'] = int(data.get('category_id')) if data.get('category_id') else 0
        self.result['data']['category'] = site.find_category_by_id(self.result['data']['category_id'])

        if not self.result['data']['category']:
            self.result['message'] = 'Wrong program id'
            has_error = True

        if not self.result['data']['type']:
            self.result['message'] = 'Course type not selected'

        if self.result['data']['name']:
            if site.find_course_by_name_and_category(self.result['data']['name'], self.result['data']['category_id']):
                self.result['message'] = 'Course with this name already exist in this program'
                has_error = True
        else:
            has_error = True

        if not has_error:
            course_object = site.create_course(
                self.result['data']['type'],
                self.result['data']['name'],
                self.result['data']['category'])

            course_object.observers.append(notifyer)

            site.courses.append(course_object)
            logger.log('debug', f'Create new course: {course_object.name}')

            if self.result['data']['category_id']:
                self.redirect_url = f"/programs/{self.result['data']['category_id']}/"
            else:
                self.redirect_url = '/programs/'


@AppRoute(routes=routes, url='^/edit-course')
class EditCourseCreateView(CreateView):
    """ Edit course view """
    template_name = "edit_course.html"

    def __init__(self, request: Request):
        super().__init__(request)

        course_id = int(self.request.extra.get('id')) \
            if self.request.extra.get('id') else None
        self.course = site.find_course_by_id(course_id)

        if not self.course:
            self.redirect_url = '/404/'
        else:
            if not self.result['data']:
                self.result['data'] = {
                    'name': self.course.name,
                    'type': self.course.type,
                    'category_id': self.course.category.id
                }

    def set_context_data(self):
        categories = [item for item in site.categories if item.category is None]

        self.context = {
            'title': f'Edit course',
            'programs_list': categories,
            'types_list': site.get_course_types(),
        }

        if not self.request.is_post:
            self.result['status'] = ''
        self.update_context_data(self.result)

    def create_obj(self, data):
        """ Process course data """
        has_error = False

        self.result['data']['name'] = data.get('name') if data.get('name') else ''
        self.result['data']['type'] = data.get('type') if data.get('type') else ''
        self.result['data']['category_id'] = int(data.get('category_id')) if data.get('category_id') else 0
        self.result['data']['category'] = site.find_category_by_id(self.result['data']['category_id'])

        if not self.result['data']['category']:
            self.result['message'] = 'Wrong program id'
            has_error = True

        if not self.result['data']['type']:
            self.result['message'] = 'Course type not selected'

        if self.result['data']['name']:
            search_course = site.find_course_by_name_and_category(self.result['data']['name'], self.result['data']['category_id'])
            if search_course:
                if search_course.id != self.course.id:
                    self.result['message'] = 'Course with this name already exist in this program'
                    has_error = True
        else:
            has_error = True

        if not has_error:
            # -- Update course data ----------------------------------
            self.course.name = self.result['data']['name']
            self.course.category = self.result['data']['category']

            self.course.notify_course_users(f'{self.course.name}" course has been updated!')
            self.result['status'] = 'success'


class CopyCourse(View):
    """ View to copy a course """

    def get(self, *args, **kwargs) -> Response:
        course_id = int(self.request.extra.get('id')) \
            if self.request.extra.get('id') else None
        course = site.find_course_by_id(course_id)

        body = build_template(self.request, {}, f'course.html')
        response = Response(self.request, body=body)

        if course is None:
            response.redirect('/404/')
        else:
            new_course = course.clone()
            new_course.name = f'copy_{course.name}'
            new_course.id = new_course.auto_id
            new_course.auto_id += 1

            site.courses.append(new_course)
            logger.log('debug', f'Course been copied: {course.name}')
            response.redirect(f'/programs/{course.category.id}/')

        return response


class CoursePage(View):
    """ Course page view """

    def get(self, *args, **kwargs) -> Response:
        """ Course page rendering """

        course_id = int(self.request.extra.get('id')) \
            if self.request.extra.get('id') else None
        course = site.find_course_by_id(course_id)

        body = build_template(self.request, {
            'title': course.name if course else '',
            'url_param': f'{course.category.id}/' if course else '',
        }, f'course.html')

        response = Response(self.request, body=body)

        if course is None:
            response.redirect('/404/')

        return response


@AppRoute(routes=routes, url='^/programs/add')
class CreateProgram(CreateView):
    """ View for create program page """
    template_name = "create_program.html"

    def set_context_data(self):
        categories = [item for item in site.categories if item.category is None]
        self.context = {
            'title': 'New program',
            'programs_list': categories
        }
        if not self.request.is_post:
            self.result['status'] = ''
        self.update_context_data(self.result)

    def create_obj(self, data):
        """ Process program data """
        has_error = False

        self.result['data']['name'] = data.get('name') if data.get('name') else ''
        self.result['data']['category_id'] = int(data.get('category_id')) if data.get('category_id') else 0
        self.result['data']['category'] = site.find_category_by_id(self.result['data']['category_id'])

        if self.result['data']['name']:
            if site.find_category_by_name_and_parent(self.result['data']['name'], self.result['data']['category_id']):
                self.result['message'] = 'Program with this name already exist in this category'
                has_error = True
        else:
            has_error = True

        if not has_error:
            category_obj = site.create_category(self.result['data']['name'], self.result['data']['category'])
            site.categories.append(category_obj)
            logger.log('debug', f'Create new program: {category_obj.name}')
            self.redirect_url = '/programs/'


@AppRoute(routes=routes, url='^/programs')
class ProgramsListView(ListView):
    template_name = 'programs.html'

    def set_context_data(self):
        category_id = int(self.request.extra.get('id')) \
            if self.request.extra.get('id') else None
        category = site.find_category_by_id(category_id)
        if category_id:
            categories = list(
                filter(lambda item: item.category.id == category_id if item.category else False, site.categories))
        else:
            categories = [item for item in site.categories if item.category is None]

        self.set_queryset(categories)

        self.context = {
            'title': category.name if category else 'Programs',
            'url_param': f'{category_id}/' if category_id else ''
        }


@AppRoute(routes=routes, url='^/students')
class StudentListView(ListView):
    queryset = site.students
    template_name = 'students.html'

    def set_context_data(self):
        self.context = {
            'title': 'Students list',
        }


@AppRoute(routes=routes, url='^/create_student')
class StudentCreateView(CreateView):
    """ View for create student page """
    template_name = 'create_student.html'

    def set_context_data(self):
        self.context = {
            'title': 'Create student',
        }

        if not self.request.is_post:
            self.result['status'] = ''
        self.update_context_data(self.result)

    def create_obj(self, data):
        """ Process student data """
        has_error = False
        if data.get('name'):
            self.result['data']['name'] = data.get('name')

            if site.get_student(self.result['data']['name']):
                self.result['message'] = 'Student with this name already exists'
                has_error = True
        else:
            has_error = True

        if not has_error:
            new_obj = site.create_user('student', self.result['data']['name'])
            site.students.append(new_obj)
            self.result = {
                'message': 'Student has been added!',
                'status': 'success',
                'data': {},
            }


@AppRoute(routes=routes, url='^/api')
class CourseApi(TemplateView):
    template_name = 'json.html'

    @Debug(name='CourseApi')
    def set_context_data(self):
        self.context = {
            'json': BaseSerializer(site.courses).save()
        }


@AppRoute(routes=routes, url='^/student-courses')
class StudentCoursesCreateView(CreateView):
    """ View for changing student's courses list """
    template_name = 'student_courses.html'

    def __init__(self, request: Request):
        super().__init__(request)

        student_id = int(self.request.extra.get('id'))
        student = site.find_student_by_id(student_id)
        self.student = student

    def set_context_data(self):
        self.context = {
            'title': 'Student courses',
            'student': self.student,
            'courses_list': site.courses,
            'courses_ids': [course.id for course in self.student.courses if course]
        }

        if not self.request.is_post:
            self.result['status'] = ''
        self.update_context_data(self.result)

    def create_obj(self, data):
        """ Process form data """
        has_error = False
        courses_ids = []
        courses = []

        if not self.student:
            has_error = True
            self.result['message'] = 'Student not found'

        if data.get('course_id'):
            if isinstance(data.get('course_id'), list):
                courses_ids = data.get('course_id')
            else:
                courses_ids.append(data.get('course_id'))

            for course_id in courses_ids:
                course = site.find_course_by_id(int(course_id))
                if not course:
                    has_error = True
                    self.result['message'] = 'Course not found'
                else:
                    courses.append(course)

        if not has_error:
            if courses:
                # -- Add student to selected courses --
                for course in courses:
                    course.add_student(self.student)
            else:
                # -- Remove student from all courses --
                self.student.clear_courses()

            self.result = {
                'message': 'Courses list has been updated!',
                'status': 'success',
                'data': {},
            }
