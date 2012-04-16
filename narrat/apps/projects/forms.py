from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Hidden, Fieldset
from ajax_select import make_ajax_field

from narrat.apps.projects.models import Project, ProjectMember



# @@@ we should have auto slugs, even if suggested and overrideable



class ProjectForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        
        self.fields['slug'].help_text = _("a short version of the name consisting only of letters, numbers, underscores and hyphens.")
        self.fields['keywords'].required = False
    
    def clean_slug(self):
        if Project.objects.filter(slug__iexact=self.cleaned_data["slug"]).exists():
            raise forms.ValidationError(_("A project already exists with that slug."))
        return self.cleaned_data["slug"].lower()
    
    def clean_name(self):
        if Project.objects.filter(name__iexact=self.cleaned_data["name"]).exists():
            raise forms.ValidationError(_("A project already exists with that name."))
        return self.cleaned_data["name"]
    
    class Meta:
        model = Project
        fields = ["name", "slug", "keywords", "description"]


# @@@ is this the right approach, to have two forms where creation and update fields differ?


class ProjectUpdateForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(ProjectUpdateForm, self).__init__(*args, **kwargs)
        
        self.fields['keywords'].required = False
    
    def clean_name(self):
        if Project.objects.filter(name__iexact=self.cleaned_data["name"]).exists():
            if self.cleaned_data["name"] == self.instance.name:
                pass # same instance
            else:
                raise forms.ValidationError(_("A project already exists with that name."))
        return self.cleaned_data["name"]
    
    class Meta:
        model = Project
        fields = ['name', 'keywords', 'description']


class ProjectMemberForm(forms.ModelForm):
    
    #user = make_ajax_field(ProjectMember,'user','user',help_text=None)
    
    def __init__(self, *args, **kwargs):
        super(ProjectMemberForm, self).__init__(*args, **kwargs)
        
        self.fields['roles'].required = False
        self.fields['project'].widget = forms.HiddenInput()
        
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            self.fields['project'].widget.attrs['readonly'] = True
            self.fields['user'].widget.attrs['readonly'] = True
    
    def clean_project(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            return self.instance.project
        
        return self.cleaned_data['project']
        
    def clean_user(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            return self.instance.user
        
        return self.cleaned_data['user']
    
    class Meta:
        model = ProjectMember
        fields = ['project', 'user', 'membership', 'roles']


class AddUserForm(forms.Form):
    
    recipient = forms.CharField(label=_(u"User"))
    
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project")
        super(AddUserForm, self).__init__(*args, **kwargs)
        self._user_cache = None
    
    def clean_recipient(self):
        try:
            user = User.objects.get(username__exact=self.cleaned_data["recipient"])
        except User.DoesNotExist:
            raise forms.ValidationError(_("There is no user with this username."))
        
        if ProjectMember.objects.filter(project=self.project, user=user).exists():
            raise forms.ValidationError(_("User is already a member of this project."))
        
        # store user instance we queried for here to prevent additional
        # lookups.
        self._user_cache = user
        
        return self.cleaned_data["recipient"]
    
    def save(self, user):
        new_member = self._user_cache
        project_member = ProjectMember(project=self.project, user=new_member)
        project_member.save()
        self.project.members.add(project_member)
        if notification:
            notification.send(self.project.member_users.all(), "projects_new_member", {
                "new_member": new_member,
                "project": self.project
            })
            notification.send([new_member], "projects_added_as_member", {
                "adder": user,
                "project": self.project
            })
        return project_member
