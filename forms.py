from django import forms
from django.contrib.auth import forms as auth_forms
from django.utils.translation import ugettext_lazy as _

from authtools import forms as at_forms

from lte_accounts import forms as accounts_forms


class LoginForm(accounts_forms.AuthForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Email'),
        }),
        max_length=25)
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Password'),
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        label=_('Remember me'),
        widget=forms.CheckboxInput(attrs={
            'class': 'icheck',
        }),
    )


class ProfileForm(accounts_forms.ProfileUpdate):

    class Meta(accounts_forms.ProfileUpdate.Meta):
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'email': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }


class SetPasswordForm(auth_forms.SetPasswordForm):
    new_password1 = forms.CharField(
        label=_('New password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('New password'),
        }),
    )
    new_password2 = forms.CharField(
        label=_('New password confirmation'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Repeat new password'),
        })
    )


class PasswordUpdateForm(SetPasswordForm, auth_forms.PasswordChangeForm):
    old_password = forms.CharField(
        label=_('Old password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Old password'),
        })
    )


class PasswordResetForm(auth_forms.PasswordResetForm):
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Your email'),
        })
    )
