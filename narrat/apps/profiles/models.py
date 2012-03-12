from django.db import models
from django.utils.translation import ugettext_lazy as _

from idios.models import ProfileBase


class Profile(ProfileBase):
    first_name = models.CharField(_("first name"), max_length=30, null=True, blank=True)
    last_name = models.CharField(_("last name"), max_length=30, null=True, blank=True)
    about = models.TextField(_("about"), null=True, blank=True)
    location = models.CharField(_("location"), max_length=40, null=True, blank=True)
    website = models.URLField(_("website"), null=True, blank=True, verify_exists=False)
    
    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        user = self.user
        user.first_name = self.first_name
        user.last_name = self.last_name
        user.save()