<!DOCTYPE html>
<html lang="es">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Xincronix — Dashboard</title>

  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" />
  <link rel="stylesheet" href="{{ asset('assets/css/Index.css') }}" />
  <link rel="stylesheet" href="{{ asset('assets/css/Proyecto.css') }}" />
  <link rel="stylesheet" href="{{ asset('assets/css/toast.css') }}" />
  <link rel="icon" href="{{ asset('assets/img/logo xincronix.png') }}" />
  
  <!-- Chart.js para gráficos -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
</head>

<body>

  <div class="app-shell">

    <!-- ══════════════ SIDEBAR ══════════════ -->
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
        <a href="Panel" class="xnx-sidebar-item active" data-page="Panel">
          <i class="bi bi-grid"></i> Dashboard
        </a>
        <a href="Proyecto" class="xnx-sidebar-item" data-page="Proyecto">
          <i class="bi bi-kanban"></i> Proyectos
          <span class="xnx-sidebar-badge" id="badgeProyectos">0</span>
        </a>
        <a href="Tareas" class="xnx-sidebar-item" data-page="Tareas">
          <i class="bi bi-clock"></i> Tareas
        </a>
        <a href="Equipos" class="xnx-sidebar-item">
          <i class="bi bi-people"></i> Equipo
        </a>
      </div>

      <div class="xnx-sidebar-section">
        <div class="xnx-sidebar-section-label">IA &amp; Automatizacion</div>
        <a href="Asistente" class="xnx-sidebar-item"><i class="bi bi-chat-dots"></i> Asistente virtual</a>
        <a href="Automatizaciones" class="xnx-sidebar-item"><i class="bi bi-arrow-repeat"></i> Automatizaciones</a>
      </div>

      <div class="xnx-sidebar-section">
        <div class="xnx-sidebar-section-label">Reportes</div>
        <a href="Analytics" class="xnx-sidebar-item">
          <i class="bi bi-bar-chart-line"></i> Analytics
        </a>
      </div>

      <!-- ⚡ ZONA DEL USUARIO - DATOS DINÁMICOS -->
      <div class="xnx-sidebar-bottom">
        <div class="xnx-sidebar-user">
          <!-- El avatar se actualizará con JS -->
          <div class="xnx-avatar" id="userAvatar">--</div>
          <div>
            <!-- Nombre y cargo se actualizarán con JS -->
            <div class="user-name" id="userName">Cargando...</div>
            <div class="user-role" id="userRole">--</div>
          </div>
          <button class="btn btn-sm ms-auto p-0 text-white-50 border-0 bg-transparent" 
                  data-bs-toggle="tooltip" title="Cerrar sesión" 
                  onclick="window.location.href='Login'">
            <i class="bi bi-box-arrow-right"></i>
          </button>
        </div>
      </div>
    </aside>

    <!-- ══════════════ MAIN ══════════════ -->
    <main class="xnx-main">

      <!-- Topbar -->
      <div class="xnx-topbar">
        <div>
          <!-- ⚡ Saludo dinámico -->
          <span class="xnx-topbar-title" id="topbarSaludo">Buen día 👋</span>
          <span class="xnx-topbar-sub" id="topbarDate"></span>
        </div>
        <div class="xnx-topbar-right">
          <!-- Search -->
          <div class="input-group" style="width:220px">
            <span class="input-group-text bg-light border-end-0 border-secondary-subtle">
              <i class="bi bi-search text-secondary" style="font-size:12px"></i>
            </span>
            <input type="search" class="form-control form-control-sm bg-light border-start-0 border-secondary-subtle"
              placeholder="Buscar en Xincronix..." />
          </div>
          <!-- Notifications -->
          <button class="btn btn-outline-secondary btn-sm position-relative" data-bs-toggle="tooltip"
            title="Notificaciones">
            <i class="bi bi-bell"></i>
            <span id="badgeNotificaciones"
              class="position-absolute top-0 start-100 translate-middle p-1 bg-danger border border-light rounded-circle">
              <span class="visually-hidden">Notificaciones</span>
            </span>
          </button>
          <button class="btn btn-primary btn-sm px-3">
            <i class="bi bi-plus-lg me-1"></i>Nuevo
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="xnx-content">

        <!-- ⚡ Stats - Valores dinámicos -->
        <div class="stats-row">
          <div class="stat-card">
            <div class="stat-icon-wrap float-end"><i class="bi bi-kanban"></i></div>
            <div class="stat-label">Proyectos activos</div>
            <div class="stat-value" id="statProyectos">--</div>
            <div class="stat-trend" id="statProyectosTrend"><i class="bi bi-arrow-up-short"></i> Cargando...</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon-wrap float-end" style="background:rgba(16,185,129,0.1)">
              <i class="bi bi-check2-circle" style="color:var(--success)"></i>
            </div>
            <div class="stat-label">Tareas completadas</div>
            <div class="stat-value" id="statTareas">--</div>
            <div class="stat-trend" id="statTareasTrend"><i class="bi bi-arrow-up-short"></i> Cargando...</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon-wrap float-end" style="background:rgba(245,158,11,0.1)">
              <i class="bi bi-cpu" style="color:var(--warning)"></i>
            </div>
            <div class="stat-label">Agentes activos</div>
            <div class="stat-value" id="statAgentes">--</div>
            <div class="stat-trend" style="color:var(--warning)" id="statAgentesTrend">
              <i class="bi bi-dot fs-5"></i> Cargando...
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon-wrap float-end" style="background:rgba(239,68,68,0.1)">
              <i class="bi bi-exclamation-triangle" style="color:var(--danger)"></i>
            </div>
            <div class="stat-label">Issues abiertos</div>
            <div class="stat-value" id="statIssues">--</div>
            <div class="stat-trend down" id="statIssuesTrend">
              <i class="bi bi-arrow-down-short"></i> Cargando...
            </div>
          </div>
        </div>

        <!-- Dashboard grid -->
        <div class="dashboard-grid">

          <!-- Actividad reciente -->
          <div class="xnx-card">
            <div class="xnx-card-header">
              <span class="xnx-card-title">Actividad reciente</span>
              <span class="xnx-card-action">Ver todo</span>
            </div>
            <div class="xnx-card-body p-0">
              <!-- ⚡ Contenedor de actividades dinámicas -->
              <div class="px-3" id="actividadesContainer">
                <!-- Se llenará con JS -->
                <div class="text-center py-4 text-muted">
                  <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                  Cargando actividades...
                </div>
              </div>
            </div>
          </div>

          <!-- Columna derecha -->
          <div class="d-flex flex-column gap-3">

            <!-- Estado agentes -->
            <div class="xnx-card">
              <div class="xnx-card-header">
                <span class="xnx-card-title">Estado de Agentes</span>
                <a href="Agentes.html" class="xnx-card-action">Gestionar</a>
              </div>
              <div class="xnx-card-body p-0 px-3" id="agentesContainer">
                <!-- Se llenará con JS -->
                <div class="text-center py-4 text-muted">
                  <small>Cargando agentes...</small>
                </div>
              </div>
            </div>

            <!-- Progreso proyectos -->
            <div class="xnx-card">
              <div class="xnx-card-header">
                <span class="xnx-card-title">Progreso proyectos</span>
                <a href="Proyecto.html" class="xnx-card-action">Ver kanban</a>
              </div>
              <div class="xnx-card-body" id="progresoContainer">
                <!-- Se llenará con JS -->
                <div class="text-center py-4 text-muted">
                  <small>Cargando proyectos...</small>
                </div>
              </div>
            </div>

          </div><!-- /col derecha -->
        </div><!-- /dashboard-grid -->

      </div><!-- /xnx-content -->
    </main>
  </div>

  <!-- ⚡ Toast para notificaciones -->
  <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 9999">
    <div id="liveToast" class="toast align-items-center text-bg-success border-0" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body" id="toastMessage"></div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  
  <!-- ⚡ Panel.js - Carga los datos del usuario y dashboard -->
  <script>
  /**
   * Panel.js — Dashboard dinámico para Xincronix
   * Carga los datos del usuario desde la sesión PHP
   */
  
  const DASHBOARD_ENDPOINT = '../controller/dashboard.php';
  const LOGOUT_ENDPOINT = '../controller/logout.php';
  
  // Variable global para almacenar datos del usuario
  let usuarioActual = null;
  
  document.addEventListener('DOMContentLoaded', () => {
      configurarFechaActual();
      inicializarTooltips();
      cargarDashboard();
  });
  
  /**
   * Carga los datos del dashboard desde el servidor
   * El servidor lee $_SESSION y devuelve los datos del usuario logueado
   */
  async function cargarDashboard() {
    try {
        console.log('🔄 Cargando dashboard...');
        
        const response = await fetch(DASHBOARD_ENDPOINT, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'include'
        });

        console.log('📡 Status:', response.status);

        if (response.status === 401) {
            console.warn('⚠️ No hay sesión activa o el token expiró. Redirigiendo al login...');
            localStorage.removeItem('usuarioActual');
            window.location.href = 'Login.html';
            return;
        }

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const result = await response.json();
        console.log('✅ Datos recibidos:', result);

        if (result.status === 'error') {
            throw new Error(result.message || 'Error al cargar datos');
        }

        usuarioActual = result.data.usuario;
        
        actualizarDatosUsuario(result.data.usuario);
        actualizarEstadisticas(result.data.estadisticas);
        actualizarActividades(result.data.actividades);
        actualizarProyectos(result.data.proyectos);
        
        console.log('✅ Dashboard cargado correctamente');

    } catch (error) {
        console.error('❌ Error al cargar dashboard:', error);
        mostrarToast('No se pudieron cargar los datos. Verifica tu conexión.', 'error');
    }
}
  
  /**
   * Actualiza los datos del usuario en el HTML
   * Toma los datos de $_SESSION que el servidor devolvió
   */
  function actualizarDatosUsuario(usuario) {
      if (!usuario) return;
      
      console.log('👤 Actualizando datos del usuario:', usuario);
      
      // 1. Nombre en el topbar (saludo)
      const topbarSaludo = document.getElementById('topbarSaludo');
      if (topbarSaludo && usuario.nombre) {
          const primerNombre = usuario.nombre.split(' ')[0];
          topbarSaludo.textContent = `Buen día, ${primerNombre} 👋`;
      }
      
      // 2. Nombre completo en el sidebar
      const userName = document.getElementById('userName');
      if (userName) {
          userName.textContent = usuario.nombre || 'Usuario';
      }
      
      // 3. Cargo o rol en el sidebar
      const userRole = document.getElementById('userRole');
      if (userRole) {
          userRole.textContent = usuario.cargo || usuario.rol || 'Sin cargo';
      }
      
      // 4. Avatar con iniciales
      const userAvatar = document.getElementById('userAvatar');
      if (userAvatar && usuario.nombre) {
          const iniciales = usuario.nombre
              .split(' ')
              .map(palabra => palabra.charAt(0))
              .join('')
              .substring(0, 2)
              .toUpperCase();
          userAvatar.textContent = iniciales;
          
          // Color basado en el nombre
          const color = generarColor(usuario.nombre);
          userAvatar.style.background = color;
      }
      
      // 5. Guardar en localStorage por si se necesita en otras páginas
      localStorage.setItem('usuarioActual', JSON.stringify(usuario));
  }
  
  /**
   * Actualiza las 4 tarjetas de estadísticas
   */
  function actualizarEstadisticas(estadisticas) {
      if (!estadisticas) return;
      
      // Proyectos activos
      const statProyectos = document.getElementById('statProyectos');
      const statProyectosTrend = document.getElementById('statProyectosTrend');
      if (statProyectos) statProyectos.textContent = estadisticas.proyectos_activos;
      if (statProyectosTrend) {
          statProyectosTrend.innerHTML = `<i class="bi bi-arrow-up-short"></i> ${estadisticas.proyectos_este_mes} este mes`;
      }
      
      // Tareas completadas
      const statTareas = document.getElementById('statTareas');
      const statTareasTrend = document.getElementById('statTareasTrend');
      if (statTareas) statTareas.textContent = estadisticas.tareas_completadas;
      if (statTareasTrend) {
          statTareasTrend.innerHTML = `<i class="bi bi-arrow-up-short"></i> ${estadisticas.tareas_esta_semana} esta semana`;
      }
      
      // Agentes activos
      const statAgentes = document.getElementById('statAgentes');
      const statAgentesTrend = document.getElementById('statAgentesTrend');
      if (statAgentes) statAgentes.textContent = estadisticas.agentes_activos;
      if (statAgentesTrend) {
          statAgentesTrend.innerHTML = `<i class="bi bi-dot fs-5"></i> ${estadisticas.agentes_en_espera} en espera`;
      }
      
      // Issues abiertos
      const statIssues = document.getElementById('statIssues');
      const statIssuesTrend = document.getElementById('statIssuesTrend');
      if (statIssues) statIssues.textContent = estadisticas.issues_abiertos;
      if (statIssuesTrend) {
          statIssuesTrend.innerHTML = `<i class="bi bi-arrow-down-short"></i> ${estadisticas.issues_abiertos} pendientes`;
      }
      
      // Badges del sidebar
      const badgeProyectos = document.getElementById('badgeProyectos');
      if (badgeProyectos) badgeProyectos.textContent = estadisticas.proyectos_activos;
      
      const badgeAgentes = document.getElementById('badgeAgentes');
      if (badgeAgentes) badgeAgentes.textContent = estadisticas.agentes_activos;
  }
  
  /**
   * Actualiza la lista de actividad reciente
   */
  function actualizarActividades(actividades) {
      const container = document.getElementById('actividadesContainer');
      if (!container) return;
      
      if (!actividades || actividades.length === 0) {
          container.innerHTML = '<div class="text-center py-4 text-muted">No hay actividad reciente</div>';
          return;
      }
      
      let html = '';
      
      actividades.forEach(act => {
          const iniciales = act.usuario
              .split(' ')
              .map(n => n[0])
              .join('')
              .substring(0, 2)
              .toUpperCase();
          
          const color = generarColor(act.usuario);
          
          html += `
              <div class="activity-item">
                  <div class="xnx-avatar sm" style="background:${color}">${iniciales}</div>
                  <div>
                      <div class="activity-text">
                          <strong>${act.usuario}</strong> ${act.descripcion} <strong>${act.detalle}</strong>
                      </div>
                      <div class="activity-time">
                          <i class="bi bi-clock me-1"></i>${act.tiempo_relativo}
                      </div>
                  </div>
              </div>
          `;
      });
      
      container.innerHTML = html;
  }
  
  /**
   * Actualiza las barras de progreso de proyectos
   */
  function actualizarProyectos(proyectos) {
      const container = document.getElementById('progresoContainer');
      if (!container) return;
      
      if (!proyectos || proyectos.length === 0) {
          container.innerHTML = '<div class="text-center py-4 text-muted">No hay proyectos activos</div>';
          return;
      }
      
      let html = '';
      
      proyectos.forEach(proy => {
          let claseColor = '';
          if (proy.porcentaje >= 90) claseColor = 'green';
          else if (proy.porcentaje < 50) claseColor = 'orange';
          
          html += `
              <div class="mb-3">
                  <div class="d-flex justify-content-between mb-1">
                      <span class="small fw-500" style="color:var(--gray-700)">${proy.nombre}</span>
                      <span class="small fw-600">${proy.porcentaje}%</span>
                  </div>
                  <div class="xnx-progress">
                      <div class="xnx-progress-bar ${claseColor}" 
                           style="width:${proy.porcentaje}%; transition: width 1s ease-in-out;">
                      </div>
                  </div>
              </div>
          `;
      });
      
      container.innerHTML = html;
  }
  
  /**
   * Cierra la sesión del usuario
   */
  function cerrarSesion() {
      if (confirm('¿Estás seguro de cerrar sesión?')) {
          fetch(LOGOUT_ENDPOINT, {
              method: 'POST',
              credentials: 'include'
          })
          .then(() => {
              localStorage.removeItem('usuarioActual');
              window.location.href = 'Login.html';
          })
          .catch(() => {
              // Si falla el endpoint, limpiar localStorage e ir al login
              localStorage.removeItem('usuarioActual');
              window.location.href = 'Login.html';
          });
      }
  }
  
  /**
   * Configura la fecha actual
   */
  function configurarFechaActual() {
      const fechaEl = document.getElementById('topbarDate');
      if (!fechaEl) return;
  
      const opciones = { 
          weekday: 'long', 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
      };
      
      const fecha = new Date().toLocaleDateString('es-CO', opciones);
      fechaEl.textContent = fecha.charAt(0).toUpperCase() + fecha.slice(1);
  }
  
  /**
   * Inicializa tooltips de Bootstrap
   */
  function inicializarTooltips() {
      const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
      tooltips.forEach(el => {
          new bootstrap.Tooltip(el);
      });
  }
  
  /**
   * Genera un color basado en un string
   */
  function generarColor(str) {
      const colores = [
          '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
          '#8b5cf6', '#ec4899', '#06b6d4', '#f97316',
          '#6366f1', '#14b8a6', '#eab308', '#dc2626'
      ];
      
      let hash = 0;
      for (let i = 0; i < str.length; i++) {
          hash = str.charCodeAt(i) + ((hash << 5) - hash);
      }
      
      return colores[Math.abs(hash) % colores.length];
  }
  
  /**
   * Muestra un toast de notificación
   */
  function mostrarToast(mensaje, tipo = 'info') {
      const toastEl = document.getElementById('liveToast');
      const toastMsg = document.getElementById('toastMessage');
      
      if (!toastEl || !toastMsg) return;
      
      // Cambiar color según tipo
      toastEl.className = `toast align-items-center text-bg-${tipo === 'error' ? 'danger' : 'success'} border-0`;
      toastMsg.textContent = mensaje;
      
      const toast = new bootstrap.Toast(toastEl);
      toast.show();
  }
  </script>
</body>

</html>