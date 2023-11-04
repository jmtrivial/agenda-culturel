from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views

from .views import *

modes = '|'.join([dm.name for dm in DisplayMode])

urlpatterns = [
    path("", home, name="home"),
    re_path(r'^(?P<mode>' + modes + ')/$', view_mode, name='view_mode'),
    re_path(r'^(?P<mode>' + modes + ')/(?P<cat_id>\d+)/$', view_mode_cat, name='view_mode_cat'),
    path("tag/<t>/", view_tag, name='view_tag'),
    path("tags/", tag_list, name='view_all_tags'),
    path("events/", event_list, name='view_all_events'),
    path("event/<int:pk>-<extra>", EventDetailView.as_view(), name="view_event"),
    path("importer", EventSubmissionFormView.as_view(), name="event_import_form"),
    path("admin/", admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path("test_app/", include("test_app.urls")),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
