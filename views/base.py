from django.apps import apps
from django.core.urlresolvers import NoReverseMatch, reverse
from django.utils import six
from django.utils.text import capfirst

from braces import views as braces_views


class AdminPermissionViewMixin(braces_views.UserPassesTestMixin):
    """ CBV that implements AdminSite.has_permission """

    def has_permission(self, user):
        return user.is_active and user.is_staff

    def test_func(self, user):
        return self.has_permission(user)


class BaseAdminView(object):

    registry = None
    name = 'lte'
    title = ''

    def get_menu(self):
        """ Generates the admin menu based on app list. """
        app_dict = {}
        for model, model_admin in self.registry.items():
            app_label = model._meta.app_label
            has_module_perms = model_admin.has_module_permission(self.request)
            if has_module_perms:
                perms = model_admin.get_model_perms(self.request)
                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True in perms.values():
                    if app_label not in app_dict:
                        app_dict[app_label] = {
                            'name': apps.get_app_config(app_label).verbose_name,
                            'label': app_label,
                            'url': reverse(
                                'admin:app_list',
                                kwargs={'app_label': app_label},
                                current_app=self.name,
                            ),
                        }

        # Sort the apps alphabetically.
        app_list = list(six.itervalues(app_dict))
        app_list.sort(key=lambda x: x['name'].lower())
        return app_list

    def get_title(self):
        return self.title

    def get_context_data(self, **kw):
        context = super().get_context_data(**kw)
        context['menu'] = self.get_menu()
        context['title'] = self.get_title()
        return context
