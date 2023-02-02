import os
from app.main import App, FakeApp, LoggerApp
from urls import urlpatterns
from app.middleware import middlewares
from views import routes

settings = {
    'BASE_DIR': os.path.dirname(os.path.abspath(__file__)),
    # 'TEMPLATE_DIR': 'templates',
    'TEMPLATE_DIR': 'templates_jinja',
}
app = App(
    urls=urlpatterns + routes,
    settings=settings,
    middlewares=middlewares
)


fake_app = FakeApp()

logger_app = LoggerApp()
