from django.contrib import auth
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic

from authtools import views as at_views
from braces import views as braces_views

from lte_accounts import forms as accounts_forms


User = auth.get_user_model()


class AdminPermissionViewMixin(braces_views.UserPassesTestMixin):
    """ CBV that implements AdminSite.has_permission """

    def has_permission(self, user):
        return user.is_active and user.is_staff

    def test_func(self, user):
        return self.has_permission()


class LoginView(at_views.LoginView):
    template_name = 'lte/accounts/login.html'
    form_class = accounts_forms.AuthForm
    success_url = reverse_lazy('admin:profile')

    def set_session_expiration(self, form):
        if form.cleaned_data['remember_me'] is False:
            # expires at browser close
            self.request.session.set_expiry(0)

    def form_valid(self, form):
        auth.login(self.request, form.get_user())
        self.set_session_expiration(form)
        return super().form_valid(form)


class LogoutView(AdminPermissionViewMixin, at_views.LogoutView):
    url = reverse_lazy('admin:login')


class ProfileDetailView(AdminPermissionViewMixin, generic.DetailView):
    template_name = 'lte/accounts/profile.html'

    def get_object(self):
        return self.request.user


class ProfileUpdateView(AdminPermissionViewMixin, generic.UpdateView):
    form_class = accounts_forms.ProfileUpdate
    model = User
    success_url = reverse_lazy('admin:profile')
    template_name = 'lte/accounts/profile_update.html'

    def get_object(self):
        return self.request.user


class PasswordChangeView(AdminPermissionViewMixin, at_views.PasswordChangeView):
    success_url = reverse_lazy('admin:profile')
    template_name = 'lte/accounts/password_change.html'


# Reset password views
class PasswordResetView(at_views.PasswordResetView):
    email_template_name = 'lte/accounts/password_reset_email.html'
    success_url = reverse_lazy('admin:password_reset_done')
    template_name = 'lte/accounts/password_reset_view.html'


class PasswordResetDoneView(at_views.PasswordResetDoneView):
    template_name = 'lte/accounts/password_reset_done.html'


class PasswordResetConfirmAndLoginView(at_views.PasswordResetConfirmAndLoginView):
    template_name = 'lte/accounts/password_reset_confirm.html'