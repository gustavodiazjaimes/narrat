from __future__ import absolute_import
import re

from django import template

from permissions.utils import get_role

from ..models import Project, Member


register = template.Library()


@register.filter
def is_role(member, role):
    if not member or not isinstance(member, Member):
        return False
    
    return member.is_role(role)


@register.filter
def has_perm(member, perm):
    if not member or not isinstance(member, Member):
        return False
    
    user = member.user
    project = member.project
    
    return project.has_permission(user, perm)


@register.assignment_tag()
def set_member(project, user):
    if not project or not isinstance(project, Project):
        return None
    elif not user or not user.is_authenticated():
        return None
    
    return project.get_member(user)


@register.inclusion_tag("project/_project_item.html", takes_context=True)
def show_project(context, project):
    return {"request": context["request"], "project": project}


@register.inclusion_tag("project/_member_item.html", takes_context=True)
def show_member(context, member, data="info"):
    return {"request": context["request"], "member": member, "data": data }
    

#class SetMember(template.Node):
#    
#    def __init__(self, project, user, var_name):
#        self.project = template.Variable(project)
#        self.user = template.Variable(user)
#        self.var_name = var_name
#        
#    def render(self, context):
#        project = self.project.resolve(context)
#        user = self.user.resolve(context)
#        
#        context[self.var_name] = project.get_member(user)
#        return ''
#
#    @classmethod
#    def set_context(cls, parser, token):
#        try:
#            tag_name, arg = token.contents.split(None, 1)
#        except ValueError:
#            raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
#        # {% set_projectmember project user as projectmember %}
#        m = re.search(r'(.*?) (.*?) as (\w+)', arg)
#        if not m:
#            raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
#        project, user, var_name = m.groups()
#        return cls(project, user, var_name)
#
#register.tag('set_member', SetMember.set_context)
