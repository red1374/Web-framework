# -- Behavioral pattern Strategy
from datetime import datetime

from patterns.сreational_patterns import SingletonByName


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
