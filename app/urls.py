from dataclasses import dataclass
from app.view import View
from typing import Type


@dataclass
class Url:
    url: str
    view: Type[View]


class AppRoute:
    """ Structure pattern decorator for app routing """
    def __init__(self, routes, url):
        self.routes = routes
        self.url = url

    def __call__(self, cls):
        """ Add new route with view class name """
        self.routes.append(Url(self.url, cls))
