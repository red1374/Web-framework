import os
from app.main import App
from urls import urlpatterns
from app.middleware import middlewares

settings = {
    'BASE_DIR': os.path.dirname(os.path.abspath(__file__)),
    # 'TEMPLATE_DIR': 'templates',
    'TEMPLATE_DIR': 'templates_jinja',
}
app = App(
    urls=urlpatterns,
    settings=settings,
    middlewares=middlewares
)
