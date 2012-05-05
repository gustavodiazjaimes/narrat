from django.utils.translation import ugettext as _t
from django.utils.translation import ugettext_lazy as _

from django.conf import settings

from appconf import AppConf


class ProjectConf(AppConf):
    
    ROLES_DISPLAY = (
        ('leader',      _('Leader')),
        ('participant', _('Participant')),
        ('viewer',      _('Viewer')),
        ('away',        _('Away')),
    )
    ROLES = [x for (x, y) in ROLES_DISPLAY]
    
    NO_MEMBER_ROLES = ['away']
    
    PERMISSIONS = (
        ('project_update', _t(u"Project Update")),  # Translation can't be declare lazy becouse string is need when postsyncdb signal
        ('project_delete', _t(u"Project Delete")),
        ('members_update', _t(u"Members Update")),
    )
    
    ROLES_PERMISSIONS = {
        'leader':       ['project_update', 'project_delete', 'members_update'],
        'participant':  [],
        'viewer':       [],
        'away':         [],
    }
