/**
 * Mantiene consistente la identidad visible en todas las pantallas protegidas.
 * El cargo proviene siempre de la cuenta autenticada, no del rol técnico.
 */
(function () {
  if (!window.__xincronixCrudEvents) {
    const fetchOriginal = window.fetch.bind(window);
    window.fetch = async function (...args) {
      const request = args[0];
      const options = args[1] || {};
      const method = String(options.method || (request && request.method) || 'GET').toUpperCase();
      const response = await fetchOriginal(...args);
      if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method) && response.ok) {
        window.dispatchEvent(new CustomEvent('xincronix:crud'));
      }
      return response;
    };
    window.__xincronixCrudEvents = true;
  }

  async function cargarUsuarioSesion() {
    try {
      const response = await fetch('/api/auth/me', {
        credentials: 'same-origin',
        headers: { Accept: 'application/json' }
      });
      if (!response.ok) return;

      const payload = await response.json();
      if (!payload.success || !payload.data) return;

      const usuario = payload.data;
      const nombre = `${usuario.nombres || ''} ${usuario.apellidos || ''}`.trim() || 'Usuario';
      const cargo = usuario.cargo || usuario.rol || 'Empleado';
      const iniciales = nombre.split(/\s+/).map(parte => parte.charAt(0))
        .join('').substring(0, 2).toUpperCase() || 'US';

      document.querySelectorAll('.user-name, #sidebarNombre, #assistantUserName, #userName')
        .forEach(elemento => elemento.textContent = nombre);
      document.querySelectorAll('.user-role, #sidebarRol, #assistantUserRole, #userRole')
        .forEach(elemento => elemento.textContent = cargo);
      document.querySelectorAll('.xnx-sidebar .xnx-avatar, #sidebarAvatar, #assistantUserAvatar, #userAvatar')
        .forEach(elemento => elemento.textContent = iniciales);
      actualizarInsigniasModulos();
    } catch (error) {
      console.error('No se pudo cargar el usuario autenticado:', error);
    }

    async function actualizarInsigniasModulos() {
      try {
        const response = await fetch('/api/dashboard', { credentials: 'same-origin', headers: { Accept: 'application/json' } });
        const payload = response.ok ? await response.json() : {};
        const stats = payload?.data?.estadisticas || {};
        const conteos = {
          proyectos: Number(stats.proyectos_activos || 0),
          tareas: Number(stats.tareas_total || 0),
          equipos: Number(stats.equipos_total || 0),
          automatizaciones: Number(stats.automatizaciones_total || 0),
          analytics: Number(stats.tareas_total || 0)
        };
        if (!response.ok || !payload.success && payload.status !== 'success') {
          const [proyectos, equipos, automatizaciones] = await Promise.all([
            fetch('/api/proyectos?action=listar', { credentials: 'same-origin' }).then(r => r.ok ? r.json() : {}),
            fetch('/api/equipos?action=init', { credentials: 'same-origin' }).then(r => r.ok ? r.json() : {}),
            fetch('/api/automatizaciones', { credentials: 'same-origin' }).then(r => r.ok ? r.json() : {})
          ]);
          conteos.proyectos = Number(proyectos?.data?.total || proyectos?.data?.proyectos?.length || 0);
          conteos.equipos = Number(equipos?.data?.equipos?.length || 0);
          conteos.automatizaciones = Number(automatizaciones?.data?.flujos?.length || 0);
        }
        const conteosPorModulo = [
          { match: /proyecto/i, valor: conteos.proyectos },
          { match: /tarea/i, valor: conteos.tareas },
          { match: /equipo/i, valor: conteos.equipos },
          { match: /asistente/i, valor: 0 },
          { match: /automatizacion/i, valor: conteos.automatizaciones },
          { match: /analytics/i, valor: conteos.analytics }
        ];
        document.querySelectorAll('.xnx-sidebar a.xnx-sidebar-item').forEach(enlace => {
          const conteo = conteosPorModulo.find(item => item.match.test(enlace.textContent || ''));
          if (!conteo || typeof conteo.valor !== 'number') return;
          let badge = enlace.querySelector('.xnx-sidebar-badge');
          if (!badge) {
            badge = document.createElement('span');
            badge.className = 'xnx-sidebar-badge';
            enlace.appendChild(badge);
          }
          badge.textContent = conteo.valor;
          badge.classList.toggle('d-none', conteo.valor < 1);
        });
      } catch (error) {
        console.error('No se pudo actualizar la insignia de proyectos:', error);
      }
    }
    window.actualizarInsigniasModulos = actualizarInsigniasModulos;
    window.addEventListener('xincronix:crud', actualizarInsigniasModulos);
    window.setInterval(actualizarInsigniasModulos, 10000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', cargarUsuarioSesion);
  } else {
    cargarUsuarioSesion();
  }
})();
