import re

from django.core.urlresolvers import resolve
from django.contrib.auth.models import User


def profile(request):
    try:
        view, args, kwargs = resolve(request.path)
    except:
        return {}   # request captured in middleware can't be resolve (__debug__)
    
    failreturn = {
        "page_user": None,
        "is_me": None
    }
    
    username = kwargs.get("username", None)
    if not username:
        return {}
    else:
        try:
            page_user = User.objects.get(username=username, is_active=True)
        except User.DoesNotExist:
            return failreturn
    
    return {
        "page_user": page_user,
        "is_me": request.user == page_user,
    }