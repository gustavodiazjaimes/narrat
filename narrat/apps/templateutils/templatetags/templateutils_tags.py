from django import template


register = template.Library()


@register.inclusion_tag("templateutils/time_item.html", takes_context=True)
def show_time(context, timestamp):
    return {"timestamp": timestamp, "request": context["request"]}