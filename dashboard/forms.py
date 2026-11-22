from django import forms

from cuentas.forms import CampoFecha, FormularioBootstrap
from cuentas.models import Usuario

from .models import Proyecto, ProyectoMiembro, Tarea


class ProyectoForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ["nombre", "descripcion", "estado", "nivel_importancia", "tipo_proyecto", "fecha_inicio", "fecha_fin"]
        labels = {"nivel_importancia": "Importancia"}
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
        # Solo se puede asignar a quien trabaja en el proyecto
        self.fields["asignado_a"].queryset = proyecto.personas().order_by("first_name", "email")
        self.fields["asignado_a"].required = False


class MiembroForm(FormularioBootstrap, forms.Form):
    """Agregar a alguien al proyecto por su correo (puede ser de otra empresa)."""

    email = forms.EmailField(label="Correo de la persona", widget=forms.EmailInput(attrs={"placeholder": "persona@correo.com"}))
    rol = forms.ChoiceField(label="Rol en el proyecto", choices=ProyectoMiembro.RolProyecto.choices,
                            initial=ProyectoMiembro.RolProyecto.EDITOR)

    def __init__(self, *args, proyecto, **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto = proyecto

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        usuario = Usuario.objects.filter(email=email, is_active=True).first()
        if usuario is None:
            raise forms.ValidationError("No hay ninguna cuenta activa con ese correo. Pídele que se registre primero.")
        if usuario.pk == self.proyecto.creado_por_id:
            raise forms.ValidationError("Es quien creó el proyecto: ya tiene todos los permisos.")
        if self.proyecto.proyectomiembro_set.filter(usuario=usuario).exists():
            raise forms.ValidationError("Esa persona ya está en el proyecto.")
        self.usuario = usuario
        return email

    def save(self):
        return ProyectoMiembro.objects.create(proyecto=self.proyecto, usuario=self.usuario, rol=self.cleaned_data["rol"])
