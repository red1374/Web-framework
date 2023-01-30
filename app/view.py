from app.jinja_engine import build_template
from app.request import Request
from app.response import Response

# --- Behavioral patterns - Template method


class View:
    """ Base view class """
    def __init__(self, request: Request):
        self.request = request

    def get(self, *args, **kwargs) -> Response:
        pass

    def post(self, *args, **kwargs) -> Response:
        pass


class TemplateView(View):
    """ Template generator from view class """
    status_code = 200
    headers = []
    context = {}
    template_name = 'blank_template.html'
    redirect_url = ''

    def get_context_data(self):
        return self.context

    def set_context_data(self):
        pass

    def update_context_data(self, data: dict = {}):
        self.context = dict(list(self.context.items()) + list(data.items()))

    def get_template(self):
        return self.template_name

    def render_template_with_context(self) -> Response:
        self.set_context_data()

        template_name = self.get_template()
        context = self.get_context_data()
        body = build_template(self.request, context, template_name)
        response = Response(self.request, body=body, status_code=self.status_code, headers=self.headers)

        if self.redirect_url:
            response.redirect(self.redirect_url)

        return response

    def get(self, *args, **kwargs) -> Response:
        return self.render_template_with_context()

    def post(self, *args, **kwargs) -> Response:
        return self.render_template_with_context()

    # def __call__(self, request):
    #     return self.render_template_with_context()


class ListView(TemplateView):
    queryset = []
    context_object_name = 'objects_list'

    def get_queryset(self):
        return self.queryset

    def set_queryset(self, queryset: dict):
        self.queryset = queryset

    def get_context_object_name(self):
        return self.context_object_name

    def get_context_data(self):
        queryset = self.get_queryset()
        context_object_name = self.get_context_object_name()
        context = {context_object_name: queryset}

        if self.context:
            return dict(list(self.context.items()) + list(context.items()))

        return context


class CreateView(TemplateView):
    template_name = 'create.html'

    def __init__(self, request: Request):
        super().__init__(request)
        self.result = self.get_default_result()

    def get_default_result(self):
        return {
            'status': 'error',
            'data': {},
            'message': 'Fill in all the fields!'
        }

    def get_request_data(self):
        result = {}
        if self.request.POST:
            for key, value in self.request.POST.items():
                result[key] = value if len(value) > 1 else value[0]

        return result

    def create_obj(self, data):
        pass

    def post(self, *args, **kwargs) -> Response:
        post_data = self.get_request_data()
        self.create_obj(post_data)

        return self.render_template_with_context()
