import re

from django import template
from django.contrib.auth.models import User
from django.template.loader import render_to_string

import actstream
from actstream.models import actor_stream, action_object_stream, target_stream, user_stream, model_stream
from actstream.templatetags.activity_tags import AsNode


register = template.Library()


STREAMS = {
        "actor_stream" : actor_stream,
        "action_object_stream" : action_object_stream,
        "target_stream" : target_stream,
        "user_stream" : user_stream,
        "model_stream" : model_stream,
    }


@register.assignment_tag()
def set_stream(stream_name, obj):
    if not stream_name in STREAMS:
        raise template.TemplateSyntaxError("%s is not a valid stream" % stream_name)
        
    stream = STREAMS[stream_name]
    return stream(obj)


#class SetStream(template.Node):
#    """
#    actor_stream, action_object_stream, target_stream, user_stream, model_stream
#    """
#    
#    def __init__(self, stream, obj, var_name):
#        self.stream = stream
#        self.obj = template.Variable(obj)
#        self.var_name = var_name
#    
#    def render(self, context):
#        obj = self.obj.resolve(context)
#        context[self.var_name] = self.stream(obj)
#        return ''
#    
#    @classmethod
#    def set_context(cls, parser, token):
#        try:
#            tag_name, arg = token.contents.split(None, 1)
#        except ValueError:
#            raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
#        
#        stream_name = tag_name.lstrip("set_")
#        if not stream_name in STREAMS:
#            raise template.TemplateSyntaxError("%s is not a valid stream" % stream_name)
#        stream = STREAMS[stream_name]
#        
#        m = re.search(r'(.*?) as (\w+)', arg)
#        if not m:
#            raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
#        obj, var_name = m.groups()
#        
#        return cls(stream, obj, var_name)
#
#
#for stream in STREAMS.keys():
#    stream_tag = 'set_' + stream
#    register.tag(stream_tag, SetStream.set_context)