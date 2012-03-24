from django.conf.urls.defaults import *

from profiles.views import ProfileListView, ProfileDetailView, ProfileUpdateView, ProfileRedirectView


urlpatterns = patterns("profiles.views",
    url(r"^$", ProfileRedirectView.as_view(), name="profile_redirect"),
)

urlpatterns += patterns("idios.views",
    url(r"^all/$", ProfileListView.as_view(), name="profile_list"),
    url(r"^edit/$", ProfileUpdateView.as_view(), name="profile_edit"),
    url(r"^(?P<username>[\w\._-]+)/$", ProfileDetailView.as_view(), name="profile_detail"),
)