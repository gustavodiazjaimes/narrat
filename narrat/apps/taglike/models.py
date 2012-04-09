from django.db import models
from django.utils.translation import ugettext_lazy as _

from taggit.models import TagBase, ItemBase, GenericTaggedItemBase


class Keyword(TagBase):
    class Meta:
        verbose_name = _("Keyword")
        verbose_name_plural = _("Keyword")


class KeywordItem(GenericTaggedItemBase):
    tag = models.ForeignKey(Keyword, related_name="%(app_label)s_%(class)s_items")
    
    class Meta:
        verbose_name = _("Keyword Item")
        verbose_name_plural = _("Keyword Items")
    
    def __unicode__(self):
        return ugettext("%(object)s has keyword %(tag)s") % {
            "object": self.content_object,
            "tag": self.tag
        }


class Role(TagBase):
    class Meta:
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")


class RollItem(GenericTaggedItemBase):
    tag = models.ForeignKey(Role, related_name="%(app_label)s_%(class)s_items")
    
    class Meta:
        verbose_name = _("Role Item")
        verbose_name_plural = _("Role Items")
    
    def __unicode__(self):
        return ugettext("%(object)s with role %(tag)s") % {
            "object": self.content_object,
            "tag": self.tag
        }