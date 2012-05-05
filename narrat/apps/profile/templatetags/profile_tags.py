from django import template


register = template.Library()


@register.inclusion_tag("profiles/profile_item.html")
def show_profile(user):
    return {"user": user}
    

@register.filter
def is_me(user, page_user):
    if not user.is_authenticated():
        return False
    return user == page_user
    