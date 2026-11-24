/* =========================================================
   XINCRONIX — CAMBIO DE TEMA (claro / oscuro)

   - El tema claro es el predeterminado.
   - Cualquier botón con el atributo  data-theme-toggle
     cambia entre los dos temas.
   - La elección se guarda en el navegador y se comparte
     entre todas las páginas que cargan este archivo.
   - Cárgalo dentro de <head> (sin defer) para que la
     página no parpadee en claro antes de pintarse oscura.
   ========================================================= */

(function () {
  var CLAVE = 'xnx-tema';
  var raiz = document.documentElement;

  function leer() {
    try { return localStorage.getItem(CLAVE); } catch (e) { return null; }
  }

  function guardar(valor) {
    try { localStorage.setItem(CLAVE, valor); } catch (e) { /* modo privado */ }
  }

  function actualizarBotones(tema) {
    var oscuro = tema === 'dark';
    document.querySelectorAll('[data-theme-toggle]').forEach(function (boton) {
      boton.setAttribute('aria-pressed', oscuro ? 'true' : 'false');
      boton.setAttribute('title', oscuro ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro');

      var icono = boton.querySelector('.theme-toggle-icon');
      var texto = boton.querySelector('.theme-toggle-text');
      if (icono) {
        // Icono de Bootstrap Icons: luna en claro, sol en oscuro
        icono.classList.remove('bi-moon-stars-fill', 'bi-sun-fill');
        icono.classList.add('bi', oscuro ? 'bi-sun-fill' : 'bi-moon-stars-fill');
        icono.textContent = '';
      }
      if (texto) texto.textContent = oscuro ? 'Modo claro' : 'Modo oscuro';
    });
  }

  function aplicar(tema) {
    raiz.setAttribute('data-theme', tema);
    raiz.setAttribute('data-bs-theme', tema); // Bootstrap 5.3 (modales, formularios)
    raiz.style.colorScheme = tema === 'dark' ? 'dark' : 'light';
    actualizarBotones(tema);
  }

  // Se aplica de inmediato, antes de que se pinte la página
  aplicar(leer() === 'dark' ? 'dark' : 'light');

  document.addEventListener('DOMContentLoaded', function () {
    actualizarBotones(raiz.getAttribute('data-theme'));

    document.addEventListener('click', function (evento) {
      var boton = evento.target.closest('[data-theme-toggle]');
      if (!boton) return;

      var nuevo = raiz.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      aplicar(nuevo);
      guardar(nuevo);

      // Avisa a la página por si necesita repintar algo (gráficos, etc.)
      document.dispatchEvent(new CustomEvent('xnx:tema', { detail: { tema: nuevo } }));
    });
  });

  // Si el tema cambia en otra pestaña, esta también se actualiza
  window.addEventListener('storage', function (evento) {
    if (evento.key === CLAVE) aplicar(evento.newValue === 'dark' ? 'dark' : 'light');
  });
})();
