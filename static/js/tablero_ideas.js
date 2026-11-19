/* =========================================================
   XINCRONIX — TABLERO DE IDEAS

   Por ahora las ideas se guardan en el navegador
   (localStorage). Para conectarlo a tu backend, cambia solo
   las funciones  cargarIdeas()  y  guardarIdeas()  por
   llamadas fetch a tu API; el resto del archivo no cambia.
   ========================================================= */

(function () {
  'use strict';

  var CLAVE_IDEAS = 'xnx-ideas';
  var CLAVE_VOTOS = 'xnx-ideas-votos';

  var ESTADOS = ['nueva', 'evaluacion', 'aprobada', 'archivada'];
  var NOMBRE_ESTADO = {
    nueva: 'Nuevas',
    evaluacion: 'En evaluación',
    aprobada: 'Aprobadas',
    archivada: 'Archivadas'
  };

  /* Ideas de ejemplo: solo aparecen la primera vez */
  var EJEMPLOS = [
    { titulo: 'Plantillas de proyecto reutilizables', descripcion: 'Guardar un proyecto como plantilla con sus tareas y fases para no armarlo desde cero cada vez.', categoria: 'Producto', estado: 'evaluacion', color: 'azul', autor: 'Laura Méndez', votos: 12 },
    { titulo: 'Resumen semanal automático por correo', descripcion: 'Que el asistente envíe cada lunes un resumen de avances, tareas vencidas y bloqueos de cada equipo.', categoria: 'Tecnología', estado: 'aprobada', color: 'verde', autor: 'Andrés Ruiz', votos: 18 },
    { titulo: 'Encuesta de satisfacción al cerrar un proyecto', descripcion: 'Enviar una encuesta corta al cliente cuando el proyecto pasa a "Hecho" para medir la experiencia.', categoria: 'Clientes', estado: 'nueva', color: 'rosa', autor: 'Camila Torres', votos: 7 },
    { titulo: 'Reunión diaria de 10 minutos', descripcion: 'Bloque fijo en el calendario para revisar prioridades del día en cada equipo.', categoria: 'Procesos', estado: 'nueva', color: 'amarillo', autor: 'Julián Gómez', votos: 4 },
    { titulo: 'Programa de mentorías internas', descripcion: 'Emparejar personas nuevas con alguien con experiencia durante sus primeros 3 meses.', categoria: 'Equipo', estado: 'evaluacion', color: 'morado', autor: 'Sara Pineda', votos: 9 },
    { titulo: 'App de escritorio sin conexión', descripcion: 'Versión que funcione sin internet y sincronice al reconectar.', categoria: 'Tecnología', estado: 'archivada', color: 'azul', autor: 'Mateo Rojas', votos: 2 }
  ];

  var ideas = [];
  var misVotos = {};
  var filtro = { texto: '', categoria: '', orden: 'votos' };
  var idArrastrado = null;

  var el = {
    board: document.getElementById('ideasBoard'),
    buscar: document.getElementById('buscarIdea'),
    filtros: document.getElementById('filtrosCategoria'),
    orden: document.getElementById('ordenIdeas'),
    sub: document.getElementById('topbarSub'),
    form: document.getElementById('formIdea'),
    modalTitulo: document.getElementById('modalIdeaTitulo'),
    id: document.getElementById('ideaId'),
    titulo: document.getElementById('ideaTitulo'),
    descripcion: document.getElementById('ideaDescripcion'),
    categoria: document.getElementById('ideaCategoria'),
    estado: document.getElementById('ideaEstado'),
    autor: document.getElementById('ideaAutor'),
    btnEliminar: document.getElementById('btnEliminarIdea'),
    toastBody: document.getElementById('ideasToastBody')
  };

  var modal = new bootstrap.Modal(document.getElementById('modalIdea'));
  var toast = new bootstrap.Toast(document.getElementById('ideasToast'), { delay: 2200 });


  /* ---------- Guardado ---------- */

  function leerJSON(clave, porDefecto) {
    try {
      var valor = JSON.parse(localStorage.getItem(clave));
      return valor == null ? porDefecto : valor;
    } catch (e) {
      return porDefecto;
    }
  }

  function escribirJSON(clave, valor) {
    try { localStorage.setItem(clave, JSON.stringify(valor)); } catch (e) { /* sin almacenamiento */ }
  }

  function cargarIdeas() {
    var guardadas = leerJSON(CLAVE_IDEAS, null);
    if (Array.isArray(guardadas)) return guardadas;

    var ahora = Date.now();
    return EJEMPLOS.map(function (idea, i) {
      return Object.assign({ id: nuevoId(), creada: ahora - i * 86400000 }, idea);
    });
  }

  function guardarIdeas() {
    escribirJSON(CLAVE_IDEAS, ideas);
    escribirJSON(CLAVE_VOTOS, misVotos);
  }


  /* ---------- Utilidades ---------- */

  function nuevoId() {
    return 'i' + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  }

  function escapar(texto) {
    var div = document.createElement('div');
    div.textContent = texto == null ? '' : String(texto);
    return div.innerHTML;
  }

  function iniciales(nombre) {
    var partes = String(nombre || '').trim().split(/\s+/).filter(Boolean);
    if (!partes.length) return '?';
    return (partes[0][0] + (partes.length > 1 ? partes[partes.length - 1][0] : '')).toUpperCase();
  }

  function fechaCorta(ms) {
    return new Date(ms).toLocaleDateString('es-CO', { day: '2-digit', month: 'short' });
  }

  function buscarIdea(id) {
    for (var i = 0; i < ideas.length; i++) if (ideas[i].id === id) return ideas[i];
    return null;
  }

  function avisar(mensaje) {
    el.toastBody.textContent = mensaje;
    toast.show();
  }


  /* ---------- Pintar ---------- */

  function coincide(idea) {
    if (filtro.categoria && idea.categoria !== filtro.categoria) return false;
    if (!filtro.texto) return true;
    var texto = (idea.titulo + ' ' + idea.descripcion + ' ' + idea.autor).toLowerCase();
    return texto.indexOf(filtro.texto) !== -1;
  }

  function ordenar(a, b) {
    if (filtro.orden === 'recientes') return b.creada - a.creada;
    return (b.votos - a.votos) || (b.creada - a.creada);
  }

  function tarjeta(idea) {
    var votada = !!misVotos[idea.id];
    return '' +
      '<article class="idea-card" draggable="true" data-id="' + idea.id + '" data-color="' + escapar(idea.color) + '">' +
        '<div class="idea-card-top">' +
          '<span class="idea-tag">' + escapar(idea.categoria) + '</span>' +
          '<div class="idea-actions">' +
            '<button type="button" class="idea-icon-btn" data-accion="editar" title="Editar" aria-label="Editar idea"><i class="bi bi-pencil"></i></button>' +
            '<button type="button" class="idea-icon-btn danger" data-accion="eliminar" title="Eliminar" aria-label="Eliminar idea"><i class="bi bi-trash"></i></button>' +
          '</div>' +
        '</div>' +
        '<h3 class="idea-title">' + escapar(idea.titulo) + '</h3>' +
        (idea.descripcion ? '<p class="idea-desc">' + escapar(idea.descripcion) + '</p>' : '') +
        '<div class="idea-footer">' +
          '<div class="idea-author" title="' + escapar(idea.autor) + ' · ' + fechaCorta(idea.creada) + '">' +
            '<span class="xnx-avatar sm">' + escapar(iniciales(idea.autor)) + '</span>' +
            '<span>' + escapar(idea.autor || 'Anónimo') + '</span>' +
          '</div>' +
          '<button type="button" class="idea-vote' + (votada ? ' voted' : '') + '" data-accion="votar" aria-pressed="' + votada + '" title="' + (votada ? 'Quitar voto' : 'Votar esta idea') + '">' +
            '<i class="bi bi-hand-thumbs-up' + (votada ? '-fill' : '') + '"></i> ' + idea.votos +
          '</button>' +
        '</div>' +
      '</article>';
  }

  function pintar() {
    var visibles = ideas.filter(coincide).sort(ordenar);

    ESTADOS.forEach(function (estado) {
      var col = el.board.querySelector('.ideas-col[data-estado="' + estado + '"]');
      var lista = col.querySelector('.ideas-list');
      var deEstado = visibles.filter(function (i) { return i.estado === estado; });

      col.querySelector('.ideas-col-count').textContent = deEstado.length;
      lista.innerHTML = deEstado.length
        ? deEstado.map(tarjeta).join('')
        : '<div class="ideas-empty"><i class="bi bi-lightbulb"></i>' +
          (filtro.texto || filtro.categoria ? 'Sin resultados' : 'Arrastra una idea aquí') + '</div>';
    });

    pintarResumen();
  }

  function pintarResumen() {
    var contar = function (estado) {
      return ideas.filter(function (i) { return i.estado === estado; }).length;
    };
    var votos = ideas.reduce(function (total, i) { return total + i.votos; }, 0);

    document.getElementById('statTotal').textContent = ideas.length;
    document.getElementById('statEvaluacion').textContent = contar('evaluacion');
    document.getElementById('statAprobadas').textContent = contar('aprobada');
    document.getElementById('statVotos').textContent = votos;

    el.sub.textContent = ideas.length + (ideas.length === 1 ? ' idea' : ' ideas') + ' · ' + votos + ' votos';
  }


  /* ---------- Modal ---------- */

  function abrirModal(idea, estadoInicial) {
    el.form.classList.remove('was-validated');
    el.titulo.classList.remove('is-invalid');

    el.id.value = idea ? idea.id : '';
    el.titulo.value = idea ? idea.titulo : '';
    el.descripcion.value = idea ? idea.descripcion : '';
    el.categoria.value = idea ? idea.categoria : (filtro.categoria || 'Producto');
    el.estado.value = idea ? idea.estado : (estadoInicial || 'nueva');
    el.autor.value = idea ? idea.autor : (leerJSON('xnx-ideas-autor', '') || '');

    var color = idea ? idea.color : 'azul';
    var radio = el.form.querySelector('input[name="ideaColor"][value="' + color + '"]');
    if (radio) radio.checked = true;

    el.modalTitulo.innerHTML = idea
      ? '<i class="bi bi-pencil-square me-2"></i>Editar idea'
      : '<i class="bi bi-lightbulb me-2"></i>Nueva idea';
    el.btnEliminar.classList.toggle('d-none', !idea);

    modal.show();
  }

  document.getElementById('modalIdea').addEventListener('shown.bs.modal', function () {
    el.titulo.focus();
  });

  el.form.addEventListener('submit', function (evento) {
    evento.preventDefault();

    var titulo = el.titulo.value.trim();
    if (titulo.length < 4) {
      el.titulo.classList.add('is-invalid');
      el.titulo.focus();
      return;
    }

    var autor = el.autor.value.trim() || 'Anónimo';
    var datos = {
      titulo: titulo,
      descripcion: el.descripcion.value.trim(),
      categoria: el.categoria.value,
      estado: el.estado.value,
      autor: autor,
      color: (el.form.querySelector('input[name="ideaColor"]:checked') || {}).value || 'azul'
    };

    var existente = buscarIdea(el.id.value);
    if (existente) {
      Object.assign(existente, datos);
      avisar('Idea actualizada');
    } else {
      ideas.push(Object.assign({ id: nuevoId(), votos: 0, creada: Date.now() }, datos));
      avisar('Idea agregada a ' + NOMBRE_ESTADO[datos.estado]);
    }

    escribirJSON('xnx-ideas-autor', autor === 'Anónimo' ? '' : autor);
    guardarIdeas();
    pintar();
    modal.hide();
  });

  el.titulo.addEventListener('input', function () {
    el.titulo.classList.remove('is-invalid');
  });

  el.btnEliminar.addEventListener('click', function () {
    eliminar(el.id.value);
    modal.hide();
  });

  function eliminar(id) {
    var idea = buscarIdea(id);
    if (!idea) return;
    if (!window.confirm('¿Eliminar la idea "' + idea.titulo + '"?')) return;

    ideas = ideas.filter(function (i) { return i.id !== id; });
    delete misVotos[id];
    guardarIdeas();
    pintar();
    avisar('Idea eliminada');
  }


  /* ---------- Votos, editar y eliminar desde la tarjeta ---------- */

  el.board.addEventListener('click', function (evento) {
    var agregar = evento.target.closest('[data-agregar]');
    if (agregar) {
      abrirModal(null, agregar.getAttribute('data-agregar'));
      return;
    }

    var boton = evento.target.closest('[data-accion]');
    var card = evento.target.closest('.idea-card');
    if (!card) return;

    var idea = buscarIdea(card.getAttribute('data-id'));
    if (!idea) return;

    var accion = boton ? boton.getAttribute('data-accion') : 'editar';

    if (accion === 'votar') {
      if (misVotos[idea.id]) {
        delete misVotos[idea.id];
        idea.votos = Math.max(0, idea.votos - 1);
      } else {
        misVotos[idea.id] = true;
        idea.votos += 1;
      }
      guardarIdeas();
      pintar();

      var nuevoBoton = el.board.querySelector('.idea-card[data-id="' + idea.id + '"] .idea-vote');
      if (nuevoBoton && misVotos[idea.id]) nuevoBoton.classList.add('pop');
    } else if (accion === 'eliminar') {
      eliminar(idea.id);
    } else {
      abrirModal(idea);
    }
  });


  /* ---------- Arrastrar y soltar entre columnas ---------- */

  el.board.addEventListener('dragstart', function (evento) {
    var card = evento.target.closest('.idea-card');
    if (!card) return;
    idArrastrado = card.getAttribute('data-id');
    card.classList.add('dragging');
    evento.dataTransfer.effectAllowed = 'move';
    try { evento.dataTransfer.setData('text/plain', idArrastrado); } catch (e) { /* IE */ }
  });

  el.board.addEventListener('dragend', function (evento) {
    var card = evento.target.closest('.idea-card');
    if (card) card.classList.remove('dragging');
    el.board.querySelectorAll('.drag-over').forEach(function (c) { c.classList.remove('drag-over'); });
    idArrastrado = null;
  });

  el.board.addEventListener('dragover', function (evento) {
    var col = evento.target.closest('.ideas-col');
    if (!col || !idArrastrado) return;
    evento.preventDefault();
    evento.dataTransfer.dropEffect = 'move';
    el.board.querySelectorAll('.drag-over').forEach(function (c) {
      if (c !== col) c.classList.remove('drag-over');
    });
    col.classList.add('drag-over');
  });

  el.board.addEventListener('dragleave', function (evento) {
    var col = evento.target.closest('.ideas-col');
    if (col && !col.contains(evento.relatedTarget)) col.classList.remove('drag-over');
  });

  el.board.addEventListener('drop', function (evento) {
    var col = evento.target.closest('.ideas-col');
    if (!col) return;
    evento.preventDefault();
    col.classList.remove('drag-over');

    var idea = buscarIdea(idArrastrado);
    var destino = col.getAttribute('data-estado');
    if (!idea || idea.estado === destino) return;

    idea.estado = destino;
    guardarIdeas();
    pintar();
    avisar('Movida a ' + NOMBRE_ESTADO[destino]);
  });


  /* ---------- Filtros, búsqueda y orden ---------- */

  el.filtros.addEventListener('click', function (evento) {
    var chip = evento.target.closest('.idea-chip');
    if (!chip) return;
    el.filtros.querySelectorAll('.idea-chip').forEach(function (c) {
      c.classList.toggle('active', c === chip);
    });
    filtro.categoria = chip.getAttribute('data-categoria');
    pintar();
  });

  el.buscar.addEventListener('input', function () {
    filtro.texto = el.buscar.value.trim().toLowerCase();
    pintar();
  });

  el.orden.addEventListener('change', function () {
    filtro.orden = el.orden.value;
    pintar();
  });

  document.getElementById('btnNuevaIdea').addEventListener('click', function () {
    abrirModal(null);
  });


  /* ---------- Inicio ---------- */

  ideas = cargarIdeas();
  misVotos = leerJSON(CLAVE_VOTOS, {});
  guardarIdeas();
  pintar();
})();
