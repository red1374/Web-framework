import os
from datetime import datetime

from gunicorn.http import Request

from app.request import Request
from app.response import Response
from app.view import View
# from app.template_engine import build_template
from app.jinja_engine import build_template
from patterns.structural_patterns import Debug, AppRoute

from patterns.сreational_patterns import Engine, Logger

site = Engine()
logger = Logger('views')
routes = []

# -- ToDo: Remove this temp solution after db integration
if not site.categories:
    new_category = site.create_category('Test', None)
    site.categories.append(new_category)


@AppRoute(routes=routes, url='^$')
class HomePage(View):
    @Debug(name='Home_page')
    def get(self, request: Request, *args, **kwargs) -> Response:
        body = build_template(
            request, {
                'time': str(datetime.now()),
            },
            'main.html'
        )
        return Response(request, body=body)


class PageNotFound(View):
    """ View for 404 page """
    def get(self, request: Request, *args, **kwargs) -> Response:
        body = build_template(request, {
            'title': 'Page not found',
        }, '404.html')
        return Response(request, status_code=404, body=body)


class SimplePage(View):
    """ View for simple text page """
    def get(self, request: Request, *args, **kwargs) -> Response:
        if self.template_exists(request):
            body = build_template(request, {}, f'{request.url}.html')

            logger.log('info', f'Simple page rendered: {request.url}')
            return Response(request, status_code=200, body=body)
        else:
            # -- Return 404-page if template file not found ---
            view = PageNotFound
            return view.get(view, request)

    @staticmethod
    def template_exists(request: Request) -> bool:
        """ Check if template file exists """
        template_path = os.path.join(
            request.settings.get('BASE_DIR'),
            request.settings.get('TEMPLATE_DIR'),
            f'{request.url}.html'
        )

        return os.path.isfile(template_path)


@AppRoute(routes=routes, url='^/contacts')
class ContactsPage(View):
    MESSAGES_DIR = 'messages'

    @Debug(name='Contacts_page:get')
    def get(self, request: Request, *args, **kwargs) -> Response:
        success = request.GET.get('success')
        success = success[0] if isinstance(success, list) else ""

        body = build_template(request, {
            'form_status': 'success' if success == 'Y' else ''
        }, 'contacts.html')
        return Response(request, body=body)

    @Debug(name='Contacts_page:post')
    def post(self, request: Request, *args, **kwargs) -> Response:
        form = self.prepare_post_data(request)

        body = build_template(request, {
            'form_data': form.get('data'),
            'form_status': form.get('status'),
            'form_msg': form.get('message'),
        }, 'contacts.html')
        response = Response(request, body=body)

        if form.get('status') == 'success':
            logger.log('debug', 'Save new message')
            self.save_result(self, request, form.get('data'))

        return response

    @staticmethod
    def prepare_post_data(request: Request) -> dict:
        result = {
            'status': 'error',
            'data': {
            },
            'message': 'Fill in all the fields!'
        }

        raw_email = request.POST.get('email')
        email = raw_email[0].strip() if raw_email else ''

        raw_text = request.POST.get('text')
        text = raw_text[0].strip() if raw_text else ''

        raw_topic = request.POST.get('topic')
        topic = raw_topic[0].strip() if raw_topic else ''

        if email and text and topic:
            result['status'] = 'success'
            result['message'] = 'ok!'

        result['data'] = {
            'topic': topic,
            'email': email,
            'text': text
        }

        return result

    def save_result(self, request: Request, data: dict):
        file_name = f'message_{datetime.now().strftime("%Y.%m.%d_%H_%M_%s")}.txt'
        file_path = os.path.join(request.settings.get('BASE_DIR'), self.MESSAGES_DIR, file_name)

        message = f'Topic: {data.get("topic")}\n' \
                  f'E-mail: {data.get("email")}\n' \
                  f'Text: {data.get("text")}\n'
        with open(file_path, 'w') as f:
            f.write(message)


class ProgramsList(View):
    """ View for programs list page """

    def get(self, request: Request, *args, **kwargs) -> Response:
        category_id = int(request.extra.get('id')) if request.extra.get('id') else None
        category = site.find_category_by_id(category_id)
        if category_id:
            categories = list(
                filter(lambda item: item.category.id == category_id if item.category else False, site.categories))
        else:
            categories = [item for item in site.categories if item.category is None]

        body = build_template(request, {
            'objects_list': categories,
            'title': category.name if category else 'Programs',
            'url_param': f'{category_id}/' if category_id else '',
        }, f'programs.html')

        return Response(request, body=body)


class CreateProgram(View):
    """ View for create program page """

    def get(self, request: Request, *args, **kwargs) -> Response:
        """ Get program creating form """
        categories = [item for item in site.categories if item.category is None]

        body = build_template(request, {
            'objects_list': categories,
        }, f'create_program.html')

        return Response(request, body=body)

    def post(self, request: Request, *args, **kwargs) -> Response:
        """ Create new program method """
        categories = [item for item in site.categories if item.category is None]

        form = self.process_data(request)

        body = build_template(request, {
            'objects_list': categories,
            'form_status': form.get('status'),
            'form_msg': form.get('message'),
            'form_data': form.get('data'),
        }, f'create_program.html')
        response = Response(request, body=body)

        if form.get('status') == 'success':
            new_category = site.create_category(form['data'].get('name'), form['data'].get('category'))
            site.categories.append(new_category)
            logger.log('debug', f'Create new program: {new_category.name}')
            response.redirect('/programs/')

        return response

    @staticmethod
    def process_data(request: Request) -> dict:
        """ Process program data """
        result = {
            'status': 'error',
            'data': {
            },
            'message': 'Fill in all the fields!'
        }
        data = {}

        raw_name = request.POST.get('name')
        data['name'] = raw_name[0].strip() if raw_name else ''
        if data['name']:
            result['message'] = 'Ok!'
            result['status'] = 'success'

        raw_category_id = request.POST.get('category_id')
        data['category_id'] = int(raw_category_id[0].strip()) if raw_category_id else 0

        data['category'] = None
        if data['category_id']:
            data['category'] = site.find_category_by_id(data['category_id'])

        if site.find_category_by_name_and_parent(data['name'], data['category_id']):
            result['message'] = 'Program with this name already exist in this category'
            result['status'] = 'error'

        result['data'] = data

        return result


class Courses(View):
    """ View for courses list page """

    def get(self, request: Request, *args, **kwargs) -> Response:
        category_id = int(request.extra.get('id')) if request.extra.get('id') else None
        category = site.find_category_by_id(category_id)

        body = build_template(request, {
            'objects_list': category.courses if category else None,
            'title': 'Courses' + (' of program ' + category.name if category else ''),
            'id': category.id if category else None,
            'url_param': f'{category_id}/' if category_id else '',
        }, f'courses.html')

        response = Response(request, status_code=200, body=body)
        if category is None:
            response.redirect('/404/')

        return response


class CreateCourse(View):
    """ Create course view """
    def get(self, request: Request, *args, **kwargs) -> Response:
        """ Get course creating form """
        categories = [item for item in site.categories if item.category is None]
        category_id = int(request.extra.get('id')) if request.extra.get('id') else None
        body = build_template(request, {
            'objects_list': categories,
            'id': category_id,
            'types_list': site.get_course_types()
        }, f'create_course.html')
        return Response(request, body=body)

    def post(self, request: Request, *args, **kwargs) -> Response:
        """ Create new course method """

        category_id = int(request.extra.get('id')) if request.extra.get('id') else None
        categories = [item for item in site.categories if item.category is None]

        form = self.process_data(request)
        category = site.find_category_by_id(form['data'].get('category_id'))

        status = form.get('status') if category else 'error'
        message = form.get('message') if category else 'Wrong program id'

        body = build_template(request, {
            'objects_list': categories,
            'form_status': status,
            'form_msg': message,
            'form_data': form.get('data'),
            'types_list': site.get_course_types()
        }, f'create_course.html')
        response = Response(request, body=body)

        if status == 'success':
            new_course = site.create_course(
                form['data'].get('type'),
                form['data'].get('name'),
                category)

            site.courses.append(new_course)
            logger.log('debug', f'Create new course: {new_course.name}')

            if category_id:
                response.redirect(f'/programs/{category_id}/')
            else:
                response.redirect('/programs/')

        return response

    @staticmethod
    def process_data(request: Request) -> dict:
        """ Process course data """
        result = {
            'status': 'error',
            'data': {
            },
            'message': 'Fill in all the fields!'
        }
        data = {}

        raw_name = request.POST.get('name')
        data['name'] = raw_name[0].strip() if raw_name else ''
        if data['name']:
            result['message'] = 'Ok!'
            result['status'] = 'success'

        raw_category_id = request.POST.get('category_id')
        data['category_id'] = int(raw_category_id[0].strip()) if raw_category_id else 0

        data['category'] = None
        if data['category_id']:
            data['category'] = site.find_category_by_id(data['category_id'])

        if site.find_category_by_name_and_parent(data['name'], data['category_id']):
            result['message'] = 'Course with this name already exist in this category'
            result['status'] = 'error'

        raw_type = request.POST.get('type')
        data['type'] = raw_type[0].strip() if raw_type else None
        if data['type'] is None:
            result['message'] = 'Course type not selected'
            result['status'] = 'error'

        result['data'] = data

        return result


class CopyCourse(View):
    """ View to copy a course """
    def get(self, request: Request, *args, **kwargs) -> Response:
        course_id = int(request.extra.get('id')) if request.extra.get('id') else None
        course = site.find_course_by_id(course_id)

        body = build_template(request, {}, f'course.html')
        response = Response(request, body=body)

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
    def get(self, request: Request, *args, **kwargs) -> Response:
        """ Course page rendering """

        course_id = int(request.extra.get('id')) if request.extra.get('id') else None
        course = site.find_course_by_id(course_id)

        body = build_template(request, {
            'title': course.name if course else '',
            'url_param': f'{course.category.id}/' if course else '',
        }, f'course.html')

        response = Response(request, body=body)

        if course is None:
            response.redirect('/404/')

        return response
