from __future__ import absolute_import
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist, ValidationError, FieldError
from django.db import models
from django.db.models import Count, signals
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst

from permissions import PermissionBase
from permissions.models import Role, PrincipalRoleRelation
from permissions.utils import register_role, register_permission, get_role
from taggit.managers import TaggableManager

from taggit_wrap.models import KeywordTaggedItem, BadgeTaggedItem

from .conf import settings
from .managers import MemberManager


def project_install(sender, **kwargs):
    verbosity = kwargs.get('verbosity', 1)
    
    roles = []
    perms = []
    projects = Project.objects.all()
    
    for role in settings.PROJECT_ROLES:
        r = register_role(role)
        roles.append(r)
    
    for perm in settings.PROJECT_PERMISSIONS:
        p = register_permission(perm[1], perm[0], [Project])
        perms.append(p)
        
    for project in projects:
        project._grant_permissions()
    
    if verbosity > 0:
        if any(roles):
            print "Project roles added:", 
            for r in roles:
                print r, ",",
            else:
                print ""
        
        if any(perms):
            print "Project permissions :",
            for p in perms:
                print p, ",",
            else:
                print ""


class Project(models.Model, PermissionBase):
    """
    
    """
    slug = models.SlugField(_(u"slug"), unique=True)
    name = models.CharField(_(u"name"), max_length=80, unique=True)
    description = models.TextField(_(u"description"))
    started = models.DateTimeField(_(u"started"), default=datetime.now)
    
    # private means only members can see the project
    private = models.BooleanField(_(u"private"), default=False)
    members = generic.GenericRelation('Member', content_type_field='content_type', object_id_field='content_id')
    
    keywords = TaggableManager(through=KeywordTaggedItem, verbose_name=_(u"keywords"))
    # Add science category - http://es.wikipedia.org/wiki/Clasificaci%C3%B3n_Unesco
    # science = ???
    
    class Meta():
        verbose_name = _(u"project")
    
    def __unicode__(self):
        return self.name
    
    def _grant_permissions(self, verbosity=0):
        roles_permissions = {}
        
        for role_name in settings.PROJECT_ROLES_PERMISSIONS.keys():
            roles_permissions[role_name] = []
            role = get_role(role_name)
            
            if not role:
                raise ValidationError(_(u"Role %(role)s doesn't exist") % {role:role_name})
            
            for perm in settings.PROJECT_ROLES_PERMISSIONS[role_name]:
                is_perm = self.grant_permission(role, perm)
                if not is_perm:
                    raise ValidationError(_(u"Permission %(perm)s doesn't exist") % {perm:perm})
                
                roles_permissions[role_name].append(perm)
        
        if verbosity > 1:
            print _(u"%(project)s roles permissions:") % {project : unicode(self)}
            for role in roles_permissions.keys():
                print role, ":",
                for perm in roles_permissions[role]:
                    print perm, ",",
                print ".",
            else:
                print ""
    
    @models.permalink
    def get_absolute_url(self):
        return ('project:project_detail', [], {'project_slug': self.slug})
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
            
        super(Project, self).save(*args, **kwargs)
        
        if is_new:
            self._grant_permissions()
    
    def get_member(self, user):
        if not user or not user.is_authenticated():
            return None
        
        try:
            return self.members.filter(user=user).get()
        except ObjectDoesNotExist:
            return None
    
    def member_count(self):
        return self.members.active().aggregate(Count('pk'))['pk__count']
    
    # PermissionBase rewrite
    def add_role(self, user, role):
        ctype = ContentType.objects.get_for_model(self)
        try:
            Member.objects.get(user=user, role=role, content_type=ctype, content_id=self.pk)
        except PrincipalRoleRelation.DoesNotExist:
            Member.objects.create(user=user, role=role, content_type=ctype, content_id=self.pk)
            return True
        
        return False
    
    # PermissionBase rewrite
    def remove_role(self, user, role=None):
        return self.remove_roles(user)
    
    # PermissionBase rewrite
    def remove_roles(self, user):
        try:
            ctype = ContentType.objects.get_for_model(self)
            pur = PrincipalRoleRelation.objects.filter(user=user, content_id=self.id, content_type=ctype)
        except PrincipalRoleRelation.DoesNotExist:
            return False
        else:
            pur.delete()
        
        return True


class Member(PrincipalRoleRelation):
    """
    
    """
    #user = models.ForeignKey(User, verbose_name=_(u"User"), blank=True, null=True)
    #group = models.ForeignKey(Group, verbose_name=_(u"Group"), blank=True, null=True)
    #role = models.ForeignKey(Role, verbose_name=_(u"Role"))
    #
    #content_type = models.ForeignKey(ContentType, verbose_name=_(u"Content type"), blank=True, null=True)
    #content_id = models.PositiveIntegerField(verbose_name=_(u"Content id"), blank=True, null=True)
    #content = generic.GenericForeignKey(ct_field="content_type", fk_field="content_id")
    
    member_since = models.DateTimeField(_(u"Member Since"), default=datetime.now)
    away_since = models.DateTimeField(_(u"Away Since"), null=True)
    
    badges = TaggableManager(_(u"Badge"), through = BadgeTaggedItem)
    
    objects = MemberManager()
    
    class Meta:
        verbose_name = _(u"project member")
    

    def __init__(self, *args, **kwargs):
        super(Member, self).__init__(*args, **kwargs)
        
        is_new = self.pk is None
        
        self.initial = {}
        self.initial['role'] = self.role if not is_new else None
    
    def __unicode__(self):
        return _(u"%(user)s is %(role)s of %(project)s") % {
            "user": self.user,
            "role": self.role,
            "project": self.content,
        }
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        if is_new:
            self.validate_unique()
        
        if self.role != self.initial['role']:
            no_member_roles = []
            for role in settings.PROJECT_NO_MEMBER_ROLES:
                no_member_roles.append(get_role(role))
            
            if self.role in no_member_roles and not self.away_since:
                self.away_since = datetime.now()
            elif self.initial['role'] in no_member_roles:
                self.away_since = None
        
        super(Member, self).save(*args, **kwargs)
    
    def clean_fields(self, exclude=None):
        return super(Member, self).clean_fields(exclude)
    
    def validate_unique(self, exclude=None):
        if exclude:
            for e in exclude:
                if e in ('user', 'content_type', 'content_id'):
                    return super(Member, self).validate_unique(exclude)
        else:
            is_new = self.pk is None
            model_name = capfirst(self._meta.verbose_name)
            
            ### Validate user != None
            if is_new and self.user == None:
                user_error = _(u"Attribute user is required by %(model_name)s.") % {
                    'model_name' : model_name
                }
                raise ValidationError(user_error)
                
            ### Validate unique_togueter = (user, project)
            try:
                member = Member.objects.get(user=self.user, content_type=self.content_type, content_id=self.content_id)
            except Member.DoesNotExist:
                pass
            else:
                if is_new or self.pk != member.pk:
                    unique_error = _(u"%(model_name)s already exists.") % {
                        'model_name' : model_name
                    }
                    raise ValidationError(unique_error)
        
        return super(Member, self).validate_unique(exclude)
    
    def get_project(self):
        return self.content

    def set_project(self, project):
        if isinstance(project, Project):
            self.content = project
        else:
            instance_error = _(u"%(project)s is not %(cls)s instance") %  {
                'project': unicode(project),
                'cls': Project._meta.verbose_name
            }
            raise ValidationError(instance_error)

    project = property(get_project, set_project)
    
    def is_role(self, role):
        if isinstance(role, basestring):
            role = get_role(role)
        
        return self.role == role
    
    def is_active(self):
        no_member_roles = []
        for role in settings.PROJECT_NO_MEMBER_ROLES:
            no_member_roles.append(get_role(role))
        
        return self.role not in no_member_roles
    
    def get_role_display(self):
        return self.role.name


def add_projects_user(sender, **kwargs):
    user = kwargs['instance']
    
    if hasattr(user, 'project'):
        raise FieldError
    
    setattr(user, 'projects', Member.objects.filter(user=user))

signals.post_init.connect(add_projects_user, sender=User, weak=False, dispatch_uid='project.member')
