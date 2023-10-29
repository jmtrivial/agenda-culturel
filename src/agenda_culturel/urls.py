from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include, re_path


from .views import *

modes = '|'.join([dm.name for dm in DisplayMode])

urlpatterns = [
    path("", home, name="home"),
    re_path(r'^(?P<mode>' + modes + ')/$', view_mode, name='view_mode'),
    re_path(r'^(?P<mode>' + modes + ')/(?P<cat_id>\d+)/$', view_mode_cat, name='view_mode_cat'),
    path("event/<int:pk>-<extra>", EventDetailView.as_view(), name="view_event"),
    path("proposer", EventSubmissionFormView.as_view(), name="event_submission_form"),
    path("admin/", admin.site.urls),
    path("test_app/", include("test_app.urls")),

]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
