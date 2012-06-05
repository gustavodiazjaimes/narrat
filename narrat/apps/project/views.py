from __future__ import absolute_import
from functools import wraps

from django.core.exceptions import ValidationError
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils import simplejson as json
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.forms.models import modelformset_factory
from django.forms.forms import NON_FIELD_ERRORS

from permissions.models import Role
from permissions.utils import get_role

from narrat_utils.views.formset import UpdateSetView
from narrat_utils.views.permissions import PermissionMixin
from spaceview.views import SpaceView

from .conf import settings
from .models import Project, Member
from .signals import (project_postcreate, project_postupdate, project_predelete,
                      member_postupdate, members_postupdate,)
from .forms import ProjectForm, MemberForm


class ProjectSpace(SpaceView):
    
    app_namespace = 'project'
    model = Project
    context_object_name = 'project'
    slug_url_kwarg = 'project_slug'
    template_name = 'project/project_base.html'
    
    def get_context_data(self, **kwargs):
        context = super(ProjectSpace, self).get_context_data(**kwargs)
        
        user = self.request.user
        project = self.object
        context['member'] = project.get_member(user) if user.is_authenticated() else None
        
        return context


class ProjectDetailView(ProjectSpace):
    
    template_name = 'project/project_detail.html'


class ProjectCreateView(CreateView):
    
    model = Project
    template_name = 'project/project_create.html'
    form_class = ProjectForm
    
    def form_valid(self, form):
        user = self.request.user
        
        project = form.save(commit=False)
        project.save()
        form.save_m2m()
        
        member = Member(user=user, role=get_role('leader'), project=project)
        member.save()
        
        self.object = project
        
        project_postcreate.send(sender=self, user=user, project=project)

        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        context = super(ProjectCreateView, self).get_context_data(**kwargs)

        context['project_form'] = context['form']
        return context
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProjectCreateView, self).dispatch(*args, **kwargs)


class ProjectUpdateView(PermissionMixin, UpdateView):
    
    namespace = 'project'
    model = Project
    context_object_name = 'project'
    slug_url_kwarg = 'project_slug'
    form_class = ProjectForm
    template_name = 'project/project_update.html'
    permission = 'project_update'
    
    def form_valid(self, form):
        _return = super(ProjectUpdateView, self).form_valid(form)
        
        user = self.request.user
        project = self.object
        project_postupdate.send(sender=self, user=user, project=project)
        
        return _return
    
    def get_context_data(self, **kwargs):
        context = super(ProjectUpdateView, self).get_context_data(**kwargs)
        context['project_form'] = context['form']
        
        return context
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectUpdateView, self).dispatch(request, *args, **kwargs)

class ProjectDeleteView(PermissionMixin, DeleteView):
    
    model = Project
    context_object_name = 'project'
    slug_url_kwarg = 'project_slug'
    template_name = 'project/project_delete.html'
    permission = 'project_delete'
    
    def delete(self, request, *args, **kwargs):
        user = self.request.user
        project = self.object
        
        project_predelete.send(sender=self, user=user, project=project)
        
        project.members.all().delete()
        project.delete()
        
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        user = self.request.user
        return user.get_absolute_url();
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectDeleteView, self).dispatch(request, *args, **kwargs)


class MemberUpdateSetView(PermissionMixin, UpdateSetView):
    
    model = Member
    context_object_name = 'members'
    initial = [{'role':get_role(settings.PROJECT_DEFAULT_ROLE).pk}]
    form_class = MemberForm
    template_name = 'project/member_updateset.html'
    permission = 'members_update'
    app_name = 'project'
    
    def get_queryset(self):
        return self.project.members.all()
   
    def formset_valid(self, formset):
        for (i, form) in enumerate(formset):
            if not form.cleaned_data:
                continue
            member = form.save(commit=False)
            member.project = self.project
            try:
                member.validate_unique()
            except ValidationError, e:
                formset[i]._errors[NON_FIELD_ERRORS] = formset.error_class(e.messages)
            
        for error in formset.errors:
            if error:
                return self.formset_invalid(formset)
        
        formset.save()
        
        user = self.request.user
        project = self.project
        members_postupdate.send(sender=self, user=user, project=project)
        
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        project = self.project
        return project.get_absolute_url();
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        spaces = request.spaces
        project = spaces[self.app_name].object
        self.project = project
        return super(MemberUpdateSetView, self).dispatch(request, *args, **kwargs)
