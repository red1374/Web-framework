from app.urls import Url
from views import SimplePage, CopyCourse, CoursePage

urlpatterns = [
    Url('^/about', SimplePage),
    Url('^/course/\d+', CoursePage),
    Url('^/copy-course', CopyCourse),
]
