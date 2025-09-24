from django import forms
from django.core import validators
from django.core.files.uploadedfile import InMemoryUploadedFile

from ia.models import Documento


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        if self.required and not result:
            raise forms.ValidationError(
                self.error_messages['required'], code='required'
            )
        return result


class ImportarDocumentosForm(forms.Form):
    documentos = MultipleFileField(
        label='Selecione os PDFs',
        validators=[validators.FileExtensionValidator(['pdf'])],
    )

    def __init__(self, *args, **kwargs):
        kwargs['use_required_attribute'] = False
        super().__init__(*args, **kwargs)
        self.fields['documentos'].widget.attrs['autocomplete'] = 'off'

    def save(self):
        documentos: list[InMemoryUploadedFile] = self.cleaned_data[
            'documentos'
        ]

        for documento in documentos:
            Documento(nome=documento.name, arquivo=documento).save()
