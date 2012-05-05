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


class Badge(TagBase):
    class Meta:
        verbose_name = _("Badge")
        verbose_name_plural = _("Badges")


class BadgeItem(GenericTaggedItemBase):
    tag = models.ForeignKey(Badge, related_name="%(app_label)s_%(class)s_items")
    
    class Meta:
        verbose_name = _("Badge Item")
        verbose_name_plural = _("Badge Items")
    
    def __unicode__(self):
        return ugettext("%(object)s with badge %(tag)s") % {
            "object": self.content_object,
            "tag": self.tag
        }