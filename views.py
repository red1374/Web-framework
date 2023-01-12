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
        if self.template_exists(self, request):
            body = build_template(request, {
                'title': 'Text page',
            }, f'{request.url}.html')

            return Response(request, status_code=200, body=body)
        else:
            # -- Return 404-page if template file not found ---
            view = PageNotFound
            return view.get(view, request)

    def template_exists(self, request: Request) -> bool:
        """ Check if template file exists """
        template_path = os.path.join(
            request.settings.get('BASE_DIR'),
            request.settings.get('TEMPLATE_DIR'),
            f'{request.url}.html'
        )

        return os.path.isfile(template_path)
