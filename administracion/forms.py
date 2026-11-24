from django import forms
from django.contrib.auth import password_validation

from cuentas.forms import EmpresaForm, FormularioBootstrap
from cuentas.models import Empresa, Rol, Usuario
from cuentas.politica import obtener_politica


def usuarios_gestionables():
    """Cuentas que el superadministrador puede editar: todas menos las de superadministradores."""
    return Usuario.objects.exclude(email__in=obtener_politica().superadministradores)


class AsignacionForm(FormularioBootstrap, forms.ModelForm):
    """Editar un usuario: datos, rol, empresa y estado.

    El campo "rol" solo ofrece los roles que la política deja asignar a quien
    edita (perfiles.<perfil>.puede_asignar en el JSON), y además se vuelve a
    comprobar al guardar: aunque alguien manipule el formulario en el
    navegador, el servidor no acepta un rol que no le toca.
    """

    class Meta:
        model = Usuario
        fields = ["first_name", "last_name", "email", "cargo", "telefono", "rol", "empresa", "is_active"]
        labels = {"first_name": "Nombres", "last_name": "Apellidos", "email": "Correo", "is_active": "Cuenta activa"}

    def __init__(self, *args, asignador, **kwargs):
        super().__init__(*args, **kwargs)
        self.asignador = asignador
        self.politica = obtener_politica()
        self.fields["rol"].queryset = Rol.objects.filter(codigo__in=self.politica.roles_asignables(asignador))
        self.fields["rol"].required = True
        self.fields["empresa"].queryset = Empresa.objects.order_by("nombre")
        self.fields["empresa"].required = False
        self.fields["empresa"].empty_label = "Sin empresa"

    def clean_rol(self):
        rol = self.cleaned_data["rol"]
        if not self.politica.puede_asignar(self.asignador, rol.codigo):
            raise forms.ValidationError("Tu perfil no puede asignar este rol.")
        return rol

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if email in self.politica.superadministradores:
            raise forms.ValidationError("Ese correo está reservado para el superadministrador.")
        if Usuario.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("Ya existe otra cuenta con este correo.")
        return email


class UsuarioCrearForm(AsignacionForm):
    password = forms.CharField(
        label="Contraseña inicial", strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="La persona podrá cambiarla en «Mi cuenta».",
    )

    class Meta(AsignacionForm.Meta):
        fields = ["first_name", "last_name", "email", "password", "cargo", "telefono", "rol", "empresa", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["password"].widget.attrs["class"] = "form-control"
        self.initial.setdefault("is_active", True)
        self.initial.setdefault("rol", Rol.objects.filter(codigo=self.politica.rol_registro).first())

    def clean(self):
        datos = super().clean()
        if datos.get("password"):
            try:
                password_validation.validate_password(datos["password"], Usuario(email=datos.get("email", ""), first_name=datos.get("first_name", "")))
            except forms.ValidationError as error:
                self.add_error("password", error)
        return datos

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password"])  # se guarda cifrada
        usuario.save()
        return usuario


class EmpresaAdminForm(EmpresaForm):
    """Empresa + propietario. El propietario queda vinculado a la empresa."""

    class Meta(EmpresaForm.Meta):
        fields = EmpresaForm.Meta.fields + ["propietario"]
        help_texts = {"propietario": "Queda vinculado a esta empresa (si estaba en otra, se cambia)."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["propietario"].queryset = usuarios_gestionables().filter(is_active=True).order_by("first_name", "email")
        self.fields["propietario"].empty_label = "Sin propietario"

    def save(self, commit=True):
        empresa = super().save(commit=commit)
        propietario = self.cleaned_data.get("propietario")
        if propietario and propietario.empresa_id != empresa.pk:
            propietario.empresa = empresa
            propietario.save(update_fields=["empresa"])
        return empresa


class VincularForm(FormularioBootstrap, forms.Form):
    """Vincular un usuario existente a una empresa."""

    usuario = forms.ModelChoiceField(label="Usuario", queryset=Usuario.objects.none(), empty_label="Elige un usuario")

    def __init__(self, *args, empresa, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["usuario"].queryset = (
            usuarios_gestionables().exclude(empresa=empresa).select_related("empresa").order_by("first_name", "email")
        )
        self.fields["usuario"].label_from_instance = lambda u: f"{u} ({u.email}) — {u.empresa or 'sin empresa'}"
