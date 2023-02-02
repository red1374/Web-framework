from urllib.parse import parse_qs
import re

EXTRA_PARAMS = re.compile(r'/(?P<id>\d+)/')


class Request:
    __slots__ = ('environ', 'GET', 'POST', 'settings', 'extra', 'url', 'is_post')

    """ Class to work with requests params """

    def __init__(self, environ: dict, settings: dict):
        self.environ = environ
        self.GET = self.build_get_params_dict(environ['QUERY_STRING'])
        self.POST = self.build_post_params_dict(environ['wsgi.input'].read())
        self.settings = settings
        self.extra = {}
        self.url = self._get_url()
        self.get_extra_params()
        self.is_post = environ['REQUEST_METHOD'] == 'POST'

    def __getattr__(self, item):
        return self.extra.get(item)

    def _get_url(self):
        url = self.environ['PATH_INFO'][1:]
        if not url:
            return '/'

        if url[-1] == '/':
            url = url[:-1]

        return url

    def build_get_params_dict(self, raw_params: str):
        """ Getting GET params from the request """
        return parse_qs(raw_params)

    def build_post_params_dict(self, raw_bytes: bytes):
        """ Getting POST params from the request """
        return parse_qs(raw_bytes.decode('utf-8'))

    def get_extra_params(self):
        match = re.search(EXTRA_PARAMS, self.url + '/')
        if match:
            for key, value in match.groupdict().items():
                self.extra[key] = value
