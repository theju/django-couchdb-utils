from django import forms
from auth.models import User
from openid_consumer.models import server_uri, get_or_create, get_values
from django_openid.forms import RegistrationForm as DjangoOpenidRegistrationForm, \
                                RegistrationFormPasswordConfirm as DjangoOpenidRegistrationFormPasswordConfirm

class RegistrationForm(DjangoOpenidRegistrationForm):
    auth_db = get_or_create(server_uri, "auth")

    def save(self):
        user = User(**self.cleaned_data)
        return user.store(self.auth_db)

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if self.no_duplicate_emails and len(get_values(self.auth_db.view('auth_email/all', key = email))) > 0:
            raise forms.ValidationError, self.duplicate_email_error
        return email

    def clean(self):
        return self.cleaned_data

class RegistrationFormPasswordConfirm(RegistrationForm, DjangoOpenidRegistrationFormPasswordConfirm):
    pass
