import os
import re

from app.exceptions import NotTemplateFile
from app.request import Request

FOR_BLOCK_PATTERN = re.compile(r'{% for (?P<variable>[a-zA-Z]+) in (?P<seq>[a-zA-Z]+) %}(?P<content>[\S\s]+)(?={% endfor %}){% endfor %}')
VARIABLE_PATTERN = re.compile(r'{{ (?P<variable>[a-zA-Z_]+) }}')


class Engine:
    """ Template engine class """
    def __init__(self, base_dir: str, template_dir: str):
        self.template_dir = os.path.join(base_dir, template_dir)

    def _get_template_as_string(self, template_name: str):
        """ Read template file and return it as a string """
        template_path = os.path.join(self.template_dir, template_name)
        if not os.path.isfile(template_path):
            raise NotTemplateFile(template_path)

        with open(template_path) as f:
            return f.read()

    def _build_block(self, context: dict, raw_template_block: str) -> str:
        """ Replace all variables in a template with its values from context dict """
        # -- Getting all variable names in a raw_template_block string
        used_vars = VARIABLE_PATTERN.findall(raw_template_block)

        # -- Replacing variables
        if used_vars is not None:
            for var in used_vars:
                var_in_template = '{{ %s }}' % var
                raw_template_block = re.sub(var_in_template, str(context.get(var, '')), raw_template_block)

        return raw_template_block

    def _build_for_block(self, context: dict, raw_template: str) -> str:
        """ Replace all for statements in template with a string """
        for_block = FOR_BLOCK_PATTERN.search(raw_template)

        if for_block is not None:
            build_for_block = ''
            for i in context.get(for_block.group('seq'), []):
                # -- Replace "for" body with a variables values from a context dict
                build_for_block += self._build_block(
                    {**context, for_block.group('variable'): i},
                    for_block.group('content')
                )
            return FOR_BLOCK_PATTERN.sub(build_for_block, raw_template)

        return raw_template

    def build(self, context: dict, template_name: str) -> str:
        """ Build a result string from template and variables context dict """
        raw_template = self._get_template_as_string(template_name)
        raw_template = self._build_for_block(context, raw_template)

        return self._build_block(context, raw_template)


def build_template(request: Request, context: dict, template_name: str) -> str:
    """ Create template engine instance """
    engine = Engine(
        request.settings.get('BASE_DIR'),
        request.settings.get('TEMPLATE_DIR')
    )

    return ''.join([
        engine.build(context, 'header.html'),
        engine.build(context, template_name),
        engine.build(context, 'footer.html'),
    ])


