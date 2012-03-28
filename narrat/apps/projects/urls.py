from django.conf.urls.defaults import *

from narrat.apps.projects.models import Project
from narrat.apps.projects.views import ProjectCreateView, ProjectDetailView, ProjectUpdateView

from groups.bridge import ContentBridge



bridge = ContentBridge(Project)



urlpatterns = patterns("narrat.apps.projects.views_old",
    url(r"^$", "projects", name="project_list"),
    url(r"^create/$", ProjectCreateView.as_view(), name="project_create"),
    # project-specific
    url(r"^(?P<slug>[-\w]+)/$", ProjectDetailView.as_view(), name="project_detail"),
    url(r"^(?P<slug>[-\w]+)/update/$", ProjectUpdateView.as_view(), name="project_update"),
    url(r"^(?P<slug>[-\w]+)/delete/$", "delete", name="project_delete"),
)

#urlpatterns += bridge.include_urls("pinax.apps.tasks.urls", r"^project/(?P<project_slug>[-\w]+)/tasks/")