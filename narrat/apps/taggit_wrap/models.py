from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from taggit.models import TagBase, GenericTaggedItemBase, TaggedItemBase


#class Keyword(TagBase):
#    class Meta:
#        verbose_name = _("Keyword")
#        verbose_name_plural = _("Keyword")
#
#
#class KeywordItem(GenericTaggedItemBase):
#    tag = models.ForeignKey(Keyword, related_name="%(app_label)s_%(class)s_items")
#    
#    class Meta:
#        verbose_name = _("Keyword Item")
#        verbose_name_plural = _("Keyword Items")
#    
#    def __unicode__(self):
#        return ugettext("%(object)s has keyword %(tag)s") % {
#            "object": self.content_object,
#            "tag": self.tag
#        }


#class Badge(TagBase):
#    class Meta:
#        verbose_name = _("Badge")
#        verbose_name_plural = _("Badges")
#
#
#class BadgeItem(GenericTaggedItemBase):
#    tag = models.ForeignKey(Badge, related_name="%(app_label)s_%(class)s_items")
#    
#    class Meta:
#        verbose_name = _("Badge Item")
#        verbose_name_plural = _("Badge Items")
#    
#    def __unicode__(self):
#        return ugettext("%(object)s with badge %(tag)s") % {
#            "object": self.content_object,
#            "tag": self.tag
#        }


class KindTaggedBase(models.Model):
    kind_name = ''
    kind = models.CharField(verbose_name=_('Kind'), max_length=100, null=True)
    
    class Meta:
        abstract = True
    
    @classmethod
    def lookup_kwargs(cls, instance):
        return {
            'object_id': instance.pk,
            'content_type': ContentType.objects.get_for_model(instance),
            'kind' : cls.kind_name
        }

    @classmethod
    def bulk_lookup_kwargs(cls, instances):
        # TODO: instances[0], can we assume there are instances.
        return {
            'object_id__in': [instance.pk for instance in instances],
            'content_type': ContentType.objects.get_for_model(instances[0]),
            'kind' : cls.kind_name
        }

    @classmethod
    def tags_for(cls, model, instance=None):
        ct = ContentType.objects.get_for_model(model)
        kwargs = {
            '%s__content_type' % cls.tag_relname(): ct,
            '%s__kind' % cls.tag_relname() : cls.kind_name
        }
        if instance is not None:
            kwargs['%s__object_id' % cls.tag_relname()] = instance.pk
        return cls.tag_model().objects.filter(**kwargs).distinct()


class KindTaggedItem(KindTaggedBase, GenericTaggedItemBase, TaggedItemBase):
    
    class Meta:
        verbose_name = _("Tagged Item")
        verbose_name_plural = _("Tagged Items")


class KeywordTaggedItem(KindTaggedItem):
    kind_name = 'keyword'
    
    class Meta:
        verbose_name = _("Keyword Item")
        verbose_name_plural = _("Keyword Items")
        
        proxy = True


class BadgeTaggedItem(KindTaggedItem):
    kind_name = 'badge'
    
    class Meta:
        verbose_name = _("Badge Item")
        verbose_name_plural = _("Badge Items")
        
        proxy = True
