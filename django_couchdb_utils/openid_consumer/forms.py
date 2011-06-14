from django import forms
from django_couchdb_utils.auth.models import User
from django_openid.forms import RegistrationForm as DjangoOpenidRegistrationForm, \
                                RegistrationFormPasswordConfirm as DjangoOpenidRegistrationFormPasswordConfirm
from couchdbkit.exceptions import ResourceNotFound

class RegistrationForm(DjangoOpenidRegistrationForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

    def save(self):
        user = User(**self.cleaned_data)
        return user.store()

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        try:
            email_count = User.view('%s/users_by_email' % User._meta.app_label, key = email).count()
        except ResourceNotFound:
            email_count = 0
        if self.no_duplicate_emails and email_count > 0:
            raise forms.ValidationError, self.duplicate_email_error
        return email

    def clean(self):
        return self.cleaned_data

class RegistrationFormPasswordConfirm(RegistrationForm, DjangoOpenidRegistrationFormPasswordConfirm):
    pass
