from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView

import idios.views


class ProfileDetailView(idios.views.ProfileDetailView):
    template_name = "profile/profile_detail.html"


class ProfileUpdateView(idios.views.ProfileUpdateView):
    template_name = "profile/profile_update.html"
    template_name_ajax = "profile/profile_update_ajax.html"
    template_name_ajax_success = "profile/profile_update_ajax_success.html"


class ProfileListView(idios.views.ProfileListView):
    template_name = "profile/profile_list.html"


class ProfileRedirectView(RedirectView):
    permanent = False
    
    def get_redirect_url(self):
        return reverse("profile_detail", kwargs={'username': self.request.user.username})
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProfileRedirectView, self).dispatch(*args, **kwargs)
