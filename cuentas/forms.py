from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm

from .models import Usuario


CLASES_BOOTSTRAP = {"checkbox": "form-check-input", "select": "form-select", "select-multiple": "form-select"}


class FormularioBootstrap:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            tipo = getattr(campo.widget, "input_type", "")
            campo.widget.attrs.setdefault("class", CLASES_BOOTSTRAP.get(tipo, "form-control"))


class CampoFecha(forms.DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        super().__init__(format="%Y-%m-%d", **kwargs)


class CampoFechaHora(forms.DateTimeInput):
    input_type = "datetime-local"

    def __init__(self, **kwargs):
        super().__init__(format="%Y-%m-%dT%H:%M", **kwargs)


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Correo electrónico", widget=forms.EmailInput(attrs={"autocomplete": "email", "autofocus": True}))
    password = forms.CharField(label="Contraseña", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))
    recordar = forms.BooleanField(label="Recordar sesión", required=False)

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()


class RegistroForm(FormularioBootstrap, forms.Form):
    nombre = forms.CharField(label="Nombre completo", max_length=150, widget=forms.TextInput(attrs={"autocomplete": "name", "autofocus": True}))
    email = forms.EmailField(label="Correo electrónico", max_length=150, widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    password = forms.CharField(label="Contraseña", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))

    def clean_nombre(self):
        partes = self.cleaned_data["nombre"].split()
        if len(partes) < 2:
            raise forms.ValidationError("Escribe tus nombres y tus apellidos (al menos dos palabras).")
        return " ".join(partes)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese correo.")
        return email

    def clean(self):
        datos = super().clean()
        if datos.get("password"):
            temporal = Usuario(email=datos.get("email", ""), first_name=datos.get("nombre", ""))
            try:
                password_validation.validate_password(datos["password"], temporal)
            except forms.ValidationError as error:
                self.add_error("password", error)
        return datos

    def save(self):
        nombre, _, apellido = self.cleaned_data["nombre"].partition(" ")
        return Usuario.objects.create_user(
            email=self.cleaned_data["email"], password=self.cleaned_data["password"],
            first_name=nombre, last_name=apellido,
        )


class RecuperarForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "Correo electrónico"


class NuevaContrasenaForm(SetPasswordForm):
    pass


class PerfilForm(FormularioBootstrap, forms.ModelForm):
    def save(self, commit=True):
        usuario = super().save(commit=False)
        if commit:
            usuario.save(update_fields=self.Meta.fields)
        return usuario

    class Meta:
        model = Usuario
        fields = ["first_name", "last_name", "email", "cargo", "telefono"]
        labels = {"first_name": "Nombres", "last_name": "Apellidos", "cargo": "Especialidad o rol"}

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if Usuario.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("Ya existe otra cuenta con ese correo.")
        return email


class CambiarContrasenaForm(FormularioBootstrap, SetPasswordForm):
    actual = forms.CharField(label="Contraseña actual", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        if not user.has_usable_password():
            del self.fields["actual"]

    def clean_actual(self):
        if not self.user.check_password(self.cleaned_data["actual"]):
            raise forms.ValidationError("La contraseña actual no es correcta.")
        return self.cleaned_data["actual"]


class EliminarCuentaForm(FormularioBootstrap, forms.Form):
    confirmacion = forms.CharField(label="Escribe tu correo para confirmar")

    def __init__(self, *args, usuario, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario

    def clean_confirmacion(self):
        value = self.cleaned_data["confirmacion"].strip().lower()
        if value != self.usuario.email.lower():
            raise forms.ValidationError("El correo no coincide con el de tu cuenta.")
        return value
