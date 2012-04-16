from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson as json
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.forms.models import modelformset_factory
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from narrat.apps.projects.models import Project, ProjectMember
from narrat.apps.projects.forms import ProjectForm, ProjectUpdateForm, ProjectMemberForm, AddUserForm


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


class ProjectObjectMixin(object):
    model = Project
    context_object_name = "project"
    slug_url_kwarg = project_slug = 'project_slug'
    
    project = None
    membership_required = []
    
    def get_project(self):
        
        if self.project:
            return self.project
        
        if self.model == Project:
            if hasattr(self, 'object'):
                self.project = self.object
                return self.project
        
        slug = self.kwargs.get(self.project_slug, None)
        if not slug:
            return None
        
        queryset = Project._default_manager
        try:
            project = queryset.filter(**{"slug": slug}).get()
        except ObjectDoesNotExist:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        
        self.project = project
        
        return self.project
    
    def get_initial(self):
        initial = {}
        
        project = self.get_project()
        if project:
            initial['project'] = project.pk
        
        initial.update(
            super(ProjectObjectMixin, self).get_initial()
            )
        
        return initial
    
    def get_context_data(self, **kwargs):
        ctx = {}
        
        group, bridge = group_and_bridge(kwargs)
        ctx.update(
            group_context(group, bridge)
            )
        
        ctx['project'] = self.get_project
        
        ctx.update(
            super(ProjectObjectMixin, self).get_context_data(**kwargs)
            )
        
        return ctx
    
    def get_projectmember(self):
        project = self.get_project()
        user = self.request.user
        
        if not project:
            return None
        
        projectmember = project.members.active(user=user)
        if not projectmember.exists():
            projetmember = None
        
        return projectmember
    
    def is_membership_required(self):
        if not self.membership_required:
            return True
        
        projectmember = self.get_projectmember()
        if projectmember:
            for role in self.membership_required:
                if projectmember.is_membership(role):
                    return True
        
        return False
    
    #@staticmethod
    #def do_membership_required(function=None):
    #    
    #    @wraps(function)
    #    def decorator(self, request, *args, **kwargs):
    #        self.request = request
    #        self.args = args
    #        self.kwargs = kwargs
    #        
    #        if not self.is_membership_required():
    #            return HttpResponseNotAllowed('GET')
    #        
    #        return function(self, request, *args, **kwargs)
    #        
    #    return decorator
    
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        
        if not self.is_membership_required():
            return HttpResponseNotAllowed('GET')
        
        return super(ProjectObjectMixin, self).dispatch(request, *args, **kwargs)


class ProjectDetailView(ProjectObjectMixin, DetailView):
    
    template_name = "projects/project.html"


class ProjectCreateView(ProjectObjectMixin, CreateView):
    
    template_name = "projects/create.html"
    form_class = ProjectForm
    
    def form_valid(self, form):
        project = form.save(commit=False)
        project.creator = self.request.user
        project.save()
        form.save_m2m()
        
        project_member = ProjectMember(project=project, user=self.request.user,
                                       membership=ProjectMember.MEMBERSHIP['Leader'])
        #project.members.add(project_member)
        project_member.save()
        
        self.object = project

        if notification:
            notification.send(User.objects.all(), "projects_new_project",
                {"project": project}, queue=True)

        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        ctx = super(ProjectCreateView, self).get_context_data(**kwargs)
        ctx["project_form"] = ctx["form"]
        
        return ctx
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProjectCreateView, self).dispatch(*args, **kwargs)


class ProjectUpdateView(ProjectObjectMixin, UpdateView):
    
    template_name = "projects/update.html"
    form_class = ProjectUpdateForm
    membership_required = ['Leader']
    
    def get_context_data(self, **kwargs):
        ctx = super(ProjectUpdateView, self).get_context_data(**kwargs)
        
        ctx["project_form"] = ctx["form"]
        
        return ctx
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectUpdateView, self).dispatch(request, *args, **kwargs)


class ProjectMemberCreateView(ProjectObjectMixin, CreateView):
    
    template_name = "projects/projectmember.html"
    model = ProjectMember
    context_object_name = "projectmember"
    form_class = ProjectMemberForm
    membership_required = ['Leader']
    
    def form_valid(self, form):
        if form.cleaned_data['project'] != self.get_project():
            raise Http404(_(u"value %(project)s for project field is no correct") %
                          {'project': form.cleaned_data['project']})
        
        form.save()
        
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):
        project = self.get_project()
        
        return project.get_absolute_url();
    
    def get_context_data(self, **kwargs):
        ctx = super(ProjectMemberCreateView, self).get_context_data(**kwargs)
        
        ctx["projectmember"] = self.get_projectmember()
        ctx["projectmember_form"] = ctx.get("form", None)
        
        return ctx
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectMemberCreateView, self).dispatch(request, *args, **kwargs)


class ProjectMemberUpdateView(ProjectObjectMixin, UpdateView):
    
    template_name = "projects/projectmember.html"
    context_object_name = "projectmember_set"
    model = ProjectMember
    form_class = ProjectMemberForm
    
    membership_required = ['Leader']
    
    def get_object(self):
        project = self.get_project()
        return project.members.all()
    
    def get_initial(self):
        initial = super(ProjectMemberUpdateView, self).get_initial()
        
        return [initial]
    
    def get_form_class(self):
        formset = modelformset_factory(self.model, form = self.form_class)
        
        return formset
    
    def get_form_kwargs(self):
        kwargs = super(ProjectMemberUpdateView, self).get_form_kwargs()
        
        kwargs.pop('instance')
        kwargs['queryset'] = self.get_object()
        
        return kwargs
    
    def get_context_data(self, **kwargs):
        ctx = super(ProjectMemberUpdateView, self).get_context_data(**kwargs)
        
        ctx["projectmember"] = self.get_projectmember()
        ctx["projectmember_form"] = ctx["form"]
        
        return ctx
    
    def get_success_url(self):
        project = self.get_project()
        
        return project.get_absolute_url();
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectMemberUpdateView, self).dispatch(request, *args, **kwargs)
