(function () {
  'use strict';
  var tablero = document.querySelector('.kanban');
  if (!tablero) return;
  var arrastrada = null;
  function token() {
    var m = document.cookie.match(/(?:^|; )csrftoken=([^;]*)/);
    return m ? decodeURIComponent(m[1]) : '';
  }
  function actualizarColumnas() {
    tablero.querySelectorAll('.kanban-column').forEach(function (columna) {
      var tarjetas = columna.querySelectorAll('.task-card').length;
      columna.querySelector('h2 span').textContent = tarjetas;
      var vacio = columna.querySelector('.kanban-empty');
      if (vacio) vacio.hidden = tarjetas > 0;
    });
  }
  function mover(tarjeta, estado) {
    var selector = tarjeta.querySelector('.task-status-select');
    var previo = tarjeta.closest('.kanban-column').dataset.estado;
    var destino = tablero.querySelector('.kanban-column[data-estado="' + estado + '"] .kanban-drop');
    if (!destino || estado === previo) return;
    var url = tablero.dataset.moveUrl.replace('/0/mover/', '/' + tarjeta.dataset.tarea + '/mover/');
    if (selector) selector.disabled = true;
    fetch(url, {method: 'POST', credentials: 'same-origin', headers: {'Content-Type': 'application/json', 'X-CSRFToken': token()}, body: JSON.stringify({estado: estado})})
      .then(function (r) { if (!r.ok) throw new Error(); return r.json(); })
      .then(function () { destino.appendChild(tarjeta); if (selector) { selector.value = estado; selector.dataset.original = estado; } actualizarColumnas(); })
      .catch(function () { if (selector) selector.value = previo; window.alert('No se pudo mover la tarea. Inténtalo de nuevo.'); })
      .finally(function () { if (selector) selector.disabled = false; });
  }
  tablero.querySelectorAll('.task-card[draggable="true"]').forEach(function (tarjeta) {
    tarjeta.addEventListener('dragstart', function () { arrastrada = tarjeta; tarjeta.classList.add('dragging'); });
    tarjeta.addEventListener('dragend', function () { tarjeta.classList.remove('dragging'); arrastrada = null; });
    tarjeta.querySelector('.task-status-select').addEventListener('change', function (e) { mover(tarjeta, e.target.value); });
  });
  tablero.querySelectorAll('.kanban-drop').forEach(function (destino) {
    destino.addEventListener('dragover', function (e) { e.preventDefault(); destino.classList.add('over'); });
    destino.addEventListener('dragleave', function () { destino.classList.remove('over'); });
    destino.addEventListener('drop', function (e) { e.preventDefault(); destino.classList.remove('over'); if (arrastrada) mover(arrastrada, destino.closest('.kanban-column').dataset.estado); });
  });
  actualizarColumnas();
})();
