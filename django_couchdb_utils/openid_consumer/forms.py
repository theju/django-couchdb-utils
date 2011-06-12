from django import forms
from django_couchdb_utils.auth.models import User
from django_openid.forms import RegistrationForm as DjangoOpenidRegistrationForm, \
                                RegistrationFormPasswordConfirm as DjangoOpenidRegistrationFormPasswordConfirm

class RegistrationForm(DjangoOpenidRegistrationForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.auth_db = User.get_db()

    def save(self):
        user = User(**self.cleaned_data)
        return user.store(self.auth_db)

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if self.no_duplicate_emails and len(self.auth_db.view('auth_email/all', key = email)) > 0:
            raise forms.ValidationError, self.duplicate_email_error
        return email

    def clean(self):
        return self.cleaned_data

class RegistrationFormPasswordConfirm(RegistrationForm, DjangoOpenidRegistrationFormPasswordConfirm):
    pass
