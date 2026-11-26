import os

from django import forms
from django.core.exceptions import ValidationError

from cuentas.forms import CampoFecha, CampoFechaHora, FormularioBootstrap
from cuentas.models import Usuario

from .models import Correccion, DocumentoProyecto, Evento, InvitacionProyecto, Proyecto, ProyectoMiembro, Tarea


class OrientacionProyectoForm(FormularioBootstrap, forms.Form):
    """Primera pantalla opcional: da contexto sin bloquear la creación."""

    finalidad = forms.ChoiceField(label="¿Para qué es este proyecto?", choices=[("", "Prefiero omitirlo")] + list(Proyecto.Finalidad.choices), required=False)
    metodologia = forms.ChoiceField(label="¿Cómo quieres trabajar?", choices=[("", "Prefiero decidir después")] + list(Proyecto.Metodologia.choices), required=False)
    modalidad = forms.ChoiceField(label="¿Trabajarás solo o en grupo?", choices=[("", "Aún no lo sé")] + list(Proyecto.Modalidad.choices), required=False)
    contexto_educativo = forms.CharField(label="Curso, institución o reto (opcional)", max_length=180, required=False)
    supervisor_email = forms.EmailField(label="Correo del profesor supervisor (opcional)", required=False)


class ProyectoForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ["nombre", "descripcion", "tecnologia", "repositorio_url", "estado", "fecha_inicio", "fecha_fin", "supervisor"]
        labels = {"repositorio_url": "Repositorio o demo", "supervisor": "Profesor supervisor"}
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 4}), "fecha_inicio": CampoFecha(), "fecha_fin": CampoFecha()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["supervisor"].queryset = Usuario.objects.filter(perfil=Usuario.Perfil.PROFESOR, is_active=True).order_by("first_name", "email")
        self.fields["supervisor"].required = False


class ProyectoLiderForm(ProyectoForm):
    """Lo que solo decide el líder: si el proyecto es individual o grupal, y si es público o privado."""

    class Meta(ProyectoForm.Meta):
        fields = ProyectoForm.Meta.fields + ["modalidad", "visibilidad"]
        labels = {**ProyectoForm.Meta.labels, "modalidad": "¿Trabajas solo o en grupo?", "visibilidad": "Visibilidad"}


class InvitacionForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = InvitacionProyecto
        fields = ["email", "rol"]
        labels = {"email": "Correo de la persona invitada", "rol": "Acceso"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Nadie puede invitar como líder: solo editor o lector. El líder es quien creó el proyecto.
        roles_invitables = {ProyectoMiembro.Rol.EDITOR, ProyectoMiembro.Rol.LECTOR}
        self.fields["rol"].choices = [(v, t) for v, t in ProyectoMiembro.Rol.choices if v in roles_invitables]

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()


class TareaForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ["titulo", "descripcion", "estado", "prioridad", "fecha_vencimiento", "asignado_a"]
        labels = {"asignado_a": "Responsable", "fecha_vencimiento": "Fecha límite"}
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3}), "fecha_vencimiento": CampoFecha()}

    def __init__(self, *args, proyecto, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["asignado_a"].queryset = proyecto.personas().order_by("first_name", "email")
        self.fields["asignado_a"].required = False


class EventoForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Evento
        fields = ["titulo", "descripcion", "inicia_en", "termina_en"]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 2}), "inicia_en": CampoFechaHora(), "termina_en": CampoFechaHora()}


# Tipos y tamaño permitidos para documentos del proyecto. Nada ejecutable ni HTML:
# un .html o .js subido podría ejecutarse en el navegador de quien lo abra.
EXTENSIONES_DOCUMENTO = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
                         ".txt", ".md", ".csv", ".png", ".jpg", ".jpeg", ".zip"}
TAMANO_MAXIMO_DOCUMENTO = 10 * 1024 * 1024  # 10 MB


class DocumentoForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = DocumentoProyecto
        fields = ["nombre", "archivo"]

    def clean_archivo(self):
        archivo = self.cleaned_data["archivo"]
        extension = os.path.splitext(archivo.name)[1].lower()
        if extension not in EXTENSIONES_DOCUMENTO:
            raise ValidationError("Tipo de archivo no permitido. Usa PDF, Office, texto, imagen o ZIP.")
        if archivo.size > TAMANO_MAXIMO_DOCUMENTO:
            raise ValidationError("El archivo supera el máximo de 10 MB.")
        return archivo


class CorreccionForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Correccion
        fields = ["tarea", "comentario", "sugerencia_calificacion"]
        labels = {"sugerencia_calificacion": "Calificación sugerida (solo referencia)"}
        widgets = {"comentario": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, proyecto, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tarea"].queryset = proyecto.tareas.all()
        self.fields["tarea"].required = False
