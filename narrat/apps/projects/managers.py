from django.db.models import Manager
from django.db.models.query import QuerySet
from django.db.models import Q


class ProjectMemberQuerySet(QuerySet):
    
    def active(self, **kwargs):
        return self.filter(~Q(membership=4), **kwargs) #not away

class ProjectMemberManager(Manager):
    """
    Manager for ProjectMember model.
    """
    
    def active(self, **kwargs):
        return self.all().active(**kwargs)
    
    def get_query_set(self):
        return ProjectMemberQuerySet(self.model)
    