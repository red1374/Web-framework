from datetime import datetime
import os
import json

from app.request import Request
from app.response import Response
from uuid import uuid4
from urllib.parse import parse_qs


class BaseMiddleware:
    def to_request(self, request: Request):
        return

    def to_response(self, response: Response):
        return


class Session(BaseMiddleware):
    """ Class to work with session id """
    def to_request(self, request: Request):
        cookie = request.environ.get('HTTP_COOKIE', None)
        if not cookie:
            return

        # -- Get session_id from client request ----------
        try:
            session_id = parse_qs(cookie)['session_id'][0]
        except KeyError:
            return

        request.extra['session_id'] = session_id

    def to_response(self, response: Response):
        """ Setting up a session_id value if exists """
        if not response.request.session_id:
            response.update_headers(
                {'set-Cookie': f'session_id={uuid4()}'}
            )


class GetContent(BaseMiddleware):
    """ Class to work with additional content """
    def to_request(self, request: Request):
        # -- Get site menu items --------------------------
        request.extra['top_menu'] = []
        request.extra['current_url'] = request.url if request.url == '/' else f'/{request.url}'
        request.extra['date'] = datetime.now()

        if request.type == 'html':
            request.extra['top_menu'] = self.get_menu_items(request.settings.get('BASE_DIR'), 'menu')

    def to_response(self, response: Response):
        pass

    def get_menu_items(self, base_dir: str, menu_name: str) -> list:
        """ Get site menu items """
        file_path = os.path.join(base_dir, f'{menu_name}.json')

        if not os.path.isfile(file_path):
            return {}

        try:
            with open(file_path) as f:
                content = json.load(f)
        except json.decoder.JSONDecodeError:
            return []

        return content


middlewares = [
    Session,
    GetContent
]
