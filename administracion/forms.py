from django import forms
from django.contrib.auth import password_validation

from cuentas.forms import FormularioBootstrap
from cuentas.models import Usuario


class UsuarioAdminForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["first_name", "last_name", "email", "perfil", "cargo", "telefono", "is_active"]


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
