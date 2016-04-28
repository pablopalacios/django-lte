from django.apps import apps
from django.core.urlresolvers import NoReverseMatch, reverse, reverse_lazy
from django.utils import six
from django.utils.decorators import method_decorator
from django.utils.text import capfirst
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from braces import views as braces_views


class BaseAdminMixin(object):
    site_title = 'DjangoLTE'
    site_header = 'Site Administration'
    site_url = '/'
    name = 'lte'
    title = 'Dashboard'

    def get_site_title(self):
        return self.site_title

    def get_site_header(self):
        return self.site_header

    def get_site_url(self):
        return self.site_header

    def get_title(self):
        return self.title

    def get_context_data(self, **kw):
        context = super().get_context_data(**kw)
        context['site_title'] = self.get_site_title()
        context['site_header'] = self.get_site_header()
        context['site_url'] = self.get_site_url()
        context['title'] = self.get_title()
        return context


class CSRFProtectedMixin(object):

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kw):
        return super().dispatch(*args, **kw)


class NoCacheAdminViewMixin(CSRFProtectedMixin):

    @method_decorator(never_cache)
    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kw):
        return super().dispatch(*args, **kw)


class HasPermissionMixin(braces_views.UserPassesTestMixin):
    """ CBV that implements AdminSite.has_permission """

    login_url = reverse_lazy('admin:login')

    def test_func(self, user):
        return user.is_active and user.is_staff


class PrivateAdminViewMixin(HasPermissionMixin, BaseAdminMixin):
    registry = None

    def get_context_data(self, **kw):
        context = super().get_context_data(**kw)
        context['title'] = self.get_title()
        context['menu'] = self.get_menu()
        return context

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


class PublicAdminViewMixin(BaseAdminMixin):
    pass
