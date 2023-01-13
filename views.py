import os
from datetime import datetime

from app.request import Request
from app.response import Response
from app.view import View
# from app.template_engine import build_template
from app.jinja_engine import build_template


class HomePage(View):
    def get(self, request: Request, *args, **kwargs) -> Response:
        body = build_template(
            request, {
                'time': str(datetime.now()),
                'title': 'Home page',
            },
            'main.html'
        )
        return Response(request, body=body)


class EpicMath(View):
    def get(self, request: Request, *args, **kwargs) -> Response:
        first = request.GET.get('first')
        if not first or not first[0].isnumeric():
            return Response(request, body=f'First is empty or not numeric value')

        second = request.GET.get('second')
        if not second or not second[0].isnumeric():
            return Response(request, body=f'Second is empty or not numeric value')

        return Response(request, body=f'Sum is {int(first[0]) + int(second[0])}')


class Hello(View):
    def get(self, request: Request, *args, **kwargs) -> Response:
        body = build_template(request, {
            'title': 'Hello guest page',
            'name': 'Anonimus'
        }, 'hello.html')
        return Response(request, body=body)

    def post(self, request: Request, *args, **kwargs) -> Response:
        raw_name = request.POST.get('name')
        name = raw_name[0] if raw_name else 'Anonimus'

        body = build_template(request, {'name': name}, 'hello.html')
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
            body = build_template(request, {
                'title': 'Text page',
            }, f'{request.url}.html')

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


class ContactsPage(View):
    MESSAGES_DIR = 'messages'

    def get(self, request: Request, *args, **kwargs) -> Response:
        success = request.GET.get('success')
        success = success[0] if isinstance(success, list) else ""

        body = build_template(request, {
            'title': 'Contacts page',
            'form_status': 'success' if success == 'Y' else ''
        }, 'contacts.html')
        print(request.GET)
        return Response(request, body=body)

    def post(self, request: Request, *args, **kwargs) -> Response:
        form = self.prepare_post_data(request)

        body = build_template(request, {
            'form_data': form.get('data'),
            'form_status': form.get('status'),
            'form_msg': form.get('message'),
        }, 'contacts.html')
        response = Response(request, body=body)

        if form.get('status') == 'success':
            self.save_result(self, request, form.get('data'))
            response.redirect('/contacts/?success=Y')

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
