from django.apps import apps
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import NoReverseMatch, reverse
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from . import base


class IndexView(base.PrivateAdminViewMixin, base.NoCacheAdminViewMixin, generic.TemplateView):
    template_name = 'lte/index.html'
    title = _('Dashboard')


class AppIndexView(base.PrivateAdminViewMixin, base.NoCacheAdminViewMixin,  generic.TemplateView):
    template_name = 'lte/app_index.html'

    @property
    def app_label(self):
        return self.kwargs['app_label']

    @property
    def app_name(self):
        return apps.get_app_config(self.app_label).verbose_name

    def get_title(self):
        return _('{app} administration'.format(app=self.app_name))

    def get_context_data(self, **kw):
        context = super().get_context_data(**kw)
        context['app_name'] = self.app_name
        context['app_model_list'] = self.get_models()
        return context

    def check_module_permissions(self, model_admin):
        """Check permissions per module. Returns perms if there is some
        permission, otherwise raises PermissionDenied"""
        perms = model_admin.has_module_permission(self.request)
        if perms:
            return perms
        raise PermissionDenied

    def get_models(self):
        """ Returns a list models in which request user has access """
        models = []
        for model, model_admin in self.registry.items():
            if self.app_label == model._meta.app_label:
                self.check_module_permissions(model_admin)
                perms = model_admin.get_model_perms(self.request)
                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True in perms.values():
                    info = (self.app_label, model._meta.model_name)
                    model_dict = {
                        'name': capfirst(model._meta.verbose_name_plural),
                    }
                    if perms.get('change'):
                        try:
                            model_dict['admin_url'] = reverse(
                                'admin:%s_%s_changelist' % info,
                                current_app=self.name,
                            )
                        except NoReverseMatch:
                            pass
                    if perms.get('add'):
                        try:
                            model_dict['add_url'] = reverse(
                                'admin:%s_%s_add' % info,
                                current_app=self.name,
                            )
                        except NoReverseMatch:
                            pass
                    models.append(model_dict)
        # Sort the models alphabetically within each app.
        models.sort(key=lambda x: x['name'])
        return models
