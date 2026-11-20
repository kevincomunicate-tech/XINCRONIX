from django import forms
from django.contrib.auth import password_validation
from django.db import transaction
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm

from .models import Empresa, Rol, Usuario


class LoginForm(AuthenticationForm):
    """Login con correo + contraseña + 'recordar sesión'.

    AuthenticationForm llama 'username' al campo de identificación; como
    nuestro USERNAME_FIELD es 'email', ahí llega el correo.
    """

    username = forms.EmailField(
        label="Correo corporativo",
        widget=forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "tu@empresa.com", "autofocus": True}),
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password", "placeholder": "••••••••••"}),
    )
    recordar = forms.BooleanField(label="Recordar sesión", required=False)

    error_messages = {
        "invalid_login": "Correo o contraseña incorrectos.",
        "inactive": "Esta cuenta está desactivada.",
    }

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()


class RegistroForm(forms.Form):
    """Registro: nombre completo, empresa, correo y contraseña.

    Como en el sistema original, quien se registra crea su empresa y
    queda como su administrador.
    """

    nombre = forms.CharField(
        label="Nombre completo",
        max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "name", "placeholder": "María García López", "autofocus": True}),
    )
    empresa = forms.CharField(
        label="Nombre de la empresa",
        max_length=200,
        widget=forms.TextInput(attrs={"autocomplete": "organization", "placeholder": "Mi Empresa S.A.S."}),
    )
    email = forms.EmailField(
        label="Correo electrónico",
        max_length=150,
        widget=forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "tu@empresa.com"}),
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "placeholder": "Mínimo 8 caracteres"}),
    )

    def clean_nombre(self):
        nombre = " ".join(self.cleaned_data["nombre"].split())
        if len(nombre.split(" ")) < 2:
            raise forms.ValidationError("Escribe tu nombre y tu apellido.")
        return nombre

    def clean_empresa(self):
        return " ".join(self.cleaned_data["empresa"].split())

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email

    def clean(self):
        datos = super().clean()
        password = datos.get("password")
        if password:
            # Usa las reglas de AUTH_PASSWORD_VALIDATORS (mínimo 8, no común, etc.)
            nombre = datos.get("nombre", "")
            temporal = Usuario(email=datos.get("email", ""), nombres=nombre)
            try:
                password_validation.validate_password(password, temporal)
            except forms.ValidationError as error:
                self.add_error("password", error)
        return datos

    @transaction.atomic
    def save(self):
        nombre, _, apellido = self.cleaned_data["nombre"].partition(" ")
        empresa = Empresa.objects.create(nombre=self.cleaned_data["empresa"], email=self.cleaned_data["email"])
        return Usuario.objects.create_user(
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            nombres=nombre,
            apellidos=apellido,
            empresa=empresa,
            rol=Rol.ADMIN,
        )


class RecuperarForm(PasswordResetForm):
    """Pedir el enlace: el mismo de Django con el texto de ayuda en el campo."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "Correo electrónico"
        self.fields["email"].widget.attrs.update({"placeholder": "tu@empresa.com", "autofocus": True})


class NuevaContrasenaForm(SetPasswordForm):
    """Contraseña nueva: el de Django con textos de ayuda en los campos."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].widget.attrs.update({"placeholder": "Mínimo 8 caracteres", "autofocus": True})
        self.fields["new_password2"].label = "Repite la contraseña"
        self.fields["new_password2"].widget.attrs.update({"placeholder": "Escríbela de nuevo"})
        self.fields["new_password1"].help_text = ""
