from django import forms
from django.contrib.auth import password_validation

from cuentas.forms import FormularioBootstrap
from cuentas.models import Usuario


class UsuarioAdminForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["first_name", "last_name", "email", "rol", "cargo", "telefono", "is_active"]

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)
        campo = self.fields["rol"]
        campo.required = False
        campo.choices = [
            (rol, label) for rol, label in Usuario.Rol.choices
            if rol != Usuario.Rol.ADMIN or getattr(actor, "is_superuser", False)
        ]
        if self.instance.is_superuser:
            campo.disabled = True

    def clean_rol(self):
        return self.cleaned_data["rol"] or self.instance.rol

    def save(self, commit=True):
        usuario = super().save(commit=False)
        if commit and usuario.pk:
            usuario.save(update_fields=self.Meta.fields)
        elif commit:
            usuario.save()
        return usuario


class UsuarioCrearForm(UsuarioAdminForm):
    password = forms.CharField(label="Contraseña inicial", widget=forms.PasswordInput)

    def clean(self):
        datos = super().clean()
        if datos.get("password"):
            try:
                password_validation.validate_password(datos["password"], Usuario(email=datos.get("email", "")))
            except forms.ValidationError as error:
                self.add_error("password", error)
        return datos

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password"])
        if commit:
            usuario.save()
        return usuario
