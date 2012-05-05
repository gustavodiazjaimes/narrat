from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.list import MultipleObjectMixin, MultipleObjectTemplateResponseMixin

from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory


class FormsetMixin(object):
    """
    A mixin that provides a way to show and handle a formset in a request.
    """

    initial = [{}]
    form_class = None
    can_delete = False
    success_url = None

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        return self.initial

    def get_formset_class(self):
        """
        Returns the form class to use in this view
        """
        return formset_factory(self.form_class, can_delete=self.can_delete)

    def get_formset(self, formset_class):
        """
        Returns an instance of the form to be used in this view.
        """
        return formset_class(**self.get_formset_kwargs())

    def get_formset_kwargs(self):
        """
        Returns the keyword arguments for instanciating the form.
        """
        kwargs = {'initial': self.get_initial()}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_context_data(self, **kwargs):
        return kwargs

    def get_success_url(self):
        if self.success_url:
            url = self.success_url
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")
        return url

    def formset_valid(self, formset):
        return HttpResponseRedirect(self.get_success_url())

    def formset_invalid(self, formset):
        return self.render_to_response(self.get_context_data(formset=formset))


class ModelFormsetMixin(FormsetMixin, MultipleObjectMixin):
    """
    A mixin that provides a way to show and handle a modelform in a request.
    """

    def get_formset_class(self):
        """
        Returns the form class to use in this view
        """
        if self.model is not None:
            # If a model has been explicitly provided, use it
            model = self.model
        else:
            # Try to get a queryset and extract the model class
            # from that
            model = self.get_queryset().model
        
        if self.form_class:
            return modelformset_factory(model, form=self.form_class, can_delete=self.can_delete)
        else:
            return modelformset_factory(model, can_delete=self.can_delete)

    def get_formset_kwargs(self):
        """
        Returns the keyword arguments for instanciating the form.
        """
        kwargs = super(ModelFormsetMixin, self).get_formset_kwargs()
        kwargs.update({'queryset': self.get_queryset()})
        return kwargs
    
    def get_success_url(self):
        if self.success_url:
            url = self.success_url % self.queryset.__dict__
        else:
            try:
                url = self.queryset.model.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the Model.")
        return url

    def formset_valid(self, formset):
        self.object_list = formset.save()
        return super(ModelFormMixin, self).formset_valid(form)

    def get_context_data(self, **kwargs):
        context = kwargs
        if self.object_list:
            context['object_list'] = self.object_list
            context_object_name = self.get_context_object_name(self.object_list)
            if context_object_name:
                context[context_object_name] = self.object_list
        return context


class ProcessFormsetView(View):
    """
    A mixin that processes a form on POST.
    """
    def get(self, request, *args, **kwargs):
        formset_class = self.get_formset_class()
        formset = self.get_formset(formset_class)
        return self.render_to_response(self.get_context_data(formset=formset))

    def post(self, request, *args, **kwargs):
        formset_class = self.get_formset_class()
        formset = self.get_formset(formset_class)
        if formset.is_valid():
            return self.formset_valid(formset)
        else:
            return self.formset_invalid(formset)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class BaseFormsetView(FormsetMixin, ProcessFormsetView):
    """
    A base view for displaying a form
    """


class FormsetView(TemplateResponseMixin, BaseFormsetView):
    """
    A view for displaying a form, and rendering a template response.
    """


class BaseUpdateSetView(ModelFormsetMixin, ProcessFormsetView):
    """
    Base view for updating an existing object.

    Using this base class requires subclassing to provide a response mixin.
    """
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super(BaseUpdateSetView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super(BaseUpdateSetView, self).post(request, *args, **kwargs)


class UpdateSetView(MultipleObjectTemplateResponseMixin, BaseUpdateSetView):
    """
    View for updating an object,
    with a response rendered by template..
    """
    template_name_suffix = '_formset'