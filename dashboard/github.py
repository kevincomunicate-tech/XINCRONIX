"""
Consulta de repositorios con la API REST de GitHub.

* Sin token se ven repositorios públicos (GitHub permite 60 consultas por hora
  por IP). Con GITHUB_TOKEN en .env el límite sube y se ven también los privados
  a los que el token tenga acceso.
* Las respuestas se guardan 10 minutos en la caché de Django para no gastar el
  límite cada vez que alguien abre la página.
* Se usa `requests`, que ya está en requirements.txt.
"""

import re
from datetime import datetime
from urllib.parse import urlparse

from django.conf import settings
from django.core.cache import cache

import requests

API = "https://api.github.com"
# Versión de la API fijada a propósito: los endpoints que se usan aquí son básicos y estables.
VERSION_API = "2022-11-28"
TIEMPO_MAXIMO = 10
CACHE_SEGUNDOS = 600
NOMBRE_VALIDO = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,99})$")


class GitHubError(Exception):
    """Error con un mensaje que se puede mostrar tal cual a la persona."""


def analizar_url(url):
    """
    De un enlace de GitHub saca (dueño, repositorio). El repositorio es None si el
    enlace es de un usuario u organización. Devuelve None si no es de GitHub.

    Acepta: https://github.com/dueño, https://github.com/dueño/repo,
    .../repo.git, .../repo/tree/main/... y www.github.com.
    """
    if not url:
        return None
    try:
        partes = urlparse(url.strip())
    except ValueError:
        return None
    if partes.scheme not in ("http", "https") or (partes.hostname or "").lower() not in ("github.com", "www.github.com"):
        return None
    segmentos = [s for s in partes.path.split("/") if s]
    if not segmentos or not NOMBRE_VALIDO.match(segmentos[0]):
        return None
    dueno = segmentos[0]
    if len(segmentos) == 1:
        return dueno, None
    repo = segmentos[1][:-4] if segmentos[1].endswith(".git") else segmentos[1]
    if not NOMBRE_VALIDO.match(repo):
        return None
    return dueno, repo


def nombre_valido(nombre):
    return bool(nombre and NOMBRE_VALIDO.match(nombre))


def _encabezados(token):
    encabezados = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": VERSION_API, "User-Agent": "Xincronix"}
    if token:
        encabezados["Authorization"] = f"Bearer {token}"
    return encabezados


def _mensaje_error(respuesta, con_token):
    codigo = respuesta.status_code
    if codigo == 401:
        return "GitHub rechazó el token. Revisa GITHUB_TOKEN en el archivo .env."
    if codigo in (403, 429) and respuesta.headers.get("X-RateLimit-Remaining") == "0":
        return "Se alcanzó el límite de consultas a GitHub. Intenta más tarde."
    if codigo == 404:
        if not con_token:
            return "No se encontró en GitHub. Si el repositorio es privado, solicítale acceso al administrador."
        return "No se encontró en GitHub: revisa el enlace y el acceso del token."
    if codigo >= 500:
        return "GitHub no está respondiendo en este momento. Intenta más tarde."
    return "GitHub no pudo responder la consulta."


def _get(ruta, params=None, *, token=''):
    clave = "github:publico:" + ruta + ":" + "&".join(f"{k}={v}" for k, v in sorted((params or {}).items()))
    guardado = None if token else cache.get(clave)
    if guardado is not None:
        return guardado
    try:
        respuesta = requests.get(API + ruta, params=params, headers=_encabezados(token), timeout=TIEMPO_MAXIMO)
    except requests.Timeout:
        raise GitHubError("GitHub tardó demasiado en responder. Intenta de nuevo.")
    except requests.RequestException:
        raise GitHubError("No hay conexión con GitHub. Revisa la conexión a internet del servidor.")
    if respuesta.status_code == 409:  # repositorio vacío: no tiene commits
        datos = []
    elif respuesta.status_code != 200:
        raise GitHubError(_mensaje_error(respuesta, bool(token)))
    else:
        try:
            datos = respuesta.json()
        except ValueError:
            raise GitHubError("GitHub devolvió una respuesta que no se pudo leer.")
    if not token:
        cache.set(clave, datos, CACHE_SEGUNDOS)
    return datos


def _fecha(texto):
    try:
        return datetime.fromisoformat(texto.replace("Z", "+00:00")) if texto else None
    except ValueError:
        return None


def repositorio(dueno, repo, *, usar_token=False):
    """Datos de un repositorio: información general, lenguajes y últimos commits."""
    token = settings.GITHUB_TOKEN if usar_token else ""
    info = _get(f"/repos/{dueno}/{repo}", token=token)
    lenguajes = _get(f"/repos/{dueno}/{repo}/languages", token=token) or {}
    total = sum(lenguajes.values()) or 1
    commits = _get(f"/repos/{dueno}/{repo}/commits", {"per_page": 6}, token=token) or []
    return {
        "nombre": info.get("full_name") or f"{dueno}/{repo}",
        "descripcion": info.get("description") or "",
        "url": info.get("html_url") or f"https://github.com/{dueno}/{repo}",
        "privado": bool(info.get("private")),
        "estrellas": info.get("stargazers_count", 0),
        "forks": info.get("forks_count", 0),
        "issues": info.get("open_issues_count", 0),  # GitHub cuenta aquí issues y pull requests abiertos
        "rama": info.get("default_branch") or "",
        "licencia": (info.get("license") or {}).get("name") or "",
        "actualizado": _fecha(info.get("pushed_at")),
        "lenguajes": [
            {"nombre": nombre, "porcentaje": round(bytes_ * 100 / total, 1)}
            for nombre, bytes_ in sorted(lenguajes.items(), key=lambda par: -par[1])[:6]
        ],
        "commits": [
            {
                "sha": (c.get("sha") or "")[:7],
                "mensaje": ((c.get("commit") or {}).get("message") or "").split("\n")[0][:120],
                "autor": ((c.get("commit") or {}).get("author") or {}).get("name") or (c.get("author") or {}).get("login") or "—",
                # Fecha en que el commit entró al repositorio (committer); la del autor puede ser
                # mucho más vieja si el commit se rebasó o se aplicó después, y desordena la lista.
                "fecha": _fecha(((c.get("commit") or {}).get("committer") or {}).get("date")
                                or ((c.get("commit") or {}).get("author") or {}).get("date")),
                "url": c.get("html_url") or "",
            }
            for c in commits
        ],
    }


def repositorios_de(dueno):
    """Repositorios públicos de un usuario u organización, del más reciente al más antiguo."""
    datos = _get(f"/users/{dueno}/repos", {"sort": "pushed", "per_page": 30})
    return [
        {
            "nombre": r.get("name") or "",
            "descripcion": r.get("description") or "",
            "lenguaje": r.get("language") or "",
            "estrellas": r.get("stargazers_count", 0),
            "actualizado": _fecha(r.get("pushed_at")),
            "fork": bool(r.get("fork")),
        }
        for r in datos if r.get("name")
    ]
