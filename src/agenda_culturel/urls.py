from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include, re_path


from .views import *

urlpatterns = [
    path("", EventListView.as_view(), name="home"),
    re_path(r'^(?P<mode>' + '|'.join([dm.value for dm in DisplayModes]) + ')/$', view_interval, name='view_interval'),
    path("event/<pk>-<extra>", EventDetailView.as_view(), name="view_event"),
    path("admin/", admin.site.urls),
    path("test_app/", include("test_app.urls")),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
