from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson as json
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.views.generic import ListView, DetailView, CreateView, UpdateView

from narrat.apps.projects.models import Project, ProjectMember
from narrat.apps.projects.forms import ProjectForm, ProjectUpdateForm, AddUserForm


if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None


def group_and_bridge(kwargs):
    """
    Given kwargs from the view (with view specific keys popped) pull out the
    bridge and fetch group from database.
    """
    
    bridge = kwargs.pop("bridge", None)
    
    if bridge:
        try:
            group = bridge.get_group(**kwargs)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None
    
    return group, bridge


def group_context(group, bridge):
    # @@@ use bridge
    return {
        "group": group,
    }


class ProjectDetailView(DetailView):
    template_name = "projects/project.html"
    model = Project
    context_object_name = "project"
    
    def get_context_data(self, **kwargs):

        group, bridge = group_and_bridge(kwargs)
        
        ctx = group_context(group, bridge)
        ctx.update(
            super(ProjectDetailView, self).get_context_data(**kwargs)
        )
        
        return ctx


class ProjectCreateView(CreateView):
    
    template_name = "projects/create.html"
    context_object_name = "project"
    form_class = ProjectForm
    
    def form_valid(self, form):
        project = form.save(commit=False)
        project.creator = self.request.user
        project.save()
        project_form.save_m2m()
        project_member = ProjectMember(project=project, user=self.request.user,
                                       membership=ProjectMember.MEMBERSHIP['Leader'])
        project.members.add(project_member)
        project_member.save()
        
        self.object = project

        if notification:
            notification.send(User.objects.all(), "projects_new_project",
                {"project": project}, queue=True)

        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_context_data(self, **kwargs):
        group, bridge = group_and_bridge(self.kwargs)
        
        ctx = group_context(group, bridge)
        ctx.update(
            super(ProjectCreateView, self).get_context_data(**kwargs)
        )
        ctx["project_form"] = ctx["form"]
        return ctx
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProjectCreateView, self).dispatch(*args, **kwargs)


class ProjectUpdateView(UpdateView):
    model = Project
    template_name = "projects/update.html"
    context_object_name = "project"
    form_class = ProjectUpdateForm
    
    def get_context_data(self, **kwargs):
        group, bridge = group_and_bridge(self.kwargs)
        
        ctx = group_context(group, bridge)
        ctx.update(
            super(ProjectUpdateView, self).get_context_data(**kwargs)
        )
        ctx["project_form"] = ctx["form"]
        return ctx
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.request = args[0]
        self.args = args[1:]
        self.kwargs = kwargs
        
        project = self.get_object()
        user = self.request.user
        
        try:
            projectmember = ProjectMember.objects.activemember().get(user=user, project=project)
        except ProjectMember.DoesNotExist:
            projectmember = None
        
        if not projectmember:
            return HttpResponseNotAllowed('GET')
        
        return super(ProjectUpdateView, self).dispatch(*args, **kwargs)
