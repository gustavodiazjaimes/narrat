from __future__ import absolute_import

from django.db.models import Manager
from django.db.models.query import QuerySet
from django.db.models import Q

from permissions.utils import get_role

from .conf import settings


class MemberQuerySet(QuerySet):
    """
    Manager for Member model.
    """
    
    def active(self, **kwargs):
        no_member_roles = []
        for role in settings.PROJECT_NO_MEMBER_ROLES:
            no_member_roles.append(get_role(role))
        
        return self.filter(~Q(role__in=no_member_roles), **kwargs)

class MemberManager(Manager):
    """
    Manager for Member model.
    """
    
    def active(self, **kwargs):
        return self.get_query_set().active(**kwargs)
    
    def get_query_set(self):
        return MemberQuerySet(self.model)
    