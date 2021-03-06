from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

from pinax.apps.account.openid_consumer import PinaxConsumer


handler500 = "pinax.views.server_error"


urlpatterns = patterns("",
    url(r"^$", direct_to_template, {
        "template": "homepage.html",
        }, name="home"),
    url(r'^lookups/', include("ajax_select.urls")),
    url(r"^admin/invite_user/$", "pinax.apps.signup_codes.views.admin_invite_user", name="admin_invite_user"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^about/", include("about.urls")),
    url(r"^account/", include("pinax.apps.account.urls")),
    #url(r"^openid/", include(PinaxConsumer().urls)),
    url(r'^avatar/', include('avatar.urls')),
    url(r"^user/", include("narrat.apps.profile.urls")),
    url(r"^notices/", include("notification.urls")),
    #url(r"^announcements/", include("announcements.urls")),
    url(r"^activity/", include('narrat.apps.activity_wrap.urls')),
    url(r"^project/", include("narrat.apps.project.urls")),
)


if settings.SERVE_MEDIA:
    urlpatterns += patterns("") + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
