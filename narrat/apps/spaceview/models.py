from django.db import models

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


class NamespaceAware(models.Model):
    """
    A mixin abstract base model to use on models you want to make group-aware.
    """
    
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    content_id = models.PositiveIntegerField(blank=True, null=True)
    space = generic.GenericForeignKey(ct_field="content_type", fk_field="content_id")
    
    class Meta:
        abstract = True
