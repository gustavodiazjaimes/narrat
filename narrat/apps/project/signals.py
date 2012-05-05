import django.dispatch


project_postcreate = django.dispatch.Signal(providing_args=["user", "project"])
project_postupdate = django.dispatch.Signal(providing_args=["user", "project"])
project_predelete = django.dispatch.Signal(providing_args=["user", "project"])

member_postupdate = django.dispatch.Signal(providing_args=["user", "project"])
members_postupdate = django.dispatch.Signal(providing_args=["user", "project"])
