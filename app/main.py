import os
import re

from typing import List, Type
import mimetypes

from app.urls import Url
from app.exceptions import NotFoundException, NotAllowedException
from app.view import View
from app.request import Request
from app.response import Response
from app.middleware import BaseMiddleware
from views import PageNotFound

IMAGES = re.compile('^.+(jpg|jpeg|gif|png|ico)$')


class App:
    __slots__ = ('urls', 'settings', 'middlewares')

    def __init__(self, urls: List[Url], settings: dict, middlewares: List[Type[BaseMiddleware]]):
        self.urls = urls
        self.settings = settings
        self.middlewares = middlewares

    def __call__(self, environ, start_response, **kwargs):
        # -- Getting static file content if exists ----------
        static = self._get_static_file(environ)

        # -- Prepare request object --------------------------
        request = self._get_request(environ)
        request.extra['type'] = 'html' if not static else 'static'
        self._apply_middleware_to_request(request)

        if not static:
            # -- Getting view for current request if exists --

            view = self._get_view(environ)
            response = self._get_response(environ, view, request)
        else:
            response = Response(request, body=static['data'], headers=static['headers'])

        self._apply_middleware_to_response(response)

        # -- Return response from a view or transferring static file ------
        start_response(str(response.status_code), response.headers.items())

        return iter([response.body])

    def _prepare_url(self, url: str):
        """ Remove last slash """
        if url[-1] == '/':
            return url[:-1]
        return url

    def _find_view(self, raw_url):
        """ Find view for current url """
        url = self._prepare_url(raw_url)
        for path in self.urls:
            m = re.match(path.url, url)
            if m is not None:
                return path.view

        raise NotFoundException

    def _get_view(self, environ: dict) -> View:
        """ Get view from url """
        raw_url = environ['PATH_INFO']

        try:
            view = self._find_view(raw_url)
        except NotFoundException:
            view = PageNotFound

        return view

    def _get_static_file(self, environ: dict):
        """ Get static file content and headers """
        path_list = environ['PATH_INFO'].replace('\\', '/').split('/')
        file_path = os.path.join(*path_list)
        content_type = 'plain/text'

        if not os.path.isfile(file_path):
            return None

        data = open(file_path, 'rb').read()

        mime_type, encoding = mimetypes.guess_type(path_list[-1])

        return {
            'data': data,
            'headers': {
                'Content-Length': str(os.stat(file_path).st_size),
                'Content-Type': mime_type if mime_type else content_type
            }
        }

    def _get_request(self, environ: dict) -> Request:
        """ Parse request parameters """
        return Request(environ, self.settings)

    def _get_response(self, environ: dict, view: View, request: Request) -> Response:
        """ Get response from a view """
        method = environ['REQUEST_METHOD'].lower()

        # -- Call view method if exists -------------
        if not hasattr(view, method):
            raise NotAllowedException

        view_object = view(request)
        return getattr(view_object, method)()

    def _apply_middleware_to_request(self, request: Request):
        for i in self.middlewares:
            i().to_request(request)

    def _apply_middleware_to_response(self, response: Response):
        for i in self.middlewares:
            i().to_response(response)


class FakeApp:
    """ Fake WSGI application """
    def __init__(self):
        pass

    def __call__(self, environ, start_response, **kwargs):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        response_body = b"Hello from Fake"

        start_response(status, response_headers)

        return [response_body]


class LoggerApp:
    """ WSGI application that prints request information"""
    def __init__(self):
        pass

    def __call__(self, environ, start_response, **kwargs):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        response_body = 'Request information:\n'
        response_body += f'   Method: {environ["REQUEST_METHOD"]}\n'
        response_body += f'   Request URI: {environ["PATH_INFO"]}\n'
        response_body += f'   Get params: {environ["QUERY_STRING"]}\n'

        start_response(status, response_headers)

        return [response_body.encode('utf-8')]
