from django import template


register = template.Library()


@register.inclusion_tag("narrat_utils/_timesince.html", takes_context=True)
def show_timesince(context, timefrom, timeto=None, adverb="ago"):
    return {"request": context["request"],
            "timefrom": timefrom,
            "timeto":timeto,
            "adverb":adverb }
