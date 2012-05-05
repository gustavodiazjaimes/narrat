from functools import update_wrapper

from django.core.exceptions import ImproperlyConfigured
from django.views.generic.detail import DetailView


class SpaceMixin(DetailView):
    """
    Namespace object like class based view
    """
    namespace_name = None
    
#   model = None
#   queryset = None
#   slug_field = 'slug'
#   context_object_name = None
#   slug_url_kwarg = 'slug'
#   pk_url_kwarg = 'pk'
#
#   template_name = None
#   template_name_field = None
    template_name_suffix = '_base'
    
    @property
    @classmethod
    def namespace(cls):
        if cls.namespace_name:
            return cls.namespace_name
        elif cls.model:
            return smart_str(cls.model.__class__.__name__.lower())
        
        raise ImproperlyConfigured(u"NamespaceMixin %s must define namespace_name or model"
                                   % self.__class__.__name__)
    
    @classmethod
    def as_space(cls, **initkwargs):
        """
        Namespace object definition
        (compatible vith class base view mixin).
        """
        # sanitize keyword arguments
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError(u"You tried to pass in the %s method name as a "
                                u"keyword argument to %s(). Don't do that."
                                % (key, cls.__name__))
            if not hasattr(cls, key):
                raise TypeError(u"%s() received an invalid keyword %r" % (
                    cls.__name__, key))
        
        def space(request, *args, **kwargs):
            self = cls(**initkwargs)
            
            self.request = request
            self.args = args
            self.kwargs = kwargs
            
            self.object = self.get_object()
            self.context = self.get_context_data()
            
            return self
        
        # take name and docstring from class
        update_wrapper(space, cls, updated=())

        return space
