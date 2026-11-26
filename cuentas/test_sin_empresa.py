"""Empresa fuera del proyecto por completo: modelos, tablas, columnas, rutas, código y /admin/."""

import re
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.db import connection
from django.test import Client, TestCase
from django.urls import get_resolver


class SinEmpresaTests(TestCase):
    def test_ningun_modelo_se_llama_empresa(self):
        nombres = [m._meta.object_name.lower() for m in apps.get_models()]
        self.assertFalse([n for n in nombres if "empresa" in n], nombres)

    def test_ninguna_tabla_de_la_base_es_de_empresa(self):
        tablas = connection.introspection.table_names()
        self.assertFalse([t for t in tablas if "empresa" in t.lower()], tablas)

    def test_ninguna_columna_se_llama_empresa(self):
        for modelo in apps.get_models():
            for campo in modelo._meta.concrete_fields:
                with self.subTest(modelo=modelo.__name__, campo=campo.name):
                    self.assertNotIn("empresa", (campo.name + campo.column).lower())

    def test_ninguna_ruta_menciona_empresa(self):
        nombres = [n for n in get_resolver().reverse_dict.keys() if isinstance(n, str)]
        self.assertFalse([n for n in nombres if "empresa" in n.lower()])

    def test_el_panel_de_django_ya_no_existe(self):
        self.assertEqual(Client().get("/admin/").status_code, 404)
        self.assertNotIn("django.contrib.admin", settings.INSTALLED_APPS)

    def test_el_codigo_y_la_documentacion_no_mencionan_empresa(self):
        raiz = Path(settings.BASE_DIR)
        extensiones = {".py", ".html", ".json", ".md", ".txt", ".css", ".js", ".example"}
        omitir = {".git", "__pycache__", "media", ".venv", "venv"}  # las migraciones también cuentan
        hallazgos = []
        for ruta in raiz.rglob("*"):
            if not ruta.is_file() or ruta.suffix not in extensiones or omitir & set(ruta.parts):
                continue
            if ruta.name == "test_sin_empresa.py":
                continue
            for numero, linea in enumerate(ruta.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if re.search(r"empresa", linea, re.IGNORECASE):
                    hallazgos.append(f"{ruta.relative_to(raiz)}:{numero}")
        self.assertEqual(hallazgos, [])
