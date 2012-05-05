from django.conf.urls.defaults import *

from profile.views import ProfileListView, ProfileDetailView, ProfileUpdateView, ProfileRedirectView


urlpatterns = patterns('',
    url(r"^(?P<username>[\w\._-]+)/$", ProfileDetailView.as_view(), name="profile_detail"),
    url(r"^edit/$", ProfileUpdateView.as_view(), name="profile_update"),
    url(r"^all/$", ProfileListView.as_view(), name="profile_list"),
)

urlpatterns += patterns('',
    url(r"^$", ProfileRedirectView.as_view(), name="profile_redirect"),
)