"""Red de seguridad a nivel de modelo: el último superusuario activo no se puede
borrar ni desactivar ni quitarle el permiso, por ninguna vía (vistas, consola,
borrados en lote o scripts). Las vistas dan un mensaje claro antes; esto es el respaldo."""

from django.db import transaction
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from .models import Usuario
from .models import MENSAJE_ULTIMO_SUPERUSUARIO, SuperusuarioProtegido
from .servicios import bloquear_superusuarios, otros_superusuarios_activos


@receiver(pre_save, sender=Usuario)
def proteger_ultimo_superusuario_al_guardar(sender, instance, update_fields=None, **kwargs):
    if instance.pk is None:
        return  # crear una cuenta nunca quita superusuarios
    if update_fields is not None and not {"is_active", "is_superuser"} & set(update_fields):
        return  # p. ej. last_login al iniciar sesión: no cambia permisos
    with transaction.atomic():
        bloquear_superusuarios()
        antes = Usuario.objects.filter(pk=instance.pk).only("is_superuser", "is_active").first()
        if antes is None:
            return
        perdia_el_permiso = antes.is_superuser and antes.is_active and not (instance.is_superuser and instance.is_active)
        if perdia_el_permiso and not otros_superusuarios_activos(instance.pk).exists():
            raise SuperusuarioProtegido(MENSAJE_ULTIMO_SUPERUSUARIO)


@receiver(pre_delete, sender=Usuario)
def proteger_ultimo_superusuario_al_borrar(sender, instance, **kwargs):
    # Django ya borra dentro de una transacción: el bloqueo corre dentro de ella.
    bloquear_superusuarios()
    if instance.is_superuser and instance.is_active and not otros_superusuarios_activos(instance.pk).exists():
        raise SuperusuarioProtegido(MENSAJE_ULTIMO_SUPERUSUARIO)
