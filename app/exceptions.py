class NotFoundException(Exception):
    code = 404
    text = 'Page not found'


class NotAllowedException(Exception):
    code = 405
    text = 'HTTP method not allowed'


class NotTemplateFile(Exception):
    code = 500

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f'{self.message} is not a file!'


class FileNotFound(Exception):
    code = 500

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f'File "{self.message}" is not found!'
