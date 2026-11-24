from django import forms

from cuentas.forms import CampoFecha, FormularioBootstrap
from cuentas.models import Usuario

from .models import Proyecto, ProyectoMiembro, Tarea, Hito, InvitacionProyecto


class CuestionarioProyectoForm(FormularioBootstrap, forms.Form):
    """Preguntas sugeridas antes de crear el proyecto (pueden omitirse)."""

    proposito = forms.ChoiceField(
        label="¿Para qué es este proyecto?",
        choices=[("", "— Prefiero no responder —")] + list(Proyecto.Proposito.choices),
        required=False,
        help_text="Escolar, comercial, despliegue, open source…",
    )
    metodologia = forms.ChoiceField(
        label="¿Qué metodología usarán?",
        choices=[("", "— Prefiero no responder —")] + list(Proyecto.Metodologia.choices),
        required=False,
        help_text="Scrum, Kanban, GAES, Pomodoro…",
    )
    es_educativo = forms.BooleanField(
        label="Es un proyecto educativo (colegio / universidad / institución)",
        required=False,
        help_text="Si marcas esto, podrás asignar un profesor como supervisor para correcciones y seguimiento.",
    )
    es_grupal = forms.BooleanField(
        label="Será un proyecto grupal (invitaré a más personas)",
        required=False,
        help_text="Podrás enviar enlaces de invitación por correo.",
    )
    notas = forms.CharField(
        label="Notas iniciales (opcional)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Cualquier contexto útil para el equipo…"}),
    )


class ProyectoForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = [
            "nombre", "descripcion", "estado", "nivel_importancia",
            "tipo_proyecto", "proposito", "metodologia", "es_educativo", "es_grupal",
            "fecha_inicio", "fecha_fin",
        ]
        labels = {
            "nivel_importancia": "Importancia",
            "tipo_proyecto": "Tipo técnico",
            "proposito": "Propósito",
            "metodologia": "Metodología",
            "es_educativo": "Proyecto educativo",
            "es_grupal": "Proyecto grupal",
        }
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "fecha_inicio": CampoFecha(),
            "fecha_fin": CampoFecha(),
        }


class TareaForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ["titulo", "descripcion", "estado", "prioridad", "fecha_vencimiento", "asignado_a"]
        labels = {"fecha_vencimiento": "Fecha límite", "asignado_a": "Responsable"}
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3}), "fecha_vencimiento": CampoFecha()}

    def __init__(self, *args, proyecto, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["asignado_a"].queryset = proyecto.personas().order_by("first_name", "email")
        self.fields["asignado_a"].required = False


class MiembroForm(FormularioBootstrap, forms.Form):
    """Agregar a alguien al proyecto por su correo o generar invitación."""

    email = forms.EmailField(
        label="Correo de la persona",
        widget=forms.EmailInput(attrs={"placeholder": "persona@correo.com"}),
    )
    rol = forms.ChoiceField(
        label="Rol en el proyecto",
        choices=ProyectoMiembro.RolProyecto.choices,
        initial=ProyectoMiembro.RolProyecto.EDITOR,
    )
    enviar_invitacion = forms.BooleanField(
        label="Si no tiene cuenta, enviar enlace de invitación por correo",
        required=False,
        initial=True,
    )

    def __init__(self, *args, proyecto, **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto = proyecto
        self.usuario = None

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        usuario = Usuario.objects.filter(email=email, is_active=True).first()
        if usuario:
            if usuario.pk == self.proyecto.creado_por_id:
                raise forms.ValidationError("Es quien creó el proyecto: ya tiene todos los permisos.")
            if self.proyecto.proyectomiembro_set.filter(usuario=usuario).exists():
                raise forms.ValidationError("Esa persona ya está en el proyecto.")
            self.usuario = usuario
        return email

    def save(self, creado_por=None):
        if self.usuario:
            return ProyectoMiembro.objects.create(
                proyecto=self.proyecto, usuario=self.usuario, rol=self.cleaned_data["rol"]
            )
        import secrets
        from django.utils import timezone
        from datetime import timedelta

        token = secrets.token_urlsafe(32)
        inv = InvitacionProyecto.objects.create(
            proyecto=self.proyecto,
            email=self.cleaned_data["email"],
            token=token,
            rol=self.cleaned_data["rol"],
            creada_por=creado_por,
            fecha_expiracion=timezone.now() + timedelta(days=14),
        )
        return inv


class HitoForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Hito
        fields = ["titulo", "descripcion", "fecha_objetivo", "estado", "orden"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 2}),
            "fecha_objetivo": CampoFecha(),
        }
