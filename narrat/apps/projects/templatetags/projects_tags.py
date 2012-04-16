import re

from django import template

from narrat.apps.projects.models import ProjectMember


register = template.Library()


@register.inclusion_tag("projects/project_item.html", takes_context=True)
def show_project(context, project):
    return {"project": project, "request": context["request"]}


@register.inclusion_tag("projects/projectmember_item.html", takes_context=True)
def show_projectmember(context, projectmember):
    return {"projectmember": projectmember, "request": context["request"]}


@register.filter
def is_membership(projectmember, membership):
    if not projectmember:
        return False
    return projectmember.is_membership(membership)


class SetProjectMember(template.Node):
    
    def __init__(self, project, user, var_name):
        self.project = template.Variable(project)
        self.user = template.Variable(user)
        self.var_name = var_name
        
    def render(self, context):
        project = self.project.resolve(context)
        user = self.user.resolve(context)
        
        try:
            projectmember = ProjectMember.objects.get(user=user, project=project)
        except ProjectMember.DoesNotExist:
            projectmember = None
        
        context[self.var_name] = projectmember
        return ''

    @classmethod
    def set_context(cls, parser, token):
        try:
            tag_name, arg = token.contents.split(None, 1)
        except ValueError:
            raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
        # {% set_projectmember project user as projectmember %}
        m = re.search(r'(.*?) (.*?) as (\w+)', arg)
        if not m:
            raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
        project, user, var_name = m.groups()
        return cls(project, user, var_name)


register.tag('set_projectmember', SetProjectMember.set_context)
