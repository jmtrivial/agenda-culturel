from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views

from .views import *

urlpatterns = [
    path("", home, name="home"),
    path("semaine/<int:year>/<int:week>/", week_view, name='week_view'),
    path("mois/<int:year>/<int:month>/", month_view, name='month_view'),
    path("jour/<int:year>/<int:month>/<int:day>/", day_view, name='day_view'),
    path("aujourdhui/", day_view, name="aujourdhui"),
    path("cette-semaine/", week_view, name="cette_semaine"),
    path("ce-mois-ci", month_view, name="ce_mois_ci"),
    path("tag/<t>/", view_tag, name='view_tag'),
    path("tags/", tag_list, name='view_all_tags'),
    path("events/", event_list, name='view_all_events'),
    path("event/<int:pk>-<extra>", EventDetailView.as_view(), name="view_event"),
    path("event/<int:pk>/edit", EventUpdateView.as_view(), name="edit_event"),
    path("event/<int:pk>/delete", EventDeleteView.as_view(), name="delete_event"),
    path("importer", EventSubmissionFormView.as_view(), name="event_import_form"),
    path("ajouter", EventCreateView.as_view(), name="add_event"),
    path("admin/", admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path("test_app/", include("test_app.urls")),
    path("static-content/create", StaticContentCreateView.as_view(), name="create_static_content"),
    path("static-content/<int:pk>/edit", StaticContentUpdateView.as_view(), name="edit_static_content"),
    path('rechercher/', event_search, name='event_search')
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
