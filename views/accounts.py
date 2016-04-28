from django.contrib import auth
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from authtools import views as at_views
from braces import views as braces_views

from .. import forms
from . import base


User = auth.get_user_model()


class LoginView(base.PublicAdminViewMixin, base.NoCacheAdminViewMixin, at_views.LoginView):
    form_class = forms.LoginForm
    success_url = reverse_lazy('admin:profile')
    template_name = 'lte/accounts/login.html'
    title = _('Login')

    def set_session_expiration(self, form):
        if form.cleaned_data['remember_me'] is False:
            # expires at browser close
            self.request.session.set_expiry(0)

    def form_valid(self, form):
        auth.login(self.request, form.get_user())
        self.set_session_expiration(form)
        return super().form_valid(form)


class LogoutView(base.NoCacheAdminViewMixin, at_views.LogoutView):
    url = reverse_lazy('admin:login')


class ProfileDetailView(base.PrivateAdminViewMixin, generic.DetailView):
    template_name = 'lte/accounts/profile.html'
    title = _('Profile')

    def get_object(self):
        return self.request.user


class ProfileUpdateView(base.PrivateAdminViewMixin, generic.UpdateView):
    form_class = forms.ProfileForm
    model = User
    success_url = reverse_lazy('admin:profile')
    template_name = 'lte/accounts/profile_update.html'
    title = _('Update Profile')

    def get_object(self):
        return self.request.user


class PasswordChangeView(base.PrivateAdminViewMixin, at_views.PasswordChangeView):
    form_class = forms.PasswordUpdateForm
    success_url = reverse_lazy('admin:profile')
    template_name = 'lte/accounts/password_change.html'
    title = _('Change password')


# Reset password views
class PasswordResetView(base.PublicAdminViewMixin, at_views.PasswordResetView):
    email_template_name = 'lte/accounts/password_reset_email.html'
    form_class = forms.PasswordResetForm
    success_url = reverse_lazy('admin:password_reset_done')
    template_name = 'lte/accounts/password_reset_view.html'
    title = _('Password reset')


class PasswordResetDoneView(base.PublicAdminViewMixin, at_views.PasswordResetDoneView):
    template_name = 'lte/accounts/password_reset_done.html'
    title = _('Password reset')


class PasswordResetConfirmAndLoginView(base.PublicAdminViewMixin, at_views.PasswordResetConfirmAndLoginView):
    form_class = forms.SetPasswordForm
    template_name = 'lte/accounts/password_reset_confirm.html'
    success_url = reverse_lazy('admin:profile')
    title = _('Password reset confirm')
