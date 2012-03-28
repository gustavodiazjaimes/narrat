from django.db import models
from django.db.models import Q


class ProjectMemberManager(models.Manager):
    """
    Manager for ProjectMember model.
    """
    def activemember(self):
        return self.filter(~Q(membership=4)).order_by('membership', 'member_since')