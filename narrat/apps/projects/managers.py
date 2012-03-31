from django.db import models
from django.db.models import Q


class ProjectManager(models.Manager):
    """
    Manager for ProjectMember model.
    """
    def member_count(self):
        return self.filter(~Q(membership=4))


class ProjectMemberManager(models.Manager):
    """
    Manager for ProjectMember model.
    """
    def activemember(self):
        return self.filter(~Q(membership=4))