from django.test import TestCase
from django.urls import reverse

from .models import Usuario


class RegistroTests(TestCase):
    def test_registro_crea_usuario(self):
        respuesta = self.client.post(reverse("registro"), {"nombre": "Ana Ruiz", "email": "ana@example.com", "perfil": "estudiante", "password": "ClaveSegura123"})
        self.assertRedirects(respuesta, reverse("panel"))
        self.assertEqual(Usuario.objects.get(email="ana@example.com").rol, Usuario.Rol.USUARIO)
