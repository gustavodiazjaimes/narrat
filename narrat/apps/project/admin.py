from django.contrib import admin
from narrat.apps.project.models import Project



class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "started"]



admin.site.register(Project, ProjectAdmin)