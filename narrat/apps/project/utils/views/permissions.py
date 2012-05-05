

class PermissionMixin(object):
    """
    Permission mixin for class based views
    """
    permission = None
    
    def has_permission(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        
        perm = self.permission
        if not perm:
            return True
        
        user = request.user
        if user.is_authenticated():
            space = request.space
            _object = space.object if space else self.get_object()
            
            return _object.has_permission(user, perm)
        
        return False
    
    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission(request, *args, **kwargs):
            return HttpResponseForbidden()
        
        return super(PermissionMixin, self).dispatch(request, *args, **kwargs)
