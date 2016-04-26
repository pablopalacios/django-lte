from functools import update_wrapper

from django.conf import settings
from django.conf.urls import include, url
from django.contrib.admin import AdminSite, ModelAdmin
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect

from . import views


__all__ = ('LTEModelAdmin', 'site')


class LTEModelAdmin(ModelAdmin):

    @property
    def app_label(self):
        return self.model._meta.app_label

    @property
    def model_name(self):
        return self.model._meta.model_name

    @method_decorator(csrf_protect)
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        response.template_name = self.change_list_template or [
            'lte/%s/%s/change_list.html' % (self.app_label, self.model_name),
            'lte/%s/change_list.html' % self.app_label,
            'lte/change_list.html'
        ]
        return response


class LTEAdminSite(AdminSite):
    site_title = _('DjangoLTE')
    site_header = _('Site Administration')

    def get_urls(self):
        """ Main method to generate admin urlpatterns """
        from django.conf.urls import url, include
        from django.contrib.contenttypes import views as contenttype_views

        if settings.DEBUG:
            self.check_dependencies()

        # Admin Index
        urlpatterns = [url(r'^$', views.IndexView.as_view(registry=self._registry), name='index')]
        # Authentication app views
        urlpatterns += self.get_auth_app_urls()
        # Site wide views
        urlpatterns += [
            url(r'^jsi18n/$',
                self.set_admin_view(self.i18n_javascript, cacheable=True),
                name='jsi18n'
            ),
            url(r'^r/(?P<content_type_id>\d+)/(?P<object_id>.+)/$',
                self.set_admin_view(contenttype_views.shortcut),
                name='view_on_site'
            ),
        ]
        # Apps views
        urlpatterns += self.get_apps_urls()

        return urlpatterns

    def get_auth_app_urls(self):
        """
        Generates the authentication app urls. You can replace it based on
        you auth app.

        Here, we have login and logout, profile detail and update, password change and reset.
        """
        urlpatterns = [
            url(r'^login/$', views.accounts.LoginView.as_view(), name='login'),
            url(r'^logout/$', views.accounts.LogoutView.as_view(), name='logout'),
            url(r'^profile/$',
                views.accounts.ProfileDetailView.as_view(),
                name='profile',
            ),
            url(r'^profile/edit/$',
                views.accounts.ProfileUpdateView.as_view(),
                name='profile_update',
            ),
            url(r'^password-change/$',
                views.accounts.PasswordChangeView.as_view(),
                name='password_change',
            ),
            url(r'^password-reset/$',
                views.accounts.PasswordResetView.as_view(),
                name='password_reset',
            ),
            url(r'^password-reset/done/$',
                views.accounts.PasswordResetDoneView.as_view(),
                name='password_reset_done',
            ),
            url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                views.accounts.PasswordResetConfirmAndLoginView.as_view(),
                name='password_reset_confirm',
            ),
        ]
        return urlpatterns

    def get_apps_urls(self):
        """ Generates a url list for each app and their models """
        # First, creates urls for models
        urlpatterns = [self.create_model_url(*model) for model in self._registry.items()]
        # Then, creates urls for apps indexes
        if self.app_list:
            urlpatterns += self.create_app_index_url()
        return urlpatterns

    @property
    def app_list(self):
        return (model._meta.app_label for model, model_admin in self._registry.items())

    def set_admin_view(self, view, cacheable=False):
        """
        Set admin views in the same way that wrap in AdminSite.get_urls does
        """
        def wrapper(*args, **kwargs):
            return self.admin_view(view, cacheable)(*args, **kwargs)
        return update_wrapper(wrapper, view)

    def create_model_url_regex(self, model):
        """ Generates url regex for models (eg. ^blog/post/) """
        return r'^{app}/{model}/'.format(
            app=model._meta.app_label,
            model=model._meta.model_name,
        )

    def create_model_url(self, model, model_admin):
        """ Generates CRUD urls for a model """
        return url(self.create_model_url_regex(model), include(model_admin.urls))

    def create_app_index_url(self):
        """ Generates one url for all apps indexes """
        apps_regex = '|'.join(self.app_list)
        regex = r'^(?P<app_label>{})/$'.format(apps_regex)
        return [url(regex, views.AppIndexView.as_view(registry=self._registry), name='app_list')]


site = LTEAdminSite(name='lte')
