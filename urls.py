from app.urls import Url
from views import HomePage, ContactsPage, SimplePage, Courses, CreateCourse, ProgramsList, CreateProgram, CopyCourse,\
    CoursePage

urlpatterns = [
    # Url('^$', HomePage),
    Url('^/about', SimplePage),
    # Url('^/contacts', ContactsPage),
    Url('^/programs/add', CreateProgram),
    Url('^/programs/\d+', Courses),
    Url('^/programs', ProgramsList),
    Url('^/create_course', CreateCourse),
    Url('^/course/\d+', CoursePage),
    Url('^/copy-course', CopyCourse),
]
