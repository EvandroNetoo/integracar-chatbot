from django import forms
from django.contrib.auth.forms import AuthenticationForm


class SigninForm(AuthenticationForm):
    def get_invalid_login_error(self):
        return forms.ValidationError(
            'Credenciais inválidas.',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['autofocus'] = True

        placeholders = {
            'username': 'Digite seu email',
            'password': 'Digite sua senha',
        }
        for field_name, field in self.fields.items():
            field.widget.attrs['placeholder'] = placeholders[field_name]
