from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.db import transaction

from .models import Empresa, Rol, Usuario
from .politica import obtener_politica

# Clase de Bootstrap según el tipo de campo (el resto usa "form-control")
CLASES_BOOTSTRAP = {"checkbox": "form-check-input", "select": "form-select", "select-multiple": "form-select"}


class FormularioBootstrap:
    """Mezcla para que cualquier formulario se vea con el estilo del panel."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            tipo = getattr(campo.widget, "input_type", "")
            campo.widget.attrs.setdefault("class", CLASES_BOOTSTRAP.get(tipo, "form-control"))


class CampoFecha(forms.DateInput):
    """Selector de fecha del navegador (input type="date")."""

    input_type = "date"

    def __init__(self, **kwargs):
        super().__init__(format="%Y-%m-%d", **kwargs)


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
    """Registro con solo nombre completo, correo y contraseña."""

    nombre = forms.CharField(
        label="Nombre completo",
        max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "name", "placeholder": "María García López", "autofocus": True}),
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
            temporal = Usuario(email=datos.get("email", ""), first_name=nombre)
            try:
                password_validation.validate_password(password, temporal)
            except forms.ValidationError as error:
                self.add_error("password", error)
        return datos

    @transaction.atomic  # empresa y usuario se crean juntos, o ninguno
    def save(self):
        """Crea el usuario como USUARIO NORMAL.

        El rol y si recibe su propia empresa salen de la sección "registro"
        de config/politica_accesos.json. El rol Administrador solo lo asigna
        el superadministrador, desde /administracion/.
        """
        politica = obtener_politica()
        nombre, _, apellido = self.cleaned_data["nombre"].partition(" ")
        empresa = Empresa.objects.create(nombre=f"Empresa de {nombre}") if politica.crear_empresa_propia else None
        return Usuario.objects.create_user(
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            first_name=nombre,
            last_name=apellido,
            empresa=empresa,
            rol=Rol.objects.get(codigo=politica.rol_registro),
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


# ---------------------------------------------------------------------------
# Mi cuenta (cada persona administra su propia información)
# ---------------------------------------------------------------------------

class PerfilForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["first_name", "last_name", "email", "cargo", "telefono"]
        labels = {"first_name": "Nombres", "last_name": "Apellidos", "email": "Correo electrónico"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if Usuario.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("Ya existe otra cuenta con este correo.")
        return email


class CambiarContrasenaForm(FormularioBootstrap, SetPasswordForm):
    """Cambiar (o crear, si entró con Google) la contraseña.

    Si la cuenta ya tiene contraseña, pide la actual primero.
    """

    actual = forms.CharField(label="Contraseña actual", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))
    field_order = ["actual", "new_password1", "new_password2"]

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields["new_password2"].label = "Repite la contraseña nueva"
        self.fields["new_password1"].help_text = "Mínimo 8 caracteres, que no sea común ni solo números."
        if not user.has_usable_password():
            del self.fields["actual"]  # entró con Google: todavía no tiene contraseña

    def clean_actual(self):
        if not self.user.check_password(self.cleaned_data["actual"]):
            raise forms.ValidationError("La contraseña actual no es correcta.")
        return self.cleaned_data["actual"]


class EliminarCuentaForm(FormularioBootstrap, forms.Form):
    """Confirma la eliminación escribiendo el correo de la cuenta."""

    confirmacion = forms.CharField(label="Escribe tu correo para confirmar")

    def __init__(self, *args, usuario, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario
        self.fields["confirmacion"].widget.attrs["placeholder"] = usuario.email

    def clean_confirmacion(self):
        if self.cleaned_data["confirmacion"].strip().lower() != self.usuario.email.lower():
            raise forms.ValidationError("El correo no coincide con el de tu cuenta.")
        return self.cleaned_data["confirmacion"]


class EmpresaForm(FormularioBootstrap, forms.ModelForm):
    """Datos de una empresa (lo usan "Mi empresa" y la administración)."""

    class Meta:
        model = Empresa
        fields = ["nombre", "nit", "email", "telefono", "direccion", "sector", "num_empleados"]

    def clean_nit(self):
        return self.cleaned_data["nit"] or None  # vacío -> NULL (el NIT es único si existe)
