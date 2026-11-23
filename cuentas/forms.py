from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.db import transaction
from urllib.parse import urlsplit

from .models import Empresa, Equipo, Usuario
from dashboard.models import Proyecto, ReferenciaGitHub, Tarea


def _estilizar_campos(form):
    for field in form.fields.values():
        if isinstance(field.widget, forms.CheckboxSelectMultiple):
            css_class = "form-check-input"
        elif isinstance(field.widget, forms.Select):
            css_class = "form-select"
        elif isinstance(field.widget, forms.CheckboxInput):
            css_class = "form-check-input"
        else:
            css_class = "form-control"
        clases = field.widget.attrs.get("class", "")
        field.widget.attrs["class"] = f"{clases} {css_class}".strip()


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
    """Crea un espacio de trabajo con su primer administrador."""

    empresa = forms.CharField(
        label="Nombre de la empresa",
        max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "organization", "placeholder": "Mi empresa"}),
    )
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
            temporal = Usuario(email=datos.get("email", ""), first_name=nombre)
            try:
                password_validation.validate_password(password, temporal)
            except forms.ValidationError as error:
                self.add_error("password", error)
        return datos

    @transaction.atomic
    def save(self):
        nombre, _, apellido = self.cleaned_data["nombre"].partition(" ")
        empresa = Empresa.objects.create(nombre=self.cleaned_data["empresa"])
        return Usuario.objects.create_user(
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            first_name=nombre,
            last_name=apellido,
            rol=Usuario.Rol.ADMIN,
            empresa=empresa,
        )


class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ("nombre", "descripcion", "miembros")
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "miembros": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, empresa, **kwargs):
        super().__init__(*args, **kwargs)
        _estilizar_campos(self)
        self.empresa = empresa
        self.fields["miembros"].queryset = Usuario.objects.filter(
            empresa=empresa, is_active=True
        ).order_by("first_name", "last_name", "email")


class MiembroForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    equipos = forms.ModelMultipleChoiceField(
        label="Equipos",
        queryset=Equipo.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:
        model = Usuario
        fields = ("first_name", "last_name", "email", "rol")
        labels = {
            "first_name": "Nombre",
            "last_name": "Apellidos",
            "email": "Correo electrónico",
            "rol": "Rol",
        }

    def __init__(self, *args, empresa, actor, **kwargs):
        super().__init__(*args, **kwargs)
        _estilizar_campos(self)
        self.empresa = empresa
        self.actor = actor
        self.fields["equipos"].queryset = Equipo.objects.filter(empresa=empresa)
        if actor.rol != Usuario.Rol.ADMIN:
            self.fields["rol"].choices = (
                (Usuario.Rol.SUPERVISOR, "Supervisor"),
                (Usuario.Rol.COLABORADOR, "Colaborador"),
            )
        if self.instance.pk:
            self.fields["equipos"].initial = self.instance.equipos.filter(empresa=empresa)
        else:
            self.fields["password"].required = True

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            password_validation.validate_password(password, self.instance)
        return password

    def save(self, commit=True):
        miembro = super().save(commit=False)
        miembro.empresa = self.empresa
        password = self.cleaned_data.get("password")
        if password:
            miembro.set_password(password)
        if commit:
            miembro.save()
            self.save_m2m()
            miembro.equipos.set(self.cleaned_data["equipos"])
        return miembro


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = (
            "nombre",
            "descripcion",
            "repositorio_url",
            "estado",
            "prioridad",
            "fecha_inicio",
            "fecha_fin",
            "equipo",
            "miembros",
        )
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "repositorio_url": forms.URLInput(attrs={"placeholder": "https://github.com/organizacion/repositorio"}),
            "fecha_inicio": forms.DateInput(attrs={"type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"type": "date"}),
            "miembros": forms.CheckboxSelectMultiple(),
        }
        labels = {"repositorio_url": "Repositorio público de GitHub"}
        help_texts = {
            "repositorio_url": (
                "Opcional. Enlace HTTPS a un repositorio público, por ejemplo "
                "https://github.com/organizacion/repositorio. No se consulta la API."
            )
        }

    def __init__(self, *args, empresa, **kwargs):
        super().__init__(*args, **kwargs)
        _estilizar_campos(self)
        self.empresa = empresa
        self.fields["equipo"].queryset = Equipo.objects.filter(empresa=empresa)
        self.fields["equipo"].required = False
        self.fields["miembros"].queryset = Usuario.objects.filter(
            empresa=empresa, is_active=True
        ).order_by("first_name", "last_name", "email")
        self.fields["miembros"].required = False

    def clean_repositorio_url(self):
        url = self.cleaned_data.get("repositorio_url", "").strip().rstrip("/")
        if not url:
            return ""
        partes = urlsplit(url)
        camino = partes.path.strip("/").split("/")
        if (
            partes.scheme != "https"
            or partes.netloc.lower() != "github.com"
            or partes.query
            or partes.fragment
            or len(camino) != 2
            or not all(camino)
        ):
            raise forms.ValidationError(
                "Escribe la URL HTTPS de un repositorio público, por ejemplo "
                "https://github.com/organizacion/repositorio."
            )
        if camino[1].endswith(".git"):
            camino[1] = camino[1][:-4]
        return f"https://github.com/{camino[0]}/{camino[1]}"

    def clean(self):
        datos = super().clean()
        inicio, fin = datos.get("fecha_inicio"), datos.get("fecha_fin")
        if inicio and fin and fin < inicio:
            self.add_error("fecha_fin", "La fecha límite no puede ser anterior a la fecha de inicio.")
        return datos


class ReferenciaGitHubForm(forms.ModelForm):
    class Meta:
        model = ReferenciaGitHub
        fields = ("tipo", "titulo", "url")
        widgets = {
            "titulo": forms.TextInput(attrs={"placeholder": "Ej. Preparar autenticación"}),
            "url": forms.URLInput(attrs={"placeholder": "https://github.com/organizacion/repositorio/issues/123"}),
        }

    def __init__(self, *args, proyecto, **kwargs):
        super().__init__(*args, **kwargs)
        _estilizar_campos(self)
        self.proyecto = proyecto
        self.fields["url"].help_text = (
            "Debe ser un issue o pull request del repositorio vinculado al proyecto."
        )

    def clean_titulo(self):
        return self.cleaned_data["titulo"].strip()

    def clean_url(self):
        url = self.cleaned_data["url"].strip()
        partes = urlsplit(url)
        ruta = partes.path.strip("/").split("/")
        repositorio_url = urlsplit(self.proyecto.repositorio_url)
        repositorio = repositorio_url.path.strip("/").split("/")
        if (
            partes.scheme != "https"
            or partes.netloc.lower() != "github.com"
            or partes.query
            or partes.fragment
            or len(ruta) != 4
            or len(repositorio) != 2
            or [segmento.casefold() for segmento in ruta[:2]]
            != [segmento.casefold() for segmento in repositorio]
            or ruta[3] == ""
            or not ruta[3].isdigit()
        ):
            raise forms.ValidationError(
                "El enlace debe pertenecer al repositorio de este proyecto y ser "
                "un issue o pull request de GitHub."
            )
        tipo_ruta = ruta[2].casefold()
        tipo_formulario = self.data.get("tipo", "")
        if (tipo_ruta == "issues" and tipo_formulario != ReferenciaGitHub.Tipo.ISSUE) or (
            tipo_ruta == "pull" and tipo_formulario != ReferenciaGitHub.Tipo.PULL_REQUEST
        ) or tipo_ruta not in {"issues", "pull"}:
            raise forms.ValidationError("El tipo seleccionado no coincide con el enlace.")
        if ReferenciaGitHub.objects.filter(proyecto=self.proyecto, url=url).exists():
            raise forms.ValidationError("Ese enlace ya está asociado al proyecto.")
        return url


class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ("proyecto", "titulo", "descripcion", "estado", "prioridad", "responsable", "fecha_limite")
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "fecha_limite": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, empresa, proyectos, **kwargs):
        super().__init__(*args, **kwargs)
        _estilizar_campos(self)
        self.empresa = empresa
        self.fields["proyecto"].queryset = proyectos
        self.fields["responsable"].queryset = Usuario.objects.none()
        proyecto_id = self.data.get("proyecto") if self.is_bound else None
        if not proyecto_id:
            proyecto_id = self.initial.get("proyecto")
        if not proyecto_id and self.instance.pk:
            proyecto_id = self.instance.proyecto_id
        if proyecto_id:
            proyecto = proyectos.filter(pk=proyecto_id).first()
            if proyecto:
                self.fields["responsable"].queryset = proyecto.miembros.filter(is_active=True)

    def clean(self):
        datos = super().clean()
        proyecto = datos.get("proyecto")
        responsable = datos.get("responsable")
        if proyecto and proyecto.empresa_id != self.empresa.id:
            self.add_error("proyecto", "Selecciona un proyecto de tu empresa.")
        if proyecto and responsable and not proyecto.miembros.filter(pk=responsable.pk, is_active=True).exists():
            self.add_error("responsable", "El responsable debe ser miembro activo del proyecto.")
        return datos


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
