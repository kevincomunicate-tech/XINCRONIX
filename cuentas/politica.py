"""
Política de roles y accesos de Xincronix.

Las REGLAS viven en config/politica_accesos.json (settings.POLITICA_ACCESOS).
Este módulo solo las lee, las valida y responde preguntas como:

    politica = obtener_politica()
    politica.perfil_de(usuario)                -> "superadministrador", "admin", "usuario"...
    politica.roles_asignables(usuario)         -> ["admin", "manager", ...]
    politica.puede(usuario, "crear_empresa")   -> True / False
    politica.permisos_empresa(usuario, e)      -> {"ver", "editar", ...}
    politica.permisos_proyecto(usuario, p)     -> {"ver", "tareas", ...}
    politica.url_inicio(usuario)               -> "/administracion/" o "/app/"
    politica.perfiles_permitidos(ruta)         -> quién puede entrar a esa ruta

Así ninguna vista tiene correos ni roles escritos a mano: si cambia una regla,
se edita el JSON y el código queda igual.
"""

import json
from dataclasses import dataclass
from functools import lru_cache
from itertools import chain
from pathlib import Path

from django.conf import settings
from django.urls import reverse

SUPERADMINISTRADOR = "superadministrador"
ANONIMO = "anonimo"

CLAVES_OBLIGATORIAS = (
    "superadministradores", "roles", "registro", "perfiles", "empresas", "proyectos", "rutas_restringidas",
)

# Vocabulario que el código sabe interpretar. El JSON decide QUIÉN tiene cada cosa.
ACCIONES = {"editar_cuenta", "eliminar_cuenta", "crear_empresa", "crear_proyecto"}
SECCIONES = {
    # sección del JSON: (relaciones posibles, permisos posibles)
    "empresas": ({"propietario", "integrante"}, {"ver", "editar", "eliminar", "metricas"}),
    "proyectos": (
        {"creador", "responsable", "editor", "observador", "equipo"},
        {"ver", "editar", "eliminar", "miembros", "tareas"},
    ),
}
# "alcance" de un permiso por perfil: ¿sobre qué empresas aplica?
ALCANCES = {
    "todas": lambda usuario, empresa_id: True,
    "empresa": lambda usuario, empresa_id: usuario.empresa_id is not None and usuario.empresa_id == empresa_id,
}


class PoliticaInvalida(Exception):
    """El JSON de la política tiene errores. Trae la lista de problemas."""

    def __init__(self, errores):
        self.errores = errores
        super().__init__("Política de accesos inválida:\n- " + "\n- ".join(errores))


# ---------------------------------------------------------------------------
# Validación del JSON
# ---------------------------------------------------------------------------

def validar(datos):
    """Devuelve la lista de errores del JSON (vacía si está bien).

    Cada regla es un par (hay_error, mensaje): se juntan todas y se devuelven
    los mensajes de las que fallan. Así se ven todas las reglas de un vistazo.
    """
    faltan = [clave for clave in CLAVES_OBLIGATORIAS if clave not in datos]
    if faltan:
        return [f"Falta la clave obligatoria '{clave}'." for clave in faltan]

    roles = set(datos["roles"])
    perfiles = set(datos["perfiles"])
    esperados = roles | {SUPERADMINISTRADOR}
    rol_registro = datos["registro"].get("rol")

    reglas = []
    reglas += [
        (correo != correo.strip().lower() or "@" not in correo,
         f"El correo '{correo}' de 'superadministradores' debe ir en minúsculas y sin espacios.")
        for correo in datos["superadministradores"]
    ]
    reglas += [
        (not rol.get("nombre"), f"El rol '{codigo}' de 'roles' necesita 'nombre'.")
        for codigo, rol in datos["roles"].items()
    ]
    reglas += [(rol_registro not in roles, f"'registro.rol' es '{rol_registro}', que no existe en 'roles'.")]
    reglas += [(True, f"Falta el perfil '{p}' en 'perfiles'.") for p in sorted(esperados - perfiles)]
    reglas += [(True, f"El perfil '{p}' no es un rol ni 'superadministrador'.") for p in sorted(perfiles - esperados)]

    for nombre, perfil in datos["perfiles"].items():
        reglas += [(not perfil.get("inicio"), f"El perfil '{nombre}' necesita 'inicio'.")]
        reglas += [
            (codigo not in roles, f"El perfil '{nombre}' puede asignar '{codigo}', que no existe en 'roles'.")
            for codigo in perfil.get("puede_asignar", [])
        ]
        reglas += [
            (not (item.get("texto") and item.get("url")), f"Un elemento del menú de '{nombre}' necesita 'texto' y 'url'.")
            for item in perfil.get("menu", [])
        ]
        reglas += [
            (accion not in ACCIONES, f"El perfil '{nombre}' tiene la acción '{accion}', que no existe. Usa: {', '.join(sorted(ACCIONES))}.")
            for accion in perfil.get("acciones", [])
        ]

    for seccion, (relaciones, permisos) in SECCIONES.items():
        reglas += _validar_permisos(seccion, datos[seccion], relaciones, permisos, perfiles)

    for ruta, permitidos in datos["rutas_restringidas"].items():
        reglas += [(not (ruta.startswith("/") and ruta.endswith("/")), f"La ruta '{ruta}' debe empezar y terminar en '/'.")]
        reglas += [
            (p not in perfiles, f"La ruta '{ruta}' permite el perfil '{p}', que no existe en 'perfiles'.")
            for p in permitidos
        ]

    return [mensaje for hay_error, mensaje in reglas if hay_error]


def _validar_permisos(seccion, datos, relaciones, permisos, perfiles):
    """Reglas de 'empresas' o 'proyectos': relaciones, perfiles, alcances y permisos conocidos."""
    por_relacion = datos.get("por_relacion", {})
    por_perfil = datos.get("por_perfil", {})
    reglas = [(True, f"'{seccion}.por_relacion' usa la relación '{r}', que no existe. Usa: {', '.join(sorted(relaciones))}.")
              for r in sorted(set(por_relacion) - relaciones)]
    reglas += [(True, f"'{seccion}.por_perfil' usa el perfil '{p}', que no existe en 'perfiles'.")
               for p in sorted(set(por_perfil) - perfiles)]
    reglas += [(regla.get("alcance") not in ALCANCES,
                f"'{seccion}.por_perfil.{p}.alcance' debe ser uno de: {', '.join(sorted(ALCANCES))}.")
               for p, regla in por_perfil.items()]
    usados = chain(
        ((f"por_relacion.{r}", lista) for r, lista in por_relacion.items()),
        ((f"por_perfil.{p}", regla.get("permisos", [])) for p, regla in por_perfil.items()),
    )
    reglas += [(permiso not in permisos, f"'{seccion}.{donde}' tiene el permiso '{permiso}', que no existe. Usa: {', '.join(sorted(permisos))}.")
               for donde, lista in usados for permiso in lista]
    return reglas


# ---------------------------------------------------------------------------
# La política ya leída
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Politica:
    superadministradores: frozenset
    roles: dict
    registro: dict
    perfiles: dict
    empresas: dict
    proyectos: dict
    rutas_restringidas: dict

    # --- ¿Quién es esta persona? ---

    def es_superadministrador(self, usuario):
        """Debe estar en la lista del JSON Y ser superusuario activo.

        Pedir las dos cosas evita que alguien obtenga el poder solo por
        registrarse con ese correo (por ejemplo, si la cuenta se borrara).
        """
        return (
            usuario.is_authenticated
            and usuario.is_active
            and usuario.is_superuser
            and usuario.email.lower() in self.superadministradores
        )

    def perfil_de(self, usuario):
        if not usuario.is_authenticated:
            return ANONIMO
        if self.es_superadministrador(usuario):
            return SUPERADMINISTRADOR
        return usuario.rol.codigo if usuario.rol_id else self.rol_registro

    # --- ¿Qué puede hacer? ---

    def roles_asignables(self, usuario):
        return list(self.perfiles.get(self.perfil_de(usuario), {}).get("puede_asignar", []))

    def puede_asignar(self, usuario, codigo_rol):
        return codigo_rol in self.roles_asignables(usuario)

    def puede(self, usuario, accion):
        """Acciones generales del perfil (perfiles.<perfil>.acciones)."""
        return accion in self._perfil(usuario).get("acciones", [])

    def permisos_empresa(self, usuario, empresa):
        return self._permisos(self.empresas, usuario, empresa.relaciones_con(usuario), empresa.pk)

    def permisos_proyecto(self, usuario, proyecto):
        return self._permisos(self.proyectos, usuario, proyecto.relaciones_con(usuario), proyecto.empresa_id)

    def criterios_para_ver(self, seccion, usuario):
        """Para filtrar listas en la base de datos (ej. proyectos visibles).

        Devuelve (relaciones, alcance): las relaciones que dan "ver" y el
        alcance del perfil si este también da "ver" (o None).
        """
        datos = getattr(self, seccion)
        relaciones = [r for r, permisos in datos["por_relacion"].items() if "ver" in permisos]
        regla = datos["por_perfil"].get(self.perfil_de(usuario), {})
        alcance = regla.get("alcance") if "ver" in regla.get("permisos", []) else None
        return relaciones, alcance

    def _permisos(self, seccion, usuario, relaciones, empresa_id):
        """Une los permisos de cada relación con los del perfil (si su alcance aplica)."""
        if not usuario.is_authenticated:
            return frozenset()
        por_relacion = [seccion["por_relacion"].get(r, []) for r in relaciones]
        regla = seccion["por_perfil"].get(self.perfil_de(usuario), {"alcance": "todas", "permisos": []})
        por_perfil = regla["permisos"] if ALCANCES[regla["alcance"]](usuario, empresa_id) else []
        return frozenset(chain(por_perfil, *por_relacion))

    def _perfil(self, usuario):
        return self.perfiles.get(self.perfil_de(usuario), {})

    # --- ¿A dónde va? ---

    def url_inicio(self, usuario):
        perfil = self.perfiles.get(self.perfil_de(usuario), self.perfiles[self.rol_registro])
        return reverse(perfil["inicio"])

    def menu(self, usuario, ruta_actual=""):
        """Enlaces extra del menú para ese perfil, ya con su URL resuelta.

        Queda "activo" el enlace cuya URL coincide con la ruta actual en más
        caracteres (así /administracion/empresas/ no marca también "Usuarios").
        """
        items = [{**item, "href": reverse(item["url"])} for item in self._perfil(usuario).get("menu", [])]
        coinciden = [item["href"] for item in items if ruta_actual.startswith(item["href"])]
        activo = max(coinciden, key=len, default=None)
        return [{**item, "activo": item["href"] == activo} for item in items]

    def perfiles_permitidos(self, ruta):
        """Perfiles que pueden entrar a una ruta, o None si la ruta es libre."""
        coincidencias = [prefijo for prefijo in self.rutas_restringidas if ruta.startswith(prefijo)]
        mas_especifica = max(coincidencias, key=len, default=None)
        return self.rutas_restringidas.get(mas_especifica)

    # --- Datos para el registro ---

    @property
    def rol_registro(self):
        return self.registro["rol"]

    @property
    def crear_empresa_propia(self):
        return bool(self.registro.get("crear_empresa_propia", False))


def leer_politica(ruta):
    """Lee y valida el JSON. Lanza PoliticaInvalida si tiene errores."""
    try:
        datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise PoliticaInvalida([f"No existe el archivo {ruta}."])
    except json.JSONDecodeError as error:
        raise PoliticaInvalida([f"{Path(ruta).name} no es un JSON válido: {error}"])

    errores = validar(datos)
    if errores:
        raise PoliticaInvalida(errores)

    return Politica(
        superadministradores=frozenset(datos["superadministradores"]),
        roles=datos["roles"],
        registro=datos["registro"],
        perfiles=datos["perfiles"],
        empresas=datos["empresas"],
        proyectos=datos["proyectos"],
        rutas_restringidas={ruta: frozenset(p) for ruta, p in datos["rutas_restringidas"].items()},
    )


@lru_cache(maxsize=1)
def obtener_politica():
    """La política del proyecto. Se lee una sola vez (reinicia runserver si editas el JSON)."""
    return leer_politica(settings.POLITICA_ACCESOS)
