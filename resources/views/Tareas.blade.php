<!DOCTYPE html>
<html lang="es">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Xincronix — Tareas</title>

  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" />
  <link rel="stylesheet" href="{{ asset('assets/css/Index.css') }}" />
  <link rel="stylesheet" href="{{ asset('assets/css/Tareas.css') }}" />
</head>

<body>
  <div class="app-shell">

    <!-- ══ SIDEBAR ══ -->
    <aside class="xnx-sidebar">
      <div class="xnx-sidebar-logo">
        <div class="xnx-logo">
          <img src="{{ asset('assets/img/logo xincronix.png') }}"
            onerror="this.outerHTML='<svg width=\'28\' height=\'28\' viewBox=\'0 0 36 36\' fill=\'none\'><rect width=\'36\' height=\'36\' rx=\'8\' fill=\'rgba(37,99,235,0.2)\'/><line x1=\'5\' y1=\'10\' x2=\'15\' y2=\'26\' stroke=\'#3b82f6\' stroke-width=\'2.5\' stroke-linecap=\'round\'/><line x1=\'15\' y1=\'10\' x2=\'5\' y2=\'26\' stroke=\'#3b82f6\' stroke-width=\'2.5\' stroke-linecap=\'round\'/><line x1=\'15\' y1=\'18\' x2=\'21\' y2=\'18\' stroke=\'rgba(59,130,246,0.4)\' stroke-width=\'1.5\' stroke-dasharray=\'2 2\' stroke-linecap=\'round\'/><line x1=\'21\' y1=\'10\' x2=\'31\' y2=\'26\' stroke=\'#93c5fd\' stroke-width=\'2.5\' stroke-linecap=\'round\'/><line x1=\'31\' y1=\'10\' x2=\'21\' y2=\'26\' stroke=\'#93c5fd\' stroke-width=\'2.5\' stroke-linecap=\'round\'/></svg>'"
            alt="" />
          <div class="xnx-logo-text">Xin<span>cronix</span></div>
        </div>
      </div>
      <div class="xnx-sidebar-section">
        <div class="xnx-sidebar-section-label">General</div>
        <a href="Panel" class="xnx-sidebar-item"><i class="bi bi-grid"></i> Dashboard</a>
        <a href="Proyecto" class="xnx-sidebar-item">
          <i class="bi bi-kanban"></i> Proyectos
        </a>
        <a href="Tareas" class="xnx-sidebar-item active">
          <i class="bi bi-clock"></i> Tareas
        </a>
        <a href="Equipos" class="xnx-sidebar-item"><i class="bi bi-people"></i> Equipo</a>
      </div>
      <div class="xnx-sidebar-section">
        <div class="xnx-sidebar-section-label">IA &amp; Automatizacion</div>
        <a href="Asistente" class="xnx-sidebar-item"><i class="bi bi-chat-dots"></i> Asistente virtual</a>
        <a href="Automatizaciones" class="xnx-sidebar-item"><i class="bi bi-arrow-repeat"></i> Automatizaciones</a>
      </div>
      <div class="xnx-sidebar-section">
        <div class="xnx-sidebar-section-label">Reportes</div>
        <a href="Analytics" class="xnx-sidebar-item"><i class="bi bi-bar-chart-line"></i> Analytics</a>
      </div>
      <div class="xnx-sidebar-bottom">
        <div class="xnx-sidebar-user">
          <div class="xnx-avatar" id="sidebarAvatar">--</div>
          <div>
            <div class="user-name" id="sidebarNombre">Cargando…</div>
            <div class="user-role" id="sidebarRol">—</div>
          </div>
          <button class="btn btn-sm ms-auto p-0 text-white-50 border-0 bg-transparent" data-bs-toggle="tooltip"
            title="Cerrar sesión" onclick="window.location.href='Login'">
            <i class="bi bi-box-arrow-right"></i>
          </button>
        </div>
      </div>
    </aside>

    <!-- ══ MAIN ══ -->
    <main class="xnx-main">
      <div class="xnx-topbar">
        <div>
          <span class="xnx-topbar-title">Tareas</span>
          <span class="xnx-topbar-sub" id="topbarSub">Cargando…</span>
        </div>
        <div class="xnx-topbar-right">
          <select class="form-select form-select-sm" id="filtroProyecto" style="width:auto">
            <option value="">Todos los proyectos</option>
          </select>
          <button class="btn btn-primary btn-sm px-3" data-bs-toggle="modal" data-bs-target="#modalTarea" onclick="abrirModalNueva()">
            <i class="bi bi-plus-lg me-1"></i>Nueva tarea
          </button>
        </div>
      </div>

      <div class="xnx-content">

        <!-- Stats rápidos -->
        <div class="tareas-stats">
          <div class="tarea-stat-card">
            <div class="tarea-stat-icon" style="background:var(--blue-50)">
              <i class="bi bi-list-check" style="color:var(--blue-500)"></i>
            </div>
            <div>
              <div class="tarea-stat-num" id="statTotal">0</div>
              <div class="tarea-stat-label">Total tareas</div>
            </div>
          </div>
          <div class="tarea-stat-card">
            <div class="tarea-stat-icon" style="background:rgba(16,185,129,0.1)">
              <i class="bi bi-check2-circle" style="color:var(--success)"></i>
            </div>
            <div>
              <div class="tarea-stat-num" id="statCompletadas">0</div>
              <div class="tarea-stat-label">Completadas</div>
            </div>
          </div>
          <div class="tarea-stat-card">
            <div class="tarea-stat-icon" style="background:rgba(245,158,11,0.1)">
              <i class="bi bi-hourglass-split" style="color:var(--warning)"></i>
            </div>
            <div>
              <div class="tarea-stat-num" id="statProgreso">0</div>
              <div class="tarea-stat-label">En progreso</div>
            </div>
          </div>
          <div class="tarea-stat-card">
            <div class="tarea-stat-icon" style="background:rgba(239,68,68,0.1)">
              <i class="bi bi-exclamation-circle" style="color:var(--danger)"></i>
            </div>
            <div>
              <div class="tarea-stat-num" id="statVencidas">0</div>
              <div class="tarea-stat-label">Vencidas</div>
            </div>
          </div>
        </div>

        <!-- Toolbar filtros -->
        <div class="tareas-toolbar">
          <button class="btn btn-primary btn-sm rounded-pill px-3 filtro-btn active" data-filtro="todas">Todas</button>
          <button class="btn btn-outline-secondary btn-sm rounded-pill px-3 filtro-btn" data-filtro="Por Hacer">Pendientes</button>
          <button class="btn btn-outline-secondary btn-sm rounded-pill px-3 filtro-btn" data-filtro="En Progreso">En progreso</button>
          <button class="btn btn-outline-secondary btn-sm rounded-pill px-3 filtro-btn" data-filtro="Completada">Completadas</button>
          <button class="btn btn-outline-danger btn-sm rounded-pill px-3 filtro-btn" data-filtro="vencidas">Vencidas</button>
          <div class="ms-auto">
            <div class="input-group input-group-sm" style="width:210px">
              <span class="input-group-text bg-light border-secondary-subtle">
                <i class="bi bi-search text-secondary"></i>
              </span>
              <input type="search" class="form-control bg-light border-secondary-subtle border-start-0"
                id="buscarTarea" placeholder="Buscar tarea..." />
            </div>
          </div>
        </div>

        <!-- Tabla de tareas -->
        <div class="xnx-card">
          <table class="tareas-table">
            <thead>
              <tr>
                <th style="width:38%">Tarea</th>
                <th>Proyecto</th>
                <th>Estado</th>
                <th>Asignado</th>
                <th>Vence</th>
                <th style="width:36px"></th>
              </tr>
            </thead>
            <tbody id="tareasTbody">
              <tr><td colspan="6" class="text-center text-muted py-4">Cargando tareas…</td></tr>
            </tbody>
          </table>
        </div>

      </div><!-- /xnx-content -->
    </main>
  </div>

  <!-- ══ MODAL: Nueva / Editar tarea ══ -->
  <div class="modal fade" id="modalTarea" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <form id="formTarea">
          <div class="modal-header">
            <h5 class="modal-title" id="modalTareaTitulo">Nueva tarea</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <input type="hidden" id="tareaId" value="" />

            <div class="mb-3">
              <label class="form-label">Título</label>
              <input type="text" class="form-control" id="tareaTitulo" minlength="5" maxlength="200" required />
              <div class="invalid-feedback" id="errTitulo"></div>
            </div>

            <div class="mb-3">
              <label class="form-label">Descripción</label>
              <textarea class="form-control" id="tareaDescripcion" rows="3"></textarea>
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Proyecto</label>
                <select class="form-select" id="tareaProyecto" required>
                  <option value="">Selecciona un proyecto</option>
                </select>
                <div class="invalid-feedback" id="errProyecto"></div>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Estado</label>
                <select class="form-select" id="tareaEstado">
                  <option value="Por Hacer">Por hacer</option>
                  <option value="En Progreso">En progreso</option>
                  <option value="En Revisión">En revisión</option>
                  <option value="Completada">Completada</option>
                </select>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label">Fecha de vencimiento</label>
              <input type="date" class="form-control" id="tareaFecha" />
            </div>

            <div class="alert alert-danger d-none" id="formError"></div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-danger me-auto d-none" id="btnEliminarTarea" onclick="eliminarTareaActual()">
              <i class="bi bi-trash me-1"></i>Eliminar
            </button>
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
            <button type="submit" class="btn btn-primary" id="btnGuardarTarea">Guardar</button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Toast de notificaciones -->
  <div class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index:1080">
    <div id="toastNotif" class="toast align-items-center text-white border-0" role="alert">
      <div class="d-flex">
        <div class="toast-body" id="toastNotifBody">Mensaje</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  <script src="{{ asset('assets/js/app.js') }}"></script>
  <script>
    /* ════════════════════════════════════════════════════════
     *  Tareas.html — lógica de conexión con controller/tareas.php
     * ════════════════════════════════════════════════════════ */

    const API_URL = '../controller/tareas.php';

    let TAREAS = [];
    let PROYECTOS = [];
    let filtroActivo = 'todas';
    let textoBusqueda = '';

    const modalTareaEl = document.getElementById('modalTarea');
    const modalTarea = new bootstrap.Modal(modalTareaEl);
    const toastEl = document.getElementById('toastNotif');
    const toast = new bootstrap.Toast(toastEl, { delay: 3500 });

    function mostrarToast(mensaje, tipo = 'success') {
      const colores = { success: '#10b981', danger: '#ef4444', warning: '#f59e0b' };
      toastEl.style.backgroundColor = colores[tipo] || colores.success;
      document.getElementById('toastNotifBody').textContent = mensaje;
      toast.show();
    }

    function escapeHtml(str) {
      if (str === null || str === undefined) return '';
      const div = document.createElement('div');
      div.textContent = str;
      return div.innerHTML;
    }

    function formatearFecha(fechaStr) {
      if (!fechaStr) return '—';
      const f = new Date(fechaStr + 'T00:00:00');
      if (isNaN(f.getTime())) return '—';
      return f.toLocaleDateString('es-CO', { day: '2-digit', month: 'short' });
    }

    /* ── Cargar datos iniciales (usuario + proyectos + tareas) ── */
    async function cargarInit() {
      try {
        const res = await fetch(`${API_URL}?action=init`, { credentials: 'same-origin' });
        const json = await res.json();

        if (res.status === 401) {
          window.location.href = 'Login.html';
          return;
        }

        if (!json.success) {
          mostrarToast(json.message || 'Error al cargar datos', 'danger');
          return;
        }

        // Usuario en sidebar
        const u = json.data.usuario;
        document.getElementById('sidebarAvatar').textContent = u.iniciales;
        document.getElementById('sidebarNombre').textContent = `${u.nombres} ${u.apellidos}`;
        document.getElementById('sidebarRol').textContent = u.nombre_rol || u.cargo || 'Colaborador';

        // Proyectos
        PROYECTOS = json.data.proyectos;
        const selectFiltro = document.getElementById('filtroProyecto');
        const selectModal = document.getElementById('tareaProyecto');
        selectFiltro.innerHTML = '<option value="">Todos los proyectos</option>';
        selectModal.innerHTML = '<option value="">Selecciona un proyecto</option>';
        PROYECTOS.forEach(p => {
          selectFiltro.insertAdjacentHTML('beforeend', `<option value="${p.id_proyecto}">${escapeHtml(p.nombre)}</option>`);
          selectModal.insertAdjacentHTML('beforeend', `<option value="${p.id_proyecto}">${escapeHtml(p.nombre)}</option>`);
        });

        // Tareas + stats
        TAREAS = json.data.tareas;
        pintarStats(json.data.stats);
        pintarTareas();

      } catch (err) {
        console.error(err);
        mostrarToast('No se pudo conectar con el servidor', 'danger');
        document.getElementById('tareasTbody').innerHTML =
          `<tr><td colspan="6" class="text-center text-danger py-4">Error de conexión con el servidor</td></tr>`;
      }
    }

    function pintarStats(stats) {
      document.getElementById('statTotal').textContent = stats.total;
      document.getElementById('statCompletadas').textContent = stats.completadas;
      document.getElementById('statProgreso').textContent = stats.en_progreso;
      document.getElementById('statVencidas').textContent = stats.vencidas;
      document.getElementById('topbarSub').textContent = `${stats.total} tareas · ${stats.vencidas} vencidas`;
    }

    /* ── Filtrado en cliente (rápido, sin recargar) ── */
    function tareasFiltradas() {
      const proyectoSeleccionado = document.getElementById('filtroProyecto').value;

      return TAREAS.filter(t => {
        if (proyectoSeleccionado && String(t.id_proyecto) !== proyectoSeleccionado) return false;

        if (filtroActivo === 'vencidas' && !t.vencida) return false;
        if (filtroActivo !== 'todas' && filtroActivo !== 'vencidas' && t.estado !== filtroActivo) return false;

        if (textoBusqueda && !t.titulo.toLowerCase().includes(textoBusqueda.toLowerCase())) return false;

        return true;
      });
    }

    const ESTADO_CLASES = {
      'Por Hacer':    { clase: 'estado-pendiente', icono: 'bi-circle' },
      'En Progreso':  { clase: 'estado-progreso',  icono: 'bi-circle-half' },
      'En Revisión':  { clase: 'estado-revision',  icono: 'bi-eye' },
      'Completada':   { clase: 'estado-completada',icono: 'bi-check-circle' },
    };

    const COLORES_PROYECTO = ['#7c3aed', '#0891b2', '#10b981', '#f59e0b', '#ef4444', '#6b7280'];
    function colorProyecto(id) {
      return COLORES_PROYECTO[id % COLORES_PROYECTO.length];
    }

    function pintarTareas() {
      const tbody = document.getElementById('tareasTbody');
      const lista = tareasFiltradas();

      if (lista.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-4">No hay tareas que coincidan</td></tr>`;
        return;
      }

      tbody.innerHTML = lista.map(t => {
        const estadoInfo = ESTADO_CLASES[t.estado] || ESTADO_CLASES['Por Hacer'];
        const completada = t.estado === 'Completada';
        const asignado = t.usuario_nombres
          ? `${t.usuario_nombres.charAt(0)}${(t.usuario_apellidos || '').charAt(0)}`.toUpperCase()
          : '—';
        const nombreAsignado = t.usuario_nombres ? `${t.usuario_nombres} ${(t.usuario_apellidos || '').charAt(0)}.` : 'Sin asignar';

        const fechaClase = t.vencida ? 'vencida' : '';
        const fechaIcono = t.vencida ? 'bi-calendar-x' : (completada ? 'bi-check2' : 'bi-calendar3');
        const fechaEstilo = completada ? 'color:var(--success)' : '';

        return `
          <tr data-id="${t.id_tarea}" style="${completada ? 'opacity:0.6' : ''}">
            <td>
              <div class="tarea-titulo">
                <div class="check-circle ${completada ? 'done' : ''}" onclick="toggleCompletada(event, ${t.id_tarea})">
                  ${completada ? '<i class="bi bi-check"></i>' : ''}
                </div>
                <span class="tarea-titulo-link" onclick="abrirModalEditar(${t.id_tarea})" style="cursor:pointer">
                  ${completada ? `<s>${escapeHtml(t.titulo)}</s>` : escapeHtml(t.titulo)}
                </span>
              </div>
            </td>
            <td>
              <div class="tarea-proyecto">
                <span class="tarea-proyecto-dot" style="background:${colorProyecto(t.id_proyecto)}"></span>
                ${escapeHtml(t.proyecto_nombre)}
              </div>
            </td>
            <td><span class="tarea-estado ${estadoInfo.clase}"><i class="bi ${estadoInfo.icono} me-1"></i>${t.estado}</span></td>
            <td>
              <div class="d-flex align-items-center gap-2">
                <div class="xnx-avatar sm">${asignado}</div>
                <span class="small text-muted">${escapeHtml(nombreAsignado)}</span>
              </div>
            </td>
            <td><span class="tarea-fecha ${fechaClase}" style="${fechaEstilo}"><i class="bi ${fechaIcono} me-1"></i>${formatearFecha(t.fecha_vencimiento)}</span></td>
            <td>
              <button class="btn btn-sm p-0 text-muted border-0" onclick="abrirModalEditar(${t.id_tarea})">
                <i class="bi bi-three-dots"></i>
              </button>
            </td>
          </tr>
        `;
      }).join('');
    }

    /* ── Marcar/desmarcar como completada directamente desde la tabla ── */
    async function toggleCompletada(event, id) {
      event.stopPropagation();
      const tarea = TAREAS.find(t => t.id_tarea === id);
      if (!tarea) return;

      const nuevoEstado = tarea.estado === 'Completada' ? 'Por Hacer' : 'Completada';

      const body = new URLSearchParams({ action: 'actualizar', id, estado: nuevoEstado });
      try {
        const res = await fetch(API_URL, { method: 'POST', body, credentials: 'same-origin' });
        const json = await res.json();

        if (!json.success) {
          mostrarToast(json.message || 'No se pudo actualizar', 'danger');
          return;
        }

        tarea.estado = nuevoEstado;
        tarea.vencida = nuevoEstado === 'Completada' ? false : tarea.vencida;
        await recalcularStatsLocal();
        pintarTareas();
        mostrarToast(nuevoEstado === 'Completada' ? 'Tarea completada' : 'Tarea reabierta');
      } catch (err) {
        console.error(err);
        mostrarToast('Error de conexión', 'danger');
      }
    }

    async function recalcularStatsLocal() {
      const total = TAREAS.length;
      const completadas = TAREAS.filter(t => t.estado === 'Completada').length;
      const en_progreso = TAREAS.filter(t => t.estado === 'En Progreso').length;
      const vencidas = TAREAS.filter(t => t.vencida).length;
      pintarStats({ total, completadas, en_progreso, vencidas });
    }

    /* ── Modal: nueva tarea ── */
    function abrirModalNueva() {
      document.getElementById('formTarea').reset();
      document.getElementById('tareaId').value = '';
      document.getElementById('modalTareaTitulo').textContent = 'Nueva tarea';
      document.getElementById('btnEliminarTarea').classList.add('d-none');
      limpiarErroresForm();
    }

    /* ── Modal: editar tarea existente ── */
    function abrirModalEditar(id) {
      const t = TAREAS.find(x => x.id_tarea === id);
      if (!t) return;

      document.getElementById('tareaId').value = t.id_tarea;
      document.getElementById('tareaTitulo').value = t.titulo;
      document.getElementById('tareaDescripcion').value = t.descripcion || '';
      document.getElementById('tareaProyecto').value = t.id_proyecto;
      document.getElementById('tareaEstado').value = t.estado;
      document.getElementById('tareaFecha').value = t.fecha_vencimiento || '';
      document.getElementById('modalTareaTitulo').textContent = 'Editar tarea';
      document.getElementById('btnEliminarTarea').classList.remove('d-none');
      limpiarErroresForm();

      modalTarea.show();
    }

    function limpiarErroresForm() {
      document.getElementById('formError').classList.add('d-none');
      ['tareaTitulo', 'tareaProyecto'].forEach(id => document.getElementById(id).classList.remove('is-invalid'));
    }

    /* ── Guardar (crear o actualizar) ── */
    document.getElementById('formTarea').addEventListener('submit', async (e) => {
      e.preventDefault();
      limpiarErroresForm();

      const id = document.getElementById('tareaId').value;
      const titulo = document.getElementById('tareaTitulo').value.trim();
      const descripcion = document.getElementById('tareaDescripcion').value.trim();
      const proyecto_id = document.getElementById('tareaProyecto').value;
      const estado = document.getElementById('tareaEstado').value;
      const fecha_vencimiento = document.getElementById('tareaFecha').value;

      const btnGuardar = document.getElementById('btnGuardarTarea');
      btnGuardar.disabled = true;
      btnGuardar.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>Guardando...`;

      const params = new URLSearchParams({
        action: id ? 'actualizar' : 'crear',
        titulo, descripcion, proyecto_id, estado, fecha_vencimiento
      });
      if (id) params.set('id', id);

      try {
        const res = await fetch(API_URL, { method: 'POST', body: params, credentials: 'same-origin' });
        const json = await res.json();

        if (!json.success) {
          if (json.errors && Object.keys(json.errors).length) {
            for (const campo in json.errors) {
              const inputId = campo === 'titulo' ? 'tareaTitulo' : (campo === 'proyecto_id' ? 'tareaProyecto' : null);
              const errId = campo === 'titulo' ? 'errTitulo' : (campo === 'proyecto_id' ? 'errProyecto' : null);
              if (inputId) {
                document.getElementById(inputId).classList.add('is-invalid');
                document.getElementById(errId).textContent = json.errors[campo];
              }
            }
          } else {
            document.getElementById('formError').textContent = json.message;
            document.getElementById('formError').classList.remove('d-none');
          }
          return;
        }

        mostrarToast(json.message || 'Guardado correctamente');
        modalTarea.hide();
        await cargarInit();

      } catch (err) {
        console.error(err);
        document.getElementById('formError').textContent = 'Error de conexión con el servidor';
        document.getElementById('formError').classList.remove('d-none');
      } finally {
        btnGuardar.disabled = false;
        btnGuardar.innerHTML = 'Guardar';
      }
    });

    /* ── Eliminar tarea actual (desde el modal) ── */
    async function eliminarTareaActual() {
      const id = document.getElementById('tareaId').value;
      if (!id) return;

      if (!confirm('¿Seguro que deseas eliminar esta tarea? Esta acción no se puede deshacer.')) return;

      try {
        const res = await fetch(`${API_URL}?action=eliminar&id=${id}`, { credentials: 'same-origin' });
        const json = await res.json();

        if (!json.success) {
          mostrarToast(json.message || 'No se pudo eliminar', 'danger');
          return;
        }

        mostrarToast('Tarea eliminada');
        modalTarea.hide();
        await cargarInit();

      } catch (err) {
        console.error(err);
        mostrarToast('Error de conexión', 'danger');
      }
    }

    /* ── Filtros de la toolbar ── */
    document.querySelectorAll('.filtro-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.filtro-btn').forEach(b => {
          b.classList.remove('active', 'btn-primary', 'btn-danger');
          b.classList.add(b.dataset.filtro === 'vencidas' ? 'btn-outline-danger' : 'btn-outline-secondary');
        });
        btn.classList.add('active');
        if (btn.dataset.filtro === 'vencidas') {
          btn.classList.remove('btn-outline-danger');
          btn.classList.add('btn-danger');
        } else {
          btn.classList.remove('btn-outline-secondary');
          btn.classList.add('btn-primary');
        }
        filtroActivo = btn.dataset.filtro;
        pintarTareas();
      });
    });

    document.getElementById('filtroProyecto').addEventListener('change', pintarTareas);

    let debounceBusqueda;
    document.getElementById('buscarTarea').addEventListener('input', (e) => {
      clearTimeout(debounceBusqueda);
      debounceBusqueda = setTimeout(() => {
        textoBusqueda = e.target.value.trim();
        pintarTareas();
      }, 250);
    });

    // Reset del modal al cerrarlo
    modalTareaEl.addEventListener('hidden.bs.modal', () => {
      document.getElementById('formTarea').reset();
      limpiarErroresForm();
    });

    // Carga inicial
    cargarInit();
  </script>
</body>

</html>