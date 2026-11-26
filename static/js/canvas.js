/* =========================================================
   XINCRONIX — CANVAS (pizarra del equipo)

   Herramientas: seleccionar/mover, lápiz, rectángulo,
   círculo, flecha, texto, nota adhesiva y borrador.
   Incluye zoom, desplazamiento, deshacer/rehacer y
   exportar a PNG.

   El lienzo se guarda en el navegador (localStorage).
   Para compartirlo con el equipo, cambia solo las
   funciones  cargarLienzo()  y  guardarLienzo()  por
   llamadas a tu API; el resto del archivo no cambia.
   ========================================================= */

(function () {
  'use strict';

  var inicialNodo = document.getElementById('lienzoInicial');
  var guardarNodo = document.getElementById('canvasGuardarUrl');
  var URL_GUARDAR = guardarNodo && guardarNodo.dataset.url;
  var ZOOM_MIN = 0.25;
  var ZOOM_MAX = 3;
  var NOTA_ANCHO = 190;
  var NOTA_ALTO = 150;

  /* Colores de las notas (fondo pastel, texto oscuro) */
  var NOTA_COLORES = {
    ink: '#e8eefc',
    '#2a5bff': '#dbe6ff',
    '#10b981': '#d3f5e6',
    '#f5b43c': '#fff1c9',
    '#ef4444': '#ffdcdc',
    '#8b5cf6': '#ebe1ff'
  };

  var lienzo = document.getElementById('lienzo');
  var ctx = lienzo.getContext('2d');
  var wrap = document.getElementById('canvasWrap');
  var editor = document.getElementById('editorTexto');
  var hint = document.getElementById('canvasHint');
  var inputNombre = document.getElementById('nombreLienzo');
  var inputGrosor = document.getElementById('grosor');
  var zoomTexto = document.getElementById('zoomNivel');
  var toast = new bootstrap.Toast(document.getElementById('canvasToast'), { delay: 2000 });

  var estado = {
    herramienta: 'select',
    color: 'ink',
    grosor: 3,
    objetos: [],
    vista: { x: 0, y: 0, escala: 1 },
    seleccion: null,        // id del objeto seleccionado
    borrador: null,         // objeto que se está dibujando
    accion: null,           // 'dibujar' | 'mover' | 'desplazar' | 'borrar'
    inicio: null,
    espacio: false,         // tecla espacio pulsada (desplazar)
    editando: null          // objeto cuyo texto se está editando
  };

  var historial = [];
  var futuro = [];
  var dpr = window.devicePixelRatio || 1;
  var ancho = 0;
  var alto = 0;


  /* ---------- Utilidades ---------- */

  function nuevoId() {
    return 'o' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
  }

  function variableCSS(nombre) {
    return getComputedStyle(document.documentElement).getPropertyValue(nombre).trim();
  }

  function colorReal(color) {
    return color === 'ink' ? variableCSS('--canvas-ink') : color;
  }

  function avisar(texto) {
    document.getElementById('canvasToastBody').textContent = texto;
    toast.show();
  }

  function aMundo(evento) {
    var r = lienzo.getBoundingClientRect();
    var sx = evento.clientX - r.left;
    var sy = evento.clientY - r.top;
    return {
      sx: sx,
      sy: sy,
      x: (sx - estado.vista.x) / estado.vista.escala,
      y: (sy - estado.vista.y) / estado.vista.escala
    };
  }

  function buscar(id) {
    for (var i = 0; i < estado.objetos.length; i++) {
      if (estado.objetos[i].id === id) return estado.objetos[i];
    }
    return null;
  }

  function tamanoFuente(obj) {
    return 14 + obj.grosor * 2;
  }


  /* ---------- Guardado ---------- */

  function cargarLienzo() {
    try {
      var datos = inicialNodo ? JSON.parse(inicialNodo.textContent || '{}') : {};
      if (datos && Array.isArray(datos.objetos)) return datos;
    } catch (e) { /* lienzo nuevo */ }
    return null;
  }

  function csrf() {
    var encontrada = document.cookie.match(/(?:^|; )csrftoken=([^;]*)/);
    return encontrada ? decodeURIComponent(encontrada[1]) : '';
  }

  function guardarLienzo() {
    if (!URL_GUARDAR) return;
    clearTimeout(estado.guardarServidor);
    estado.guardarServidor = setTimeout(function () {
      fetch(URL_GUARDAR, {
        method: 'POST', credentials: 'same-origin',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf()},
        body: JSON.stringify({nombre: inputNombre.value, contenido: {
          objetos: estado.objetos, vista: estado.vista
        }})
      }).then(function (r) {
        if (!r.ok) throw new Error('No se pudo guardar');
        return r.json();
      }).then(function () { avisar('Canvas guardado'); })
        .catch(function () { avisar('Sin conexión: intenta guardar de nuevo'); });
    }, 450);
  }

  /* Guarda una foto del estado para poder deshacer */
  function confirmarCambio() {
    historial.push(JSON.stringify(estado.objetos));
    if (historial.length > 80) historial.shift();
    futuro = [];
    guardarLienzo();
    actualizarBotones();
  }

  function deshacer() {
    if (historial.length < 2) return;
    futuro.push(historial.pop());
    estado.objetos = JSON.parse(historial[historial.length - 1]);
    estado.seleccion = null;
    guardarLienzo();
    actualizarBotones();
    dibujar();
  }

  function rehacer() {
    if (!futuro.length) return;
    var siguiente = futuro.pop();
    historial.push(siguiente);
    estado.objetos = JSON.parse(siguiente);
    estado.seleccion = null;
    guardarLienzo();
    actualizarBotones();
    dibujar();
  }

  function actualizarBotones() {
    document.getElementById('btnDeshacer').disabled = historial.length < 2;
    document.getElementById('btnRehacer').disabled = !futuro.length;
    document.getElementById('btnBorrarSel').disabled = !estado.seleccion;
    zoomTexto.textContent = Math.round(estado.vista.escala * 100) + '%';
    hint.classList.toggle('hidden', estado.objetos.length > 0);
  }


  /* ---------- Medidas y detección ---------- */

  function medirTexto(obj) {
    var fs = tamanoFuente(obj);
    ctx.save();
    ctx.font = '600 ' + fs + 'px Inter, "Segoe UI", Roboto, sans-serif';
    var lineas = String(obj.texto || '').split('\n');
    var w = 0;
    lineas.forEach(function (l) { w = Math.max(w, ctx.measureText(l).width); });
    ctx.restore();
    obj.w = Math.max(20, w);
    obj.h = lineas.length * fs * 1.3;
  }

  function caja(obj) {
    if (obj.tipo === 'trazo') {
      var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      obj.puntos.forEach(function (p) {
        minX = Math.min(minX, p[0]); minY = Math.min(minY, p[1]);
        maxX = Math.max(maxX, p[0]); maxY = Math.max(maxY, p[1]);
      });
      return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
    }
    if (obj.tipo === 'texto') medirTexto(obj);
    var x = obj.w < 0 ? obj.x + obj.w : obj.x;
    var y = obj.h < 0 ? obj.y + obj.h : obj.y;
    return { x: x, y: y, w: Math.abs(obj.w), h: Math.abs(obj.h) };
  }

  function distanciaSegmento(px, py, ax, ay, bx, by) {
    var dx = bx - ax, dy = by - ay;
    var largo = dx * dx + dy * dy;
    var t = largo ? Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / largo)) : 0;
    var cx = ax + t * dx, cy = ay + t * dy;
    return Math.hypot(px - cx, py - cy);
  }

  function toca(obj, x, y) {
    var margen = 6 / estado.vista.escala + obj.grosor / 2;
    if (obj.tipo === 'trazo') {
      for (var i = 1; i < obj.puntos.length; i++) {
        var a = obj.puntos[i - 1], b = obj.puntos[i];
        if (distanciaSegmento(x, y, a[0], a[1], b[0], b[1]) <= margen) return true;
      }
      return obj.puntos.length === 1 && Math.hypot(x - obj.puntos[0][0], y - obj.puntos[0][1]) <= margen;
    }
    if (obj.tipo === 'flecha') {
      return distanciaSegmento(x, y, obj.x, obj.y, obj.x + obj.w, obj.y + obj.h) <= margen;
    }
    var c = caja(obj);
    if (obj.tipo === 'nota' || obj.tipo === 'texto') {
      return x >= c.x - margen && x <= c.x + c.w + margen && y >= c.y - margen && y <= c.y + c.h + margen;
    }
    if (obj.tipo === 'rect') {
      var dentro = x >= c.x - margen && x <= c.x + c.w + margen && y >= c.y - margen && y <= c.y + c.h + margen;
      var adentro = x > c.x + margen && x < c.x + c.w - margen && y > c.y + margen && y < c.y + c.h - margen;
      return dentro && !adentro;
    }
    if (obj.tipo === 'elipse') {
      var rx = c.w / 2, ry = c.h / 2;
      if (rx < 1 || ry < 1) return false;
      var nx = (x - (c.x + rx)) / rx, ny = (y - (c.y + ry)) / ry;
      var d = Math.sqrt(nx * nx + ny * ny);
      return Math.abs(d - 1) * Math.min(rx, ry) <= margen;
    }
    return false;
  }

  function objetoEn(x, y) {
    for (var i = estado.objetos.length - 1; i >= 0; i--) {
      if (toca(estado.objetos[i], x, y)) return estado.objetos[i];
    }
    return null;
  }


  /* ---------- Dibujo ---------- */

  function redondeado(c, x, y, w, h, r) {
    c.beginPath();
    c.moveTo(x + r, y);
    c.arcTo(x + w, y, x + w, y + h, r);
    c.arcTo(x + w, y + h, x, y + h, r);
    c.arcTo(x, y + h, x, y, r);
    c.arcTo(x, y, x + w, y, r);
    c.closePath();
  }

  function envolverTexto(c, texto, anchoMax) {
    var lineas = [];
    String(texto || '').split('\n').forEach(function (parrafo) {
      var palabras = parrafo.split(' ');
      var linea = '';
      palabras.forEach(function (p) {
        var prueba = linea ? linea + ' ' + p : p;
        if (c.measureText(prueba).width > anchoMax && linea) {
          lineas.push(linea);
          linea = p;
        } else {
          linea = prueba;
        }
      });
      lineas.push(linea);
    });
    return lineas;
  }

  function pintarObjeto(c, obj) {
    var color = colorReal(obj.color);
    c.save();
    c.strokeStyle = color;
    c.fillStyle = color;
    c.lineWidth = obj.grosor;
    c.lineCap = 'round';
    c.lineJoin = 'round';

    if (obj.tipo === 'trazo') {
      var p = obj.puntos;
      if (p.length === 1) {
        c.beginPath();
        c.arc(p[0][0], p[0][1], obj.grosor / 2, 0, Math.PI * 2);
        c.fill();
      } else {
        c.beginPath();
        c.moveTo(p[0][0], p[0][1]);
        for (var i = 1; i < p.length - 1; i++) {
          var mx = (p[i][0] + p[i + 1][0]) / 2, my = (p[i][1] + p[i + 1][1]) / 2;
          c.quadraticCurveTo(p[i][0], p[i][1], mx, my);
        }
        c.lineTo(p[p.length - 1][0], p[p.length - 1][1]);
        c.stroke();
      }
    } else if (obj.tipo === 'rect') {
      var r = caja(obj);
      redondeado(c, r.x, r.y, r.w, r.h, Math.min(10, r.w / 2, r.h / 2));
      c.stroke();
    } else if (obj.tipo === 'elipse') {
      var e = caja(obj);
      c.beginPath();
      c.ellipse(e.x + e.w / 2, e.y + e.h / 2, e.w / 2, e.h / 2, 0, 0, Math.PI * 2);
      c.stroke();
    } else if (obj.tipo === 'flecha') {
      var x2 = obj.x + obj.w, y2 = obj.y + obj.h;
      var ang = Math.atan2(obj.h, obj.w);
      var punta = 10 + obj.grosor * 2.5;
      c.beginPath();
      c.moveTo(obj.x, obj.y);
      c.lineTo(x2, y2);
      c.stroke();
      c.beginPath();
      c.moveTo(x2, y2);
      c.lineTo(x2 - punta * Math.cos(ang - 0.45), y2 - punta * Math.sin(ang - 0.45));
      c.lineTo(x2 - punta * Math.cos(ang + 0.45), y2 - punta * Math.sin(ang + 0.45));
      c.closePath();
      c.fill();
    } else if (obj.tipo === 'texto') {
      if (estado.editando !== obj) {
        var fs = tamanoFuente(obj);
        c.font = '600 ' + fs + 'px Inter, "Segoe UI", Roboto, sans-serif';
        c.textBaseline = 'top';
        String(obj.texto).split('\n').forEach(function (l, i) {
          c.fillText(l, obj.x, obj.y + i * fs * 1.3);
        });
      }
    } else if (obj.tipo === 'nota') {
      var fondo = NOTA_COLORES[obj.color] || NOTA_COLORES.ink;
      c.shadowColor = 'rgba(7, 16, 31, 0.18)';
      c.shadowBlur = 14;
      c.shadowOffsetY = 5;
      redondeado(c, obj.x, obj.y, obj.w, obj.h, 10);
      c.fillStyle = fondo;
      c.fill();
      c.shadowColor = 'transparent';

      // franja superior del color elegido
      c.save();
      redondeado(c, obj.x, obj.y, obj.w, obj.h, 10);
      c.clip();
      c.fillStyle = obj.color === 'ink' ? '#1a3a7c' : obj.color;
      c.fillRect(obj.x, obj.y, obj.w, 6);
      c.restore();

      // esquina doblada
      c.beginPath();
      c.moveTo(obj.x + obj.w - 18, obj.y + obj.h);
      c.lineTo(obj.x + obj.w, obj.y + obj.h - 18);
      c.lineTo(obj.x + obj.w - 18, obj.y + obj.h - 18);
      c.closePath();
      c.fillStyle = 'rgba(7, 16, 31, 0.08)';
      c.fill();

      if (estado.editando !== obj) {
        c.fillStyle = '#1a2540';
        c.font = '600 14px Inter, "Segoe UI", Roboto, sans-serif';
        c.textBaseline = 'top';
        var lineas = envolverTexto(c, obj.texto, obj.w - 24);
        var maxLineas = Math.floor((obj.h - 28) / 19);
        lineas.slice(0, maxLineas).forEach(function (l, i) {
          c.fillText(l, obj.x + 12, obj.y + 18 + i * 19);
        });
      }
    }
    c.restore();
  }

  function pintarCuadricula() {
    var paso = 24 * estado.vista.escala;
    if (paso < 9) return;
    ctx.fillStyle = variableCSS('--canvas-dot');
    var x0 = estado.vista.x % paso, y0 = estado.vista.y % paso;
    var r = Math.max(0.8, 1.1 * Math.min(1.4, estado.vista.escala));
    for (var x = x0; x < ancho; x += paso) {
      for (var y = y0; y < alto; y += paso) {
        ctx.fillRect(x - r / 2, y - r / 2, r, r);
      }
    }
  }

  function dibujar() {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = variableCSS('--canvas-bg');
    ctx.fillRect(0, 0, ancho, alto);
    pintarCuadricula();

    var v = estado.vista;
    ctx.setTransform(dpr * v.escala, 0, 0, dpr * v.escala, dpr * v.x, dpr * v.y);
    estado.objetos.forEach(function (o) { pintarObjeto(ctx, o); });
    if (estado.borrador) pintarObjeto(ctx, estado.borrador);

    var sel = buscar(estado.seleccion);
    if (sel) {
      var c = caja(sel);
      var m = 6 / v.escala;
      ctx.save();
      ctx.strokeStyle = variableCSS('--canvas-select');
      ctx.lineWidth = 1.5 / v.escala;
      ctx.setLineDash([6 / v.escala, 4 / v.escala]);
      ctx.strokeRect(c.x - m, c.y - m, c.w + m * 2, c.h + m * 2);
      ctx.restore();
    }
  }

  function ajustarTamano() {
    var r = wrap.getBoundingClientRect();
    ancho = r.width;
    alto = r.height;
    dpr = window.devicePixelRatio || 1;
    lienzo.width = Math.round(ancho * dpr);
    lienzo.height = Math.round(alto * dpr);
    dibujar();
  }


  /* ---------- Zoom ---------- */

  function zoomEn(factor, sx, sy) {
    var v = estado.vista;
    var nueva = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, v.escala * factor));
    v.x = sx - (sx - v.x) * (nueva / v.escala);
    v.y = sy - (sy - v.y) * (nueva / v.escala);
    v.escala = nueva;
    cerrarEditor();
    actualizarBotones();
    dibujar();
    guardarLienzo();
  }

  function verTodo() {
    if (!estado.objetos.length) {
      estado.vista = { x: 0, y: 0, escala: 1 };
    } else {
      var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      estado.objetos.forEach(function (o) {
        var c = caja(o);
        minX = Math.min(minX, c.x); minY = Math.min(minY, c.y);
        maxX = Math.max(maxX, c.x + c.w); maxY = Math.max(maxY, c.y + c.h);
      });
      var pad = 60;
      var escala = Math.min(ancho / (maxX - minX + pad * 2), alto / (maxY - minY + pad * 2), 1.5);
      escala = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, escala));
      estado.vista = {
        escala: escala,
        x: ancho / 2 - ((minX + maxX) / 2) * escala,
        y: alto / 2 - ((minY + maxY) / 2) * escala
      };
    }
    cerrarEditor();
    actualizarBotones();
    dibujar();
    guardarLienzo();
  }


  /* ---------- Editor de texto ---------- */

  function abrirEditor(obj) {
    estado.editando = obj;
    var v = estado.vista;
    var esNota = obj.tipo === 'nota';
    editor.hidden = false;
    editor.classList.toggle('is-note', esNota);
    editor.value = obj.texto || '';

    if (esNota) {
      editor.style.left = (obj.x * v.escala + v.x + 6) + 'px';
      editor.style.top = (obj.y * v.escala + v.y + 10) + 'px';
      editor.style.width = ((obj.w - 12) * v.escala) + 'px';
      editor.style.height = ((obj.h - 20) * v.escala) + 'px';
      editor.style.fontSize = (14 * v.escala) + 'px';
      editor.style.color = '';
    } else {
      var fs = tamanoFuente(obj);
      editor.style.left = (obj.x * v.escala + v.x - 8) + 'px';
      editor.style.top = (obj.y * v.escala + v.y - 6) + 'px';
      editor.style.width = Math.max(180, (obj.w || 0) * v.escala + 40) + 'px';
      editor.style.height = Math.max(fs * 1.3 * v.escala + 14, (obj.h || 0) * v.escala + 14) + 'px';
      editor.style.fontSize = (fs * v.escala) + 'px';
      editor.style.color = colorReal(obj.color);
    }
    dibujar();
    editor.focus();
    editor.select();
  }

  function cerrarEditor() {
    var obj = estado.editando;
    if (!obj) return;
    estado.editando = null;
    editor.hidden = true;

    var texto = editor.value.replace(/\s+$/, '');
    if (!texto && obj.tipo === 'texto') {
      estado.objetos = estado.objetos.filter(function (o) { return o !== obj; });
      if (estado.seleccion === obj.id) estado.seleccion = null;
    } else {
      obj.texto = texto;
    }
    confirmarCambio();
    dibujar();
  }

  editor.addEventListener('blur', cerrarEditor);

  editor.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' || (e.key === 'Enter' && (e.ctrlKey || e.metaKey))) {
      e.preventDefault();
      editor.blur();
    } else if (e.key === 'Enter' && !e.shiftKey && estado.editando && estado.editando.tipo === 'texto') {
      e.preventDefault();
      editor.blur();
    }
  });

  editor.addEventListener('input', function () {
    var obj = estado.editando;
    if (!obj || obj.tipo !== 'texto') return;
    editor.style.height = 'auto';
    editor.style.height = editor.scrollHeight + 'px';
  });


  /* ---------- Crear notas ---------- */

  function crearNota(x, y) {
    var nota = {
      id: nuevoId(), tipo: 'nota',
      x: x, y: y, w: NOTA_ANCHO, h: NOTA_ALTO,
      color: estado.color, grosor: estado.grosor, texto: ''
    };
    estado.objetos.push(nota);
    estado.seleccion = nota.id;
    actualizarBotones();
    abrirEditor(nota);
  }


  /* ---------- Ratón / dedo ---------- */

  lienzo.addEventListener('pointerdown', function (e) {
    if (e.button !== 0 && e.button !== 1) return;
    // Evita que el clic en el lienzo le quite el foco al cuadro de texto que se abre
    e.preventDefault();
    if (estado.editando) {
      // Este clic solo cierra el cuadro de texto abierto
      editor.blur();
      return;
    } else if (document.activeElement && document.activeElement !== document.body) {
      document.activeElement.blur();
    }
    lienzo.setPointerCapture(e.pointerId);

    var p = aMundo(e);
    estado.inicio = p;
    var h = estado.herramienta;

    // Desplazar: botón central, espacio o arrastrar el fondo con "seleccionar"
    if (e.button === 1 || estado.espacio) {
      estado.accion = 'desplazar';
      estado.vistaInicio = { x: estado.vista.x, y: estado.vista.y };
      lienzo.classList.add('is-panning');
      return;
    }

    if (h === 'select') {
      var obj = objetoEn(p.x, p.y);
      estado.seleccion = obj ? obj.id : null;
      if (obj) {
        // al frente
        estado.objetos = estado.objetos.filter(function (o) { return o !== obj; }).concat(obj);
        estado.accion = 'mover';
        estado.movido = false;
      } else {
        estado.accion = 'desplazar';
        estado.vistaInicio = { x: estado.vista.x, y: estado.vista.y };
        lienzo.classList.add('is-panning');
      }
      actualizarBotones();
      dibujar();
      return;
    }

    if (h === 'eraser') {
      estado.accion = 'borrar';
      estado.borrados = 0;
      borrarEn(p);
      return;
    }

    if (h === 'text') {
      var existente = objetoEn(p.x, p.y);
      if (existente && existente.tipo === 'texto') { abrirEditor(existente); return; }
      var t = { id: nuevoId(), tipo: 'texto', x: p.x, y: p.y, color: estado.color, grosor: estado.grosor, texto: '' };
      estado.objetos.push(t);
      elegirHerramienta('select');
      estado.seleccion = t.id;
      abrirEditor(t);
      return;
    }

    if (h === 'note') {
      elegirHerramienta('select');
      crearNota(p.x - NOTA_ANCHO / 2, p.y - 20);
      return;
    }

    estado.accion = 'dibujar';
    var base = { id: nuevoId(), color: estado.color, grosor: estado.grosor };
    if (h === 'pen') {
      estado.borrador = Object.assign(base, { tipo: 'trazo', puntos: [[p.x, p.y]] });
    } else {
      var tipo = { rect: 'rect', ellipse: 'elipse', arrow: 'flecha' }[h];
      estado.borrador = Object.assign(base, { tipo: tipo, x: p.x, y: p.y, w: 0, h: 0 });
    }
    dibujar();
  });

  lienzo.addEventListener('pointermove', function (e) {
    var p = aMundo(e);

    if (!estado.accion) {
      // cursor según lo que hay debajo
      if (estado.herramienta === 'select') {
        var sobre = objetoEn(p.x, p.y);
        lienzo.classList.toggle('over-object', !!sobre);
        lienzo.classList.toggle('over-empty', !sobre);
      }
      return;
    }

    var ini = estado.inicio;

    if (estado.accion === 'desplazar') {
      estado.vista.x = estado.vistaInicio.x + (p.sx - ini.sx);
      estado.vista.y = estado.vistaInicio.y + (p.sy - ini.sy);
      dibujar();
      return;
    }

    if (estado.accion === 'mover') {
      var obj = buscar(estado.seleccion);
      if (!obj) return;
      var dx = p.x - ini.x, dy = p.y - ini.y;
      if (obj.tipo === 'trazo') {
        obj.puntos = obj.puntos.map(function (q) { return [q[0] + dx, q[1] + dy]; });
      } else {
        obj.x += dx;
        obj.y += dy;
      }
      estado.inicio = p;
      estado.movido = true;
      dibujar();
      return;
    }

    if (estado.accion === 'borrar') {
      borrarEn(p);
      return;
    }

    if (estado.accion === 'dibujar' && estado.borrador) {
      var b = estado.borrador;
      if (b.tipo === 'trazo') {
        var ultimo = b.puntos[b.puntos.length - 1];
        if (Math.hypot(p.x - ultimo[0], p.y - ultimo[1]) > 1.5 / estado.vista.escala) b.puntos.push([p.x, p.y]);
      } else {
        b.w = p.x - b.x;
        b.h = p.y - b.y;
        if (e.shiftKey && b.tipo !== 'flecha') {
          var lado = Math.max(Math.abs(b.w), Math.abs(b.h));
          b.w = lado * Math.sign(b.w || 1);
          b.h = lado * Math.sign(b.h || 1);
        }
      }
      dibujar();
    }
  });

  function terminar() {
    var accion = estado.accion;
    estado.accion = null;
    lienzo.classList.remove('is-panning');

    if (accion === 'desplazar') {
      guardarLienzo();
    } else if (accion === 'mover' && estado.movido) {
      confirmarCambio();
    } else if (accion === 'borrar' && estado.borrados) {
      confirmarCambio();
    } else if (accion === 'dibujar' && estado.borrador) {
      var b = estado.borrador;
      estado.borrador = null;
      var valido = b.tipo === 'trazo' || Math.hypot(b.w, b.h) > 4;
      if (valido) {
        if (b.tipo === 'rect' || b.tipo === 'elipse') {
          var c = caja(b);
          b.x = c.x; b.y = c.y; b.w = c.w; b.h = c.h;
        }
        estado.objetos.push(b);
        confirmarCambio();
      }
      dibujar();
    }
  }

  lienzo.addEventListener('pointerup', terminar);
  lienzo.addEventListener('pointercancel', terminar);

  lienzo.addEventListener('dblclick', function (e) {
    var p = aMundo(e);
    var obj = objetoEn(p.x, p.y);
    if (obj && (obj.tipo === 'texto' || obj.tipo === 'nota')) {
      estado.seleccion = obj.id;
      abrirEditor(obj);
    } else if (!obj && estado.herramienta === 'select') {
      crearNota(p.x - NOTA_ANCHO / 2, p.y - 20);
    }
  });

  function borrarEn(p) {
    var obj = objetoEn(p.x, p.y);
    if (!obj) return;
    estado.objetos = estado.objetos.filter(function (o) { return o !== obj; });
    if (estado.seleccion === obj.id) estado.seleccion = null;
    estado.borrados++;
    actualizarBotones();
    dibujar();
  }

  lienzo.addEventListener('wheel', function (e) {
    e.preventDefault();
    var p = aMundo(e);
    if (e.ctrlKey || e.metaKey) {
      zoomEn(Math.exp(-e.deltaY * 0.0015), p.sx, p.sy);
    } else {
      estado.vista.x -= e.deltaX;
      estado.vista.y -= e.deltaY;
      cerrarEditor();
      dibujar();
      clearTimeout(estado.guardarVista);
      estado.guardarVista = setTimeout(guardarLienzo, 300);
    }
  }, { passive: false });


  /* ---------- Barra de herramientas ---------- */

  function elegirHerramienta(nombre) {
    estado.herramienta = nombre;
    lienzo.setAttribute('data-tool', nombre);
    lienzo.classList.remove('over-object', 'over-empty');
    document.querySelectorAll('.canvas-tool[data-tool]').forEach(function (b) {
      var activa = b.getAttribute('data-tool') === nombre;
      b.classList.toggle('active', activa);
      b.setAttribute('aria-pressed', activa);
    });
    if (nombre !== 'select') {
      estado.seleccion = null;
      actualizarBotones();
      dibujar();
    }
  }

  document.querySelectorAll('.canvas-tool[data-tool]').forEach(function (b) {
    b.addEventListener('click', function () { elegirHerramienta(b.getAttribute('data-tool')); });
  });

  document.querySelectorAll('.canvas-color').forEach(function (b) {
    b.addEventListener('click', function () {
      estado.color = b.getAttribute('data-color');
      document.querySelectorAll('.canvas-color').forEach(function (x) { x.classList.toggle('active', x === b); });

      // Si hay algo seleccionado, también le cambia el color
      var sel = buscar(estado.seleccion);
      if (sel) { sel.color = estado.color; confirmarCambio(); dibujar(); }
    });
  });

  inputGrosor.addEventListener('input', function () {
    estado.grosor = Number(inputGrosor.value);
    var sel = buscar(estado.seleccion);
    if (sel && sel.tipo !== 'nota') { sel.grosor = estado.grosor; dibujar(); }
  });

  inputGrosor.addEventListener('change', function () {
    if (buscar(estado.seleccion)) confirmarCambio();
  });

  function borrarSeleccion() {
    var sel = buscar(estado.seleccion);
    if (!sel) return;
    estado.objetos = estado.objetos.filter(function (o) { return o !== sel; });
    estado.seleccion = null;
    confirmarCambio();
    dibujar();
  }

  document.getElementById('btnDeshacer').addEventListener('click', deshacer);
  document.getElementById('btnRehacer').addEventListener('click', rehacer);
  document.getElementById('btnBorrarSel').addEventListener('click', borrarSeleccion);

  document.getElementById('btnLimpiar').addEventListener('click', function () {
    if (!estado.objetos.length) return;
    if (!window.confirm('¿Borrar todo el contenido del canvas? Puedes deshacerlo con Ctrl+Z.')) return;
    estado.objetos = [];
    estado.seleccion = null;
    confirmarCambio();
    dibujar();
    avisar('Canvas limpio');
  });

  document.getElementById('btnZoomMas').addEventListener('click', function () { zoomEn(1.2, ancho / 2, alto / 2); });
  document.getElementById('btnZoomMenos').addEventListener('click', function () { zoomEn(1 / 1.2, ancho / 2, alto / 2); });
  document.getElementById('btnAjustar').addEventListener('click', verTodo);

  document.getElementById('btnNuevaNota').addEventListener('click', function () {
    var v = estado.vista;
    var cx = (ancho / 2 - v.x) / v.escala, cy = (alto / 2 - v.y) / v.escala;
    var desfase = (estado.objetos.length % 5) * 18;
    elegirHerramienta('select');
    crearNota(cx - NOTA_ANCHO / 2 + desfase, cy - NOTA_ALTO / 2 + desfase);
  });

  inputNombre.addEventListener('input', guardarLienzo);


  /* ---------- Exportar a PNG ---------- */

  document.getElementById('btnExportar').addEventListener('click', function () {
    if (!estado.objetos.length) { avisar('El canvas está vacío'); return; }
    var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    estado.objetos.forEach(function (o) {
      var c = caja(o);
      minX = Math.min(minX, c.x); minY = Math.min(minY, c.y);
      maxX = Math.max(maxX, c.x + c.w); maxY = Math.max(maxY, c.y + c.h);
    });
    var pad = 40, escala = 2;
    var w = maxX - minX + pad * 2, h = maxY - minY + pad * 2;
    var lienzoExp = document.createElement('canvas');
    lienzoExp.width = Math.ceil(w * escala);
    lienzoExp.height = Math.ceil(h * escala);
    var c2 = lienzoExp.getContext('2d');
    c2.fillStyle = variableCSS('--canvas-bg');
    c2.fillRect(0, 0, lienzoExp.width, lienzoExp.height);
    c2.setTransform(escala, 0, 0, escala, (pad - minX) * escala, (pad - minY) * escala);
    var editando = estado.editando;
    estado.editando = null;
    estado.objetos.forEach(function (o) { pintarObjeto(c2, o); });
    estado.editando = editando;

    var enlace = document.createElement('a');
    enlace.download = (inputNombre.value.trim() || 'canvas').replace(/[^\w\-áéíóúñ ]+/gi, '') + '.png';
    enlace.href = lienzoExp.toDataURL('image/png');
    enlace.click();
    avisar('Imagen descargada');
  });


  /* ---------- Teclado ---------- */

  var ATAJOS = { v: 'select', p: 'pen', r: 'rect', o: 'ellipse', a: 'arrow', t: 'text', n: 'note', e: 'eraser' };

  document.addEventListener('keydown', function (e) {
    var escribiendo = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
    if (escribiendo) return;

    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') {
      e.preventDefault();
      if (e.shiftKey) rehacer(); else deshacer();
    } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'y') {
      e.preventDefault();
      rehacer();
    } else if (e.key === 'Delete' || e.key === 'Backspace') {
      if (estado.seleccion) { e.preventDefault(); borrarSeleccion(); }
    } else if (e.key === ' ') {
      if (!estado.espacio) { estado.espacio = true; lienzo.classList.add('is-panning'); }
      e.preventDefault();
    } else if (!e.ctrlKey && !e.metaKey && !e.altKey && ATAJOS[e.key.toLowerCase()]) {
      elegirHerramienta(ATAJOS[e.key.toLowerCase()]);
    }
  });

  document.addEventListener('keyup', function (e) {
    if (e.key === ' ') {
      estado.espacio = false;
      if (estado.accion !== 'desplazar') lienzo.classList.remove('is-panning');
    }
  });


  /* ---------- Tema claro/oscuro ---------- */

  document.addEventListener('xnx:tema', dibujar);


  /* ---------- Inicio ---------- */

  var guardado = cargarLienzo();
  if (guardado) {
    estado.objetos = guardado.objetos;
    if (guardado.vista) estado.vista = guardado.vista;
    if (guardado.nombre) inputNombre.value = guardado.nombre;
  }

  historial = [JSON.stringify(estado.objetos)];
  elegirHerramienta('select');
  actualizarBotones();

  if (window.ResizeObserver) {
    new ResizeObserver(ajustarTamano).observe(wrap);
  } else {
    window.addEventListener('resize', ajustarTamano);
  }
  ajustarTamano();
})();
