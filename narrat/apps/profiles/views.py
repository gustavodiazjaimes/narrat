from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView

import idios.views


class ProfileListView(idios.views.ProfileListView):
    template_name = "profiles/profiles.html"


class ProfileUpdateView(idios.views.ProfileUpdateView):
    template_name = "profiles/profile_edit.html"
    template_name_ajax = "profiles/profile_edit_ajax.html"
    template_name_ajax_success = "profiles/profile_edit_ajax_success.html"


class ProfileDetailView(idios.views.ProfileDetailView):
    template_name = "profiles/profile.html"


class ProfileRedirectView(RedirectView):
    permanent = False
    
    def get_redirect_url(self):
        return reverse("profile_detail", kwargs={'username': self.request.user.username})
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProfileRedirectView, self).dispatch(*args, **kwargs)
