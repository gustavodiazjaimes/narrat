from __future__ import absolute_import

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Hidden, Fieldset
from ajax_select import make_ajax_field
from permissions.utils import get_role

from .models import Project, Member
from .conf import settings

roles = [get_role(role) for role in settings.PROJECT_ROLES]
ROLES_CHOICES = [(role.pk, _(unicode(role))) for role in roles]


# @@@ we should have auto slugs, even if suggested and overrideable


class ProjectForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        
        is_new = self.instance.pk is None
        
        if is_new:
            slug_help_text = _(u"a short version of the name consisting only of letters, numbers, underscores and hyphens.")
        else:
            slug_help_text = _(u"warning: changing slug will cause urls changes, hyperlinks could be lose.")
        
        self.fields['slug'].help_text = slug_help_text
        self.fields['keywords'].required = False
    
    class Meta:
        model = Project
        fields = ['name', 'slug', 'keywords', 'description']


class MemberForm(forms.ModelForm):
    
    #user = make_ajax_field(Member,'user','user',help_text=None)
    
    def __init__(self, *args, **kwargs):
        super(MemberForm, self).__init__(*args, **kwargs)
        
        self.fields['user'].required = True
        self.fields['role'].choices = ROLES_CHOICES
        self.fields['badges'].required = False
        
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['user'].widget.attrs['readonly'] = True
        
    def clean_user(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return self.instance.user
        
        return self.cleaned_data['user']
    
    class Meta:
        model = Member
        fields = ['user', 'role', 'badges']
