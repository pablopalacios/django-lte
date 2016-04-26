from functools import update_wrapper

from django.apps import apps
from django.conf import settings
from django.conf.urls import include, url
from django.contrib.admin import AdminSite
from django.core.urlresolvers import NoReverseMatch, reverse
from django.template.response import TemplateResponse
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst

from . import views


class LTEAdminSite(AdminSite):
    site_title = _('DjangoLTE')
    site_header = _('Site Administration')
    index_title = _('Dashboard')

    def set_admin_view(self, view, cacheable=False):
        """
        Set admin views in the same way that wrap in AdminSite.get_urls does
        """
        def wrapper(*args, **kwargs):
            return self.admin_view(view, cacheable)(*args, **kwargs)
        return update_wrapper(wrapper, view)

    def get_accounts_urls(self):
        urlpatterns = [
            url(r'^login/$', views.LoginView.as_view(), name='login'),
            url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
            url(r'^profile/$', views.ProfileDetailView.as_view(), name='profile'),
            url(r'^profile/edit/$', views.ProfileUpdateView.as_view(), name='profile_update'),
            url(r'^password-change/$',
                views.PasswordChangeView.as_view(),
                name='password_change'
            ),
            url(r'^password-reset/$',
                views.PasswordResetView.as_view(),
                name='password_reset'
            ),
            url(r'^password-reset/done/$',
                views.PasswordResetDoneView.as_view(),
                name='password_reset_done'
            ),
            url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                views.PasswordResetConfirmAndLoginView.as_view(),
                name='password_reset_confirm'
            ),
        ]
        return urlpatterns

    def get_apps_urls(self):
        urlpatterns = []
        # Add in each model's views, and create a list of valid URLS for the
        # app_index
        valid_app_labels = []
        for model, model_admin in six.iteritems(self._registry):
            urlpatterns += [
                url(r'^%s/%s/' % (model._meta.app_label, model._meta.model_name), include(model_admin.urls)),
            ]
            if model._meta.app_label not in valid_app_labels:
                valid_app_labels.append(model._meta.app_label)

        # If there were ModelAdmins registered, we should have a list of app
        # labels for which we need to allow access to the app_index view,
        if valid_app_labels:
            regex = r'^(?P<app_label>' + '|'.join(valid_app_labels) + ')/$'
            urlpatterns += [
                url(regex, self.set_admin_view(self.app_index), name='app_list'),
            ]
        return urlpatterns

    def get_urls(self):
        from django.conf.urls import url, include
        from django.contrib.contenttypes import views as contenttype_views

        if settings.DEBUG:
            self.check_dependencies()

        # Admin-site-wide views.
        urlpatterns = [
            url(r'^$', self.set_admin_view(self.index), name='index'),
            url(r'^jsi18n/$', self.set_admin_view(self.i18n_javascript, cacheable=True), name='jsi18n'),
            url(r'^r/(?P<content_type_id>\d+)/(?P<object_id>.+)/$',
                self.set_admin_view(contenttype_views.shortcut),
                name='view_on_site'
            ),
        ]
        # Accounts  views
        urlpatterns += self.get_accounts_urls()
        # Apps views
        urlpatterns += self.get_apps_urls()

        return urlpatterns

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
