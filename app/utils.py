from time import time
from jsonpickle import dumps, loads


class BaseSerializer:
    """ Class to serialize object to json and back"""
    def __init__(self, obj):
        self.obj = obj

    def save(self):
        return dumps(self.obj)

    @staticmethod
    def load(data):
        return loads(data)


class Debug:
    """ Structure decorator for class methods debugging """
    def __init__(self, name):
        self.name = name

    def __call__(self, cls):
        def timeit(method):
            def timed(*args, **kwargs):
                time_start = time()
                result = method(*args, **kwargs)
                time_end = time()
                delta = time_start - time_end

                print(f'Debug --> {self.name} execution time: {delta:2.2f} ms')
                return result
            return timed

        return timeit(cls)
