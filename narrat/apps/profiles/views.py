from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.generic import RedirectView


class ProfileRedirectView(RedirectView):
    
    def get_redirect_url(self):
        return reverse("profile_detail", kwargs={'username': self.request.user.username})
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProfileRedirectView, self).dispatch(*args, **kwargs)
