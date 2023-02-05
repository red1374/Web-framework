# -- Main engine exceptions ------------------------------------
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


# -- Database exceptions ------------------------------------
class DbCommitException(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')


class RecordNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')


class TableNameIsEmpty(Exception):
    def __init__(self, model_name):
        super().__init__(model_name)
        self.model_name = model_name

    def __str__(self):
        return f'Table name is empty for model "{self.model_name}"!'


class FieldsListRequired(Exception):
    def __init__(self, model_name):
        super().__init__(model_name)
        self.model_name = model_name

    def __str__(self):
        return f'The fields list must not be empty. Model "{self.model_name}"!'
