from datetime import datetime

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict

from django.contrib.auth.models import User

from groups.base import Group

from narrat.apps.projects import managers


class Project(Group):
    
    member_users = models.ManyToManyField(User,
        through = "ProjectMember",
        verbose_name = _("members")
    )
    
    # private means only members can see the project
    private = models.BooleanField(_("private"), default=False)
    
    @models.permalink
    def get_absolute_url(self):
        return ("project_detail", [], {"slug": self.slug})
    
    def member_queryset(self):
        return self.member_users.filter(~Q(projects__membership=ProjectMember.MEMBERSHIP['Away']))
    
    def user_is_member(self, user):
         return ProjectMember.objects.filter(project=self, user=user).exists()


class ProjectMember(models.Model):
    
    MEMBERSHIP = {
        'Leader' : 1,
        'Participant' : 2,
        'Viewer' : 3,
        'Away' : 4
    }
    MEMBERSHIP_REVERSE = dict((y, x) for (x, y) in MEMBERSHIP.iteritems())
    MEMBERSHIP_CHOICES = (
        (MEMBERSHIP['Leader'],      _('Leader')),
        (MEMBERSHIP['Participant'], _('Participant')),
        (MEMBERSHIP['Viewer'],      _('Viewer')),
        (MEMBERSHIP['Away'],        _('Away')),
    )
    MEMBERSHIP_CHOICES_DISPLAY = dict(MEMBERSHIP_CHOICES)
    
    project = models.ForeignKey(Project,
        related_name = "members",
        verbose_name = _("project")
    )
    user = models.ForeignKey(User,
        related_name = "projects",
        verbose_name = _("user")
    )
    membership = models.PositiveSmallIntegerField(_("member type"),
        choices = MEMBERSHIP_CHOICES,
        default = MEMBERSHIP['Participant'],
    )
    member_since = models.DateTimeField(_("away since"), default=datetime.now)
    away_since = models.DateTimeField(_("away since"), default=datetime.now)
    
    objects = managers.ProjectMemberManager()
    
    class Meta:
        unique_together = [("user", "project")]
    
    def __init__(self, *args, **kwargs):
        super(ProjectMember, self).__init__(*args, **kwargs)
        self.membership_0 = self.membership
    
    def save(self, *args, **kwargs):
        if self.membership != self.membership_0 and self.membership == ProjectMember.MEMBERSHIP['Away']:
            self.away_since = datetime.now
        super(ProjectMember, self).save(*args, **kwargs)
    
    def get_membership(self):
        return ProjectMember.MEMBERSHIP_REVERSE[self.membership]
    
    def get_membership_display(self):
        return ProjectMember.MEMBERSHIP_CHOICES_DISPLAY[self.membership]
