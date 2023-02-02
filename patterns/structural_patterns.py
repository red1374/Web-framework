from time import time

from app.urls import Url


class AppRoute:
    """ Structure pattern decorator for app routing """
    def __init__(self, routes, url):
        self.routes = routes
        self.url = url

    def __call__(self, cls):
        """ Add new route with view class name """
        self.routes.append(Url(self.url, cls))


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
