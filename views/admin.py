from django.apps import apps
from django.core.urlresolvers import NoReverseMatch, reverse
from django.utils import six
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from django.views import generic


class BaseAdminView(object):

    registry = None
    name = 'lte'
    title = ''

    def get_menu(self):
        """
        Generates the admin menu based on app/model list.
        It is basically the AdminSite.index method.
        """
        app_dict = {}
        for model, model_admin in self.registry.items():
            app_label = model._meta.app_label
            has_module_perms = model_admin.has_module_permission(self.request)
            if has_module_perms:
                perms = model_admin.get_model_perms(self.request)
                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True in perms.values():
                    info = (app_label, model._meta.model_name)
                    model_dict = {
                        'name': capfirst(model._meta.verbose_name_plural),
                        'object_name': model._meta.object_name,
                        'perms': perms,
                    }
                    if perms.get('change', False):
                        try:
                            model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=self.name)
                        except NoReverseMatch:
                            pass
                    if app_label in app_dict:
                        app_dict[app_label]['models'].append(model_dict)
                    else:
                        app_dict[app_label] = {
                            'name': apps.get_app_config(app_label).verbose_name,
                            'app_label': app_label,
                            'app_url': reverse(
                                'admin:app_list',
                                kwargs={'app_label': app_label},
                                current_app=self.name,
                            ),
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
                        }

        # Sort the apps alphabetically.
        app_list = list(six.itervalues(app_dict))
        app_list.sort(key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        return app_list

    def get_title(self):
        return self.title

    def get_context_data(self, **kw):
        context = super().get_context_data(**kw)
        context['menu'] = self.get_menu()
        context['title'] = self.get_title()
        return context


class IndexView(BaseAdminView, generic.TemplateView):
    template_name = 'lte/index.html'
    title = _('Dashboard')


class AppIndexView(BaseAdminView, generic.TemplateView):
    template_name = 'lte/app_index.html'
    title = _('App name not implemented')

    @property
    def app_label(self):
        return self.kwargs['app_label']

    @property
    def app_name(self):
        return apps.get_app_config(self.app_label).verbose_name

    def get_title(self):
        return _('%(app)s administration') % {'app': self.app_name}

    def get_context_data(self, **kw):
        context = super().get_context_data(**kw)
        context['app_label'] = self.app_label
        context['app_list'] = self.get_models()
        return context

    def get_models(self):
        """
        App index view. It is a copy of AdminSite.app_index.
        """
        app_dict = {}
        for model, model_admin in self.registry.items():
            if self.app_label == model._meta.app_label:
                has_module_perms = model_admin.has_module_permission(self.request)
                if not has_module_perms:
                    raise PermissionDenied

                perms = model_admin.get_model_perms(self.request)

                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True in perms.values():
                    info = (self.app_label, model._meta.model_name)
                    model_dict = {
                        'name': capfirst(model._meta.verbose_name_plural),
                        'object_name': model._meta.object_name,
                        'perms': perms,
                    }
                    if perms.get('change'):
                        try:
                            model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=self.name)
                        except NoReverseMatch:
                            pass
                    if perms.get('add'):
                        try:
                            model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=self.name)
                        except NoReverseMatch:
                            pass
                    if app_dict:
                        app_dict['models'].append(model_dict),
                    else:
                        # First time around, now that we know there's
                        # something to display, add in the necessary meta
                        # information.
                        app_dict = {
                            'name': self.app_name,
                            'app_label': self.app_label,
                            'app_url': '',
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
                        }

        # Sort the models alphabetically within each app.
        app_dict['models'].sort(key=lambda x: x['name'])

        return [app_dict]
