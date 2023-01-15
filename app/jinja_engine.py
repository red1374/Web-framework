from datetime import datetime
import os

import jinja2.exceptions
from jinja2 import Environment, FileSystemLoader

from app.request import Request


class Engine:
    """ Template engine class """
    def __init__(self, base_dir: str, template_dir: str):
        self.template_dir = os.path.join(base_dir, template_dir)
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def build(self, context: dict, template_name: str) -> str:
        """ Build a result string from template and variables context dict """

        try:
            template = self.env.get_template(template_name)
        except jinja2.exceptions.TemplateNotFound:
            template = self.env.get_template('404.html')

        return template.render(context)


def build_template(request: Request, context: dict, template_name: str) -> str:
    """ Create template engine instance """
    engine = Engine(
        request.settings.get('BASE_DIR'),
        request.settings.get('TEMPLATE_DIR')
    )

    context['extra'] = request.extra

    return engine.build(context, template_name)
