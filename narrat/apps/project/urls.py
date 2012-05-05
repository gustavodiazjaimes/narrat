from django.conf.urls.defaults import *

from narrat.apps.project.models import Project
from narrat.apps.project.views import (ProjectCreateView, ProjectDetailView, ProjectUpdateView, ProjectDeleteView,
                                       MemberUpdateSetView)

from groups.bridge import ContentBridge


member_urlpatterns = patterns('',
    url(r"^update/all/$", MemberUpdateSetView.as_view(), name="members_update"),
)

urlpatterns = patterns('',
    #url(r"^$", "projects", name="project_list"),
    url(r"^create/$", ProjectCreateView.as_view(), name="project_create"),
    # project-specific
    url(r"^(?P<project_slug>[-\w]+)/$", ProjectDetailView.as_view(), name="project_detail"),
    url(r"^(?P<project_slug>[-\w]+)/update/$", ProjectUpdateView.as_view(), name="project_update"),
    url(r"^(?P<project_slug>[-\w]+)/delete/$", ProjectDeleteView.as_view(), name="project_delete"),
    url(r"^(?P<project_slug>[-\w]+)/member/", include(member_urlpatterns, namespace='project', app_name='project')),
)