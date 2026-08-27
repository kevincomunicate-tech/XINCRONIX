/**
 * Panel.js — Dashboard para Xincronix
 * Versión simplificada y funcional
 */

const DASHBOARD_ENDPOINT = '../controller/dashboard.php';

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Panel cargado');
    configurarFechaActual();
    cargarDashboard();
});

async function cargarDashboard() {
    try {
        console.log('📡 Solicitando datos a:', DASHBOARD_ENDPOINT);
        
        const response = await fetch(DASHBOARD_ENDPOINT, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        console.log('📡 Status de respuesta:', response.status);
        
        // Obtener el texto de la respuesta
        const text = await response.text();
        console.log('📡 Respuesta recibida:', text.substring(0, 200) + '...');
        
        // Intentar parsear como JSON
        let data;
        try {
            data = JSON.parse(text);
        } catch (e) {
            console.error('❌ Error al parsear JSON:', e);
            console.error('❌ Respuesta no es JSON válido:', text);
            throw new Error('El servidor no devolvió JSON válido');
        }
        
        console.log('✅ Datos parseados:', data);
        
        if (data.status === 'success') {
            // Actualizar la UI
            actualizarUsuario(data.data.usuario);
            actualizarEstadisticas(data.data.estadisticas);
            actualizarActividades(data.data.actividades);
            actualizarProyectos(data.data.proyectos);
            
            console.log('✅ Dashboard cargado correctamente');
            console.log('ℹ️ Modo:', data.data.modo || 'desconocido');
        } else {
            throw new Error(data.message || 'Error desconocido');
        }
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        // Mostrar error en la UI
        mostrarError(error.message);
    }
}

function actualizarUsuario(usuario) {
    console.log('👤 Actualizando usuario:', usuario);
    
    // Nombre en topbar
    const topbar = document.querySelector('.xnx-topbar-title');
    if (topbar && usuario.nombre) {
        const nombre = usuario.nombre.split(' ')[0];
        topbar.textContent = 'Buen día, ' + nombre + ' 👋';
    }
    
    // Sidebar - nombre
    const userName = document.querySelector('.user-name');
    if (userName) userName.textContent = usuario.nombre || 'Usuario';
    
    // Sidebar - cargo
    const userRole = document.querySelector('.user-role');
    if (userRole) userRole.textContent = usuario.cargo || usuario.rol || '';
    
    // Sidebar - avatar
    const avatar = document.querySelector('.xnx-avatar');
    if (avatar && usuario.nombre) {
        const iniciales = usuario.nombre
            .split(' ')
            .map(n => n[0])
            .join('')
            .substring(0, 2)
            .toUpperCase();
        avatar.textContent = iniciales;
        avatar.style.background = '#3b82f6';
    }
}

function actualizarEstadisticas(stats) {
    console.log('📊 Actualizando estadísticas:', stats);
    
    // Buscar las tarjetas de estadísticas
    const valores = document.querySelectorAll('.stat-value');
    const trends = document.querySelectorAll('.stat-trend');
    
    if (valores.length >= 4) {
        valores[0].textContent = stats.proyectos_activos;
        valores[1].textContent = stats.tareas_completadas;
        valores[2].textContent = stats.agentes_activos;
        valores[3].textContent = stats.issues_abiertos;
    }
    
    if (trends.length >= 4) {
        trends[0].innerHTML = '<i class="bi bi-arrow-up-short"></i> ' + stats.proyectos_este_mes + ' este mes';
        trends[1].innerHTML = '<i class="bi bi-arrow-up-short"></i> ' + stats.tareas_esta_semana + ' esta semana';
        trends[2].innerHTML = '<i class="bi bi-dot fs-5"></i> ' + stats.agentes_en_espera + ' en espera';
        trends[3].innerHTML = '<i class="bi bi-arrow-down-short"></i> ' + stats.issues_abiertos + ' pendientes';
    }
}

function actualizarActividades(actividades) {
    console.log('📝 Actualizando actividades:', actividades);
    
    // Buscar el contenedor de actividades
    const container = document.querySelector('.xnx-card-body .px-3');
    if (!container) return;
    
    if (!actividades || actividades.length === 0) {
        container.innerHTML = '<div class="text-center py-4 text-muted">No hay actividad reciente</div>';
        return;
    }
    
    let html = '';
    const colores = ['#7c3aed', '#10b981', '#3b82f6', '#f59e0b', '#0891b2'];
    
    actividades.forEach((act, i) => {
        const iniciales = act.usuario
            .split(' ')
            .map(n => n[0])
            .join('')
            .substring(0, 2)
            .toUpperCase();
        
        const color = colores[i % colores.length];
        
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

function actualizarProyectos(proyectos) {
    console.log('📈 Actualizando proyectos:', proyectos);
    
    // Buscar el contenedor de progreso
    const cards = document.querySelectorAll('.xnx-card');
    let progresoContainer = null;
    
    cards.forEach(card => {
        const title = card.querySelector('.xnx-card-title');
        if (title && title.textContent.includes('Progreso proyectos')) {
            progresoContainer = card.querySelector('.xnx-card-body');
        }
    });
    
    if (!progresoContainer) return;
    
    if (!proyectos || proyectos.length === 0) {
        progresoContainer.innerHTML = '<div class="text-center py-4 text-muted">No hay proyectos activos</div>';
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
                    <div class="xnx-progress-bar ${claseColor}" style="width:${proy.porcentaje}%"></div>
                </div>
            </div>
        `;
    });
    
    progresoContainer.innerHTML = html;
}

function mostrarError(mensaje) {
    // Buscar el contenido principal
    const content = document.querySelector('.xnx-content');
    if (!content) return;
    
    // Mostrar alerta de error
    const alerta = document.createElement('div');
    alerta.className = 'alert alert-danger m-3';
    alerta.innerHTML = `
        <i class="bi bi-exclamation-triangle me-2"></i>
        <strong>Error:</strong> ${mensaje}
        <br><small>Verifica la consola (F12) para más detalles.</small>
    `;
    
    content.insertBefore(alerta, content.firstChild);
}

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