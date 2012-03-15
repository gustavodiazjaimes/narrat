import re
from django.core.urlresolvers import resolve

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from django.conf import settings

try:
    import actstream
except ImportError:
    actstream = None


def profile(request):
    try:
        view, args, kwargs = resolve(request.path)
        username = kwargs.get("username", None)
    except:
        return {}
    
    if username:
        try:
            page_user = User.objects.get(username=username, is_active=True)
        except User.DoesNotExist:
            page_user = None
        
        if actstream:
            ctype = ContentType.objects.get_for_model(User)
            actions = actstream.models.actor_stream(page_user)
            if request.user.is_authenticated():
                is_following = actstream.models.Follow.objects.is_following(request.user, page_user)
            else:
                is_following = None
        else:
            ctype = None
            actions = None
            is_following = None
        
        if page_user:
            return {
                "page_user": page_user,
                "is_me": request.user == page_user,
                "page_user_ctype": ctype,
                "page_user_actions": actions,
                "is_following": is_following,
            }
    return {}