/* =========================================================
   XINCRONIX — Login, registro y recuperar contraseña

   Solo mejora la experiencia en el navegador: la validación
   real la hace Django en el servidor (cuentas/forms.py).
   ========================================================= */

(function () {
  'use strict';

  // Mostrar / ocultar contraseña
  document.querySelectorAll('[data-toggle-pwd]').forEach(function (boton) {
    boton.addEventListener('click', function () {
      var input = boton.parentElement.querySelector('input');
      var ver = input.type === 'password';
      input.type = ver ? 'text' : 'password';
      boton.querySelector('i').className = ver ? 'bi bi-eye-slash' : 'bi bi-eye';
      boton.title = ver ? 'Ocultar contraseña' : 'Ver contraseña';
    });
  });

  // Al volver a escribir, se quita el error de ese campo
  document.querySelectorAll('.field.has-error input').forEach(function (input) {
    input.addEventListener('input', function () {
      input.closest('.field').classList.remove('has-error');
    });
  });

  // Indicador de fortaleza de la contraseña
  var NIVELES = [
    { texto: 'Muy débil', color: '#d63d58', ancho: '20%' },
    { texto: 'Débil', color: '#e8833a', ancho: '40%' },
    { texto: 'Aceptable', color: '#d9a21b', ancho: '60%' },
    { texto: 'Buena', color: '#2a5bff', ancho: '80%' },
    { texto: 'Fuerte', color: '#1f9d68', ancho: '100%' }
  ];

  document.querySelectorAll('[data-fortaleza]').forEach(function (caja) {
    var input = caja.closest('.field').querySelector('input');
    var barra = caja.querySelector('.pwd-strength-fill');
    var texto = caja.querySelector('.pwd-strength-text');

    input.addEventListener('input', function () {
      var v = input.value;
      caja.classList.toggle('show', v.length > 0);
      var puntos = 0;
      if (v.length >= 8) puntos++;
      if (v.length >= 12) puntos++;
      if (/[a-z]/.test(v) && /[A-Z]/.test(v)) puntos++;
      if (/\d/.test(v)) puntos++;
      if (/[^A-Za-z0-9]/.test(v)) puntos++;
      var nivel = NIVELES[Math.max(0, Math.min(4, puntos - 1))];
      barra.style.width = v.length ? nivel.ancho : '0';
      barra.style.background = nivel.color;
      texto.textContent = v.length < 8 ? 'Mínimo 8 caracteres' : nivel.texto;
    });
  });

  // Estado "cargando" del botón al enviar
  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function () {
      var boton = form.querySelector('.btn-login');
      if (boton) boton.classList.add('loading');
    });
  });
})();
