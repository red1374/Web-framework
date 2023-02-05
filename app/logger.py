from datetime import datetime


class SingletonByName(type):
    """ Creational singleton pattern class """
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class ConsoleWriter:
    def write(self, text):
        print(text)


class FileWriter:
    def __init__(self):
        self.name = 'log'

    def write(self, text):
        with open(f'{self.name}.log', 'a+') as f:
            f.write(f'{text}\n')


class Logger(metaclass=SingletonByName):
    """ Logger class """
    def __init__(self, name, writer=FileWriter()):
        self.name = name
        self.writer = writer

    def log(self, message_type: str = 'info', text: str = ''):
        now = datetime.now()
        text = f'{now:%Y-%m-%d %H:%M} [{message_type.upper()}]: {text}'

        self.writer.write(text)
