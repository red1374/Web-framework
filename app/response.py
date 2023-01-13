from app.request import Request


class Response:
    """ Create and manipulate with response """
    def __init__(self, request: Request, status_code: int = 200, headers: dict = None, body: str = ''):
        # -- Set default values ---------
        self.status_code = status_code
        self.headers = {}
        self.body = b''
        self._set_default_headers()
        self.request = request
        self.extra = {}
        self.menu = {}

        if headers is not None:
            self.update_headers(headers)
        self._set_body(body)

    def __getattr__(self, item):
        return self.extra.get(item)

    def _set_default_headers(self):
        """ Set default headers """
        self.headers = {
            'Content-Type': 'text/html; charset=utf-8',
            'Content-Length': 0,
        }

    def _set_body(self, raw_body: str = ''):
        """ Set body value """
        if not isinstance(raw_body, str):
            # -- For static files --------------------
            self.body = raw_body
        else:
            # -- Encode document string --------------
            self.body = raw_body.encode('utf-8')
            self.update_headers(
                {'Content-Length': str(len(self.body))}
            )

    def update_headers(self, headers: dict):
        """ Update response headers """
        self.headers.update(headers)

    def redirect(self, url, status_code: int = 301):
        """ Redirect to a new url """
        self.status_code = status_code
        self.update_headers({
            'Location': url
        })
