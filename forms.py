from django import forms
from django.contrib import auth
from django.utils.translation import ugettext_lazy as _

from lte_accounts import forms as accounts_forms


User = auth.get_user_model()


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
