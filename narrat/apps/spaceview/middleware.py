from __future__ import absolute_import

from django.core.urlresolvers import resolve
from django.utils.importlib import import_module    

from .conf import settings


def load_space(path):
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing namespace %s: "%s"' % (path, e))
    except ValueError, e:
        raise ImproperlyConfigured('Error importing namespace. Is SPACEVIEW_NAMESPACES a correctly defined list or tuple?')
    try:
        cls = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" namespace' % (module, attr))
    
    try:
        namespace = getattr(cls, 'namespace')
        as_space = getattr(cls, 'as_space')
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define get_namespace_name or as_namespace' % (module, attr))

    return namespace, as_space()


def get_spaces_func():
    spaces_func = {}
    for view_path in settings.SPACEVIEW_SPACES:
        name, space_func = load_space(view_path)
        spaces_func[name] = space_func
    
    return spaces_func


class SpaceviewMiddleware(object):
    
    def process_view(self, request, func, *args, **kwargs):
        _args, _kwargs = args[0], args[1]
        
        _resolve = resolve(request.path_info)
        space = None
        spaces = None
        
        if _resolve.namespace:
            spaces_func = get_spaces_func()
            
            namespace = _resolve.namespace
            namespaces = _resolve.namespaces
            
            if namespace in spaces_func.keys():
                space_func = spaces_func[namespace]
                space = space_func(request, *_args, **_kwargs)
            
            spaces = {namespace:space} if space else {}
            print spaces
            for ns in namespaces[1:]:
                if ns in spaces_func.keys():
                    space_func = spaces_func[ns]
                    spaces[ns] = space_func(request, *_args, **_kwargs)
            
        request.resolve = _resolve
        request.space = space
        request.spaces = spaces
    
    def process_template_response(self, request, response):
        _resolve = request.resolve
        namespace = _resolve.namespace
        namespaces = _resolve.namespaces
        spaces = request.spaces
        
        context = {
            'current_app': namespace
        }
        
        if len(namespaces) > 1:
            for ns in namespaces.reverse():
                if ns in spaces.keys():
                    context.update(spaces[ns].context)
        elif namespace:
            if namespace in spaces.keys():
                context.update(spaces[namespace].context)
        
        response.context_data.update(context)
        
        return response
    
    
        #print "### request ###"
        #print request
        #
        #print "### request session ###"
        #session = request.__dict__['session']
        #for key in session.__dict__:
        #    print key, " : ", session.__dict__[key]
        #
        #print "### request attributes ###"
        #for key in request.__dict__:
        #    print key,
        #    print " : ",
        #    print request.__dict__[key]
        #
        #print "### func ###"
        #print func
        #
        #print "### args ###"
        #for arg in args:
        #    print arg
        #
        #print "### args ###"
        #for key in kwargs:
        #    print key,
        #    print " : ",
        #    print kwargs[val]
        #
        #print "### resolve ###"
        #print resolve(request.path_info)
        #
        #print "### resolve tuple ###"
        #a, b, c = resolve(request.path_info)
        #print a, b, c