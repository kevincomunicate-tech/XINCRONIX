"""
Publica el plan Scrum en GitHub usando GitHub CLI (gh).

Crea, a partir de docs/backlog.csv:
  * Milestones  -> un sprint cada uno (fecha de cierre + sprint goal)
  * Etiquetas   -> story points (sp:5), prioridad, épica, tipo y backlog
  * Issues      -> una historia de usuario cada uno, con su doliente
                   como assignee y su criterio de aceptación
  * Cierra los issues de los sprints ya terminados.
  * (Opcional) Un tablero de GitHub Projects con el campo "Story Points".

Se puede correr varias veces: lo que ya existe no se repite.

Uso (desde la raíz del proyecto):
    gh auth login
    python scripts/publicar_backlog.py --repo kevincomunicate-tech/XINCRONIX --simular
    python scripts/publicar_backlog.py --repo kevincomunicate-tech/XINCRONIX
    python scripts/publicar_backlog.py --repo kevincomunicate-tech/XINCRONIX --tablero

El tablero se crea en la cuenta de quien corre el script (@me). En la
cuenta personal de otra persona solo puede crearlo esa persona.

ANTES DE CORRERLO: pon los usuarios de GitHub de cada persona en DOLIENTES.
"""

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIGURA AQUÍ
# ---------------------------------------------------------------------------

# Usuario de GitHub de cada persona (deben ser colaboradores del repo).
# Si alguno está vacío, sus issues se crean sin assignee.
DOLIENTES = {
    "Yohan": "FIRE31690",
    "Felipe": "FelipeNavarrete0313",
    "Kevin": "kevincomunicate-tech",
}

SPRINTS = {
    "Sprint 1": {
        "titulo": "Sprint 1 — Base del proyecto y cuentas",
        "cierre": "2026-11-13",
        "goal": "Tener el proyecto Django funcionando con entorno virtual, y que un usuario pueda "
                "registrarse, iniciar sesión, cerrar sesión y recuperar su contraseña con el diseño "
                "original (claro y oscuro).",
        "terminado": True,
    },
    "Sprint 2": {
        "titulo": "Sprint 2 — Modelo de datos y panel",
        "cierre": "2026-11-20",
        "goal": "Reconstruir la base de datos normalizada (3FN) con trabajo en equipo en proyectos y "
                "canvas, y que el Panel muestre datos reales.",
        "terminado": True,
    },
    "Sprint 3": {
        "titulo": "Sprint 3 — Proyectos, tareas y analytics",
        "cierre": "2026-11-27",
        "goal": "Que el equipo pueda gestionar sus proyectos y tareas desde la aplicación (crear, "
                "asignar, mover en el Kanban) respetando los permisos, y ver el avance en Analytics.",
        "terminado": False,
    },
    "Sprint 4": {
        "titulo": "Sprint 4 — Colaboración, sitio y entrega",
        "cierre": "2026-12-01",
        "goal": "Completar el trabajo en equipo (ideas, canvas compartido, gestión de equipos), "
                "publicar el sitio y dejar el proyecto listo para desplegar y sustentar.",
        "terminado": False,
    },
}

NOMBRE_TABLERO = "Xincronix — Scrum"

# ---------------------------------------------------------------------------

COLORES = {
    "sp": "5319e7",
    "prioridad:must": "b60205",
    "prioridad:should": "d93f0b",
    "prioridad:could": "fbca04",
    "prioridad:wont": "cccccc",
    "epica": "1d76db",
    "tipo:historia": "0e8a16",
    "tipo:tarea-tecnica": "006b75",
    "backlog": "ededed",
}

SIMULAR = False


def gh(*args, salida_json=False, permitir_error=False):
    """Ejecuta un comando de gh (o solo lo muestra con --simular)."""
    comando = ["gh", *args]
    if SIMULAR and not _es_lectura(args):
        # Al simular, lo que crea o cambia algo solo se muestra
        print("     $ " + " ".join(_citar(a if len(a) < 80 else a[:77] + "...") for a in comando))
        return [] if salida_json else ""
    resultado = subprocess.run(comando, capture_output=True, text=True)
    if resultado.returncode != 0:
        if permitir_error:
            return None
        print(f"\n✖ Falló: {' '.join(comando)}\n{resultado.stderr.strip()}")
        sys.exit(1)
    texto = resultado.stdout.strip()
    return json.loads(texto) if salida_json and texto else texto


def _es_lectura(args):
    """Comandos que solo consultan: se ejecutan también al simular."""
    return (
        args[:2] in (("label", "list"), ("issue", "list"), ("auth", "status"))
        or (args[0] == "api" and "--method" not in args and not any(a.startswith("-f") for a in args))
    )


def _citar(texto):
    return f'"{texto}"' if (" " in texto or not texto) else texto


def slug(texto):
    reemplazos = str.maketrans("áéíóúñÁÉÍÓÚÑ ", "aeiounAEIOUN-")
    return texto.translate(reemplazos).lower()


def etiquetas_de(fila):
    puntos = fila["Story points"]
    prioridad = slug(fila["Prioridad"]).replace("'", "")
    tipo = "tipo:historia" if fila["Tipo"] == "Historia" else "tipo:tarea-tecnica"
    etiquetas = [f"sp:{puntos}", f"prioridad:{prioridad}", f"epica:{slug(fila['Épica'])}", tipo]
    if fila["Sprint"] == "Backlog":
        etiquetas.append("backlog")
    return etiquetas


def color_de(etiqueta):
    if etiqueta.startswith("sp:"):
        return COLORES["sp"]
    if etiqueta.startswith("epica:"):
        return COLORES["epica"]
    return COLORES.get(etiqueta, "c5def5")


def cuerpo_de(fila):
    doliente = fila["Doliente"] or "Sin asignar"
    criterio = fila["Criterio de aceptación"] or "Por definir en el refinamiento."
    return (
        f"**Historia:** {fila['Historia']} — {fila['Título']}\n\n"
        f"| Campo | Valor |\n|---|---|\n"
        f"| Épica | {fila['Épica']} |\n"
        f"| Sprint | {fila['Sprint']} |\n"
        f"| Story points | {fila['Story points']} |\n"
        f"| Doliente | {doliente} |\n"
        f"| Prioridad | {fila['Prioridad']} |\n\n"
        f"### Criterio de aceptación\n- [ ] {criterio}\n\n"
        f"### Definición de terminado\n"
        f"- [ ] Pruebas automáticas y `python manage.py test` pasa\n"
        f"- [ ] Funciona en modo claro, oscuro y móvil\n"
        f"- [ ] Respeta los permisos de trabajo en equipo\n"
        f"- [ ] Pull request revisado por otra persona\n\n"
        f"_Detalle completo en `docs/plan_sprints.md`._"
    )


def main():
    global SIMULAR
    parser = argparse.ArgumentParser(description="Publica el backlog de Xincronix en GitHub.")
    parser.add_argument("--repo", required=True, help="usuario/repositorio, ej. kevincomunicate-tech/XINCRONIX")
    parser.add_argument("--csv", default="docs/backlog.csv")
    parser.add_argument("--simular", action="store_true", help="Muestra lo que haría sin crear nada")
    parser.add_argument("--tablero", action="store_true", help="Crea también un tablero de GitHub Projects")
    parser.add_argument("--dueno-tablero", default="@me",
                        help="Cuenta donde se crea el tablero (por defecto, la de quien corre el script)")
    args = parser.parse_args()
    SIMULAR = args.simular
    repo = args.repo
    dueno = args.dueno_tablero

    filas = list(csv.DictReader(open(args.csv, encoding="utf-8-sig")))
    print(f"{'SIMULACIÓN — ' if SIMULAR else ''}Publicando {len(filas)} historias en {repo}\n")

    # 1. Etiquetas ---------------------------------------------------------
    print("1. Etiquetas")
    existentes = {e["name"] for e in (gh("label", "list", "--repo", repo, "--limit", "200",
                                         "--json", "name", salida_json=True) or [])}
    necesarias = sorted({e for f in filas for e in etiquetas_de(f)})
    for etiqueta in necesarias:
        if etiqueta in existentes:
            continue
        gh("label", "create", etiqueta, "--repo", repo, "--color", color_de(etiqueta), "--force")
    print(f"   {len(necesarias)} etiquetas listas\n")

    # 2. Milestones (sprints) ---------------------------------------------
    print("2. Sprints (milestones)")
    hitos = {m["title"]: m["number"] for m in (gh("api", f"repos/{repo}/milestones?state=all&per_page=100",
                                                   salida_json=True) or [])}
    for clave, sprint in SPRINTS.items():
        if sprint["titulo"] not in hitos:
            gh("api", f"repos/{repo}/milestones", "--method", "POST",
               "-f", f"title={sprint['titulo']}",
               "-f", f"description=Sprint goal: {sprint['goal']}",
               "-f", f"due_on={sprint['cierre']}T23:59:59Z")
        print(f"   {sprint['titulo']}  (cierra {sprint['cierre']})")
    print()

    # 3. Issues ------------------------------------------------------------
    print("3. Issues")
    ya_creados = {i["title"].split(" ")[0]: i for i in (gh("issue", "list", "--repo", repo, "--state", "all",
                                                          "--limit", "500", "--json", "title,number,state",
                                                          salida_json=True) or [])}
    sin_usuario = set()
    creados = {}
    for fila in filas:
        hu = fila["Historia"]
        titulo = f"{hu} {fila['Título']}"
        if hu in ya_creados:
            creados[hu] = ya_creados[hu]["number"]
            print(f"   = {titulo} (ya existe)")
            continue

        comando = ["issue", "create", "--repo", repo, "--title", titulo, "--body", cuerpo_de(fila)]
        for etiqueta in etiquetas_de(fila):
            comando += ["--label", etiqueta]
        if fila["Sprint"] in SPRINTS:
            comando += ["--milestone", SPRINTS[fila["Sprint"]]["titulo"]]

        personas = list(DOLIENTES) if fila["Doliente"] == "Todos" else [fila["Doliente"]] if fila["Doliente"] else []
        for persona in personas:
            usuario = DOLIENTES.get(persona, "")
            if usuario:
                comando += ["--assignee", usuario]
            else:
                sin_usuario.add(persona)

        url = gh(*comando, permitir_error=True)
        if url is None:  # suele ser un assignee que no es colaborador: se reintenta sin él
            comando = [c for i, c in enumerate(comando) if c != "--assignee" and (i == 0 or comando[i - 1] != "--assignee")]
            url = gh(*comando)
            print(f"   ! {titulo}: creado SIN assignee (¿el usuario es colaborador del repo?)")
        creados[hu] = int(url.rstrip("/").split("/")[-1]) if url else None
        print(f"   + {titulo}")

        if SPRINTS.get(fila["Sprint"], {}).get("terminado"):
            gh("issue", "close", url or titulo, "--repo", repo, "--reason", "completed")
    print()

    # 4. Tablero opcional ---------------------------------------------------
    if args.tablero:
        print("4. Tablero de GitHub Projects")
        print("   (si falla por permisos: gh auth refresh -s project)")
        proyecto = gh("project", "create", "--owner", dueno, "--title", NOMBRE_TABLERO,
                      "--format", "json", salida_json=True) or {"number": "N", "id": "PROJECT_ID"}
        numero = proyecto["number"]
        gh("project", "link", str(numero), "--owner", dueno, "--repo", repo, permitir_error=True)
        campo = gh("project", "field-create", str(numero), "--owner", dueno, "--name", "Story Points",
                   "--data-type", "NUMBER", "--format", "json", salida_json=True) or {"id": "FIELD_ID"}
        for fila in filas:
            numero_issue = creados.get(fila["Historia"])
            if not numero_issue:
                continue
            item = gh("project", "item-add", str(numero), "--owner", dueno,
                      "--url", f"https://github.com/{repo}/issues/{numero_issue}",
                      "--format", "json", salida_json=True) or {"id": "ITEM_ID"}
            gh("project", "item-edit", "--id", item["id"], "--project-id", proyecto["id"],
               "--field-id", campo["id"], "--number", fila["Story points"])
        print(f"   Tablero '{NOMBRE_TABLERO}' listo\n")

    if sin_usuario:
        print(f"⚠ Sin usuario de GitHub en DOLIENTES: {', '.join(sorted(sin_usuario))}. "
              "Sus issues quedaron sin assignee.")
    print("✔ Listo" if not SIMULAR else "✔ Simulación terminada: no se creó nada.")


if __name__ == "__main__":
    main()
