from django.conf.urls.defaults import *


urlpatterns = patterns("",
    url(r"^projects/", include("narrat.apps.projects.urls")),
    url(r"^profiles/", include("pinax.apps.profiles.urls")),
)
