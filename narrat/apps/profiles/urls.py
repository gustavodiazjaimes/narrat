from django.conf.urls.defaults import *

from idios.views import ProfileListView, ProfileDetailView, ProfileCreateView, ProfileUpdateView


urlpatterns = patterns("idios.views",
    url(r"^$", ProfileListView.as_view(), name="profile_list"),
    url(r"^edit/$", ProfileUpdateView.as_view(), name="profile_edit"),
    url(r"^(?P<username>[\w\._-]+)/$", ProfileDetailView.as_view(), name="profile_detail"),
)