from django.apps import apps
from django.contrib.admin import AdminSite
from django.core.urlresolvers import NoReverseMatch, reverse
from django.template.response import TemplateResponse
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst

from lte_accounts.forms import AuthForm


class LTEAdminSite(AdminSite):
    site_title = _('AdminLTE')
    site_header = _('Site Administration')
    index_title = _('Dashboard')

    login_form = AuthForm
    login_template = 'accounts/lte/login.html'

    def get_menu(self, request):
        """
        Generates the admin menu based on app/model list.
        It is basically the AdminSite.index method.
        """
        app_dict = {}
        for model, model_admin in self._registry.items():
            app_label = model._meta.app_label
            has_module_perms = model_admin.has_module_permission(request)
            if has_module_perms:
                perms = model_admin.get_model_perms(request)
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

    def index(self, request, extra_context=None):
        menu = self.get_menu(request)
        context = dict(
            self.each_context(request),
            title=self.index_title,
            menu=menu,
        )
        context.update(extra_context or {})
        request.current_app = self.name
        return TemplateResponse(request, self.index_template or
                                'lte/index.html', context)

    def app_index(self, request, app_label, extra_context=None):
        """
        App index view. It is a copy of AdminSite.app_index.
        """
        menu = self.get_menu(request)

        app_name = apps.get_app_config(app_label).verbose_name
        app_dict = {}
        for model, model_admin in self._registry.items():
            if app_label == model._meta.app_label:
                has_module_perms = model_admin.has_module_permission(request)
                if not has_module_perms:
                    raise PermissionDenied

                perms = model_admin.get_model_perms(request)

                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True in perms.values():
                    info = (app_label, model._meta.model_name)
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
                            'name': app_name,
                            'app_label': app_label,
                            'app_url': '',
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
                        }
        if not app_dict:
            raise Http404('The requested admin page does not exist.')
        # Sort the models alphabetically within each app.
        app_dict['models'].sort(key=lambda x: x['name'])
        context = dict(
            self.each_context(request),
            title=_('%(app)s administration') % {'app': app_name},
            app_list=[app_dict],
            app_label=app_label,
            menu=menu,
        )
        context.update(extra_context or {})

        request.current_app = self.name

        return TemplateResponse(request, self.app_index_template or [
            'lte/%s/app_index.html' % app_label,
            'lte/app_index.html'
        ], context)


site = LTEAdminSite(name='lte')
