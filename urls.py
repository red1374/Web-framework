from app.urls import Url
from views import HomePage, EpicMath, ContactsPage, SimplePage

urlpatterns = [
    Url('^$', HomePage),
    Url('^/math$', EpicMath),
    # Url('^/hello$', Hello),
    Url('^/about', SimplePage),
    Url('^/contacts', ContactsPage),
]
