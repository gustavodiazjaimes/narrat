import re

from django import template
from django.contrib.auth.models import User
from django.template.loader import render_to_string

import actstream
from actstream.templatetags.activity_tags import AsNode


register = template.Library()


class UserStream(template.Node):
    def __init__(self, actor, var_name):
        self.actor = template.Variable(actor)
        self.var_name = var_name
    def render(self, context):
        actor = self.actor.resolve(context)
        context[self.var_name] = actstream.models.user_stream(actor)
        return ''
    
def do_user_stream(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
    actor, var_name = m.groups()
    return UserStream(actor, var_name)


class DisplayActorAvatar(AsNode):

    def render_result(self, context):
        actor = self.args[0].resolve(context)
        templates = [
            'activity/actor_avatar.html'
        ]
        return render_to_string(templates, {'actor': actor},
            context)
        
def display_actor_avatar(parser, token):
    return DisplayActorAvatar.handle_token(parser, token)


register.tag('user_stream', do_user_stream)
register.tag('display_actor_avatar', display_actor_avatar)