/**
 * proyectos.js — Gestión de proyectos y kanban
 * Ubicación: /Assets/js/proyectos.js
 */

const PROYECTOS_ENDPOINT = '/api/proyectos';
let proyectoSeleccionado = null;
let toastInstance = null;
let proyectosCache = [];

// ═══════════════════════════════════════════
// INICIO
// ═══════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Iniciando Proyectos...');
    cargarDatosUsuario();
    cargarProyectos();
    inicializarDragDrop();
    inicializarToasts();
    inicializarEventos();
});

function inicializarToasts() {
    const toastEl = document.getElementById('liveToast');
    if (toastEl) {
        toastInstance = new bootstrap.Toast(toastEl, { delay: 4000 });
    }
}

function inicializarEventos() {
    document.querySelector('.btn[title="Recargar"]')?.addEventListener('click', () => {
        cargarProyectos();
    });
}

// ═══════════════════════════════════════════
// USUARIO
// ═══════════════════════════════════════════

function cargarDatosUsuario() {
    try {
        const data = localStorage.getItem('usuarioActual');
        if (!data) return;
        
        const usuario = JSON.parse(data);
        document.getElementById('userName').textContent = usuario.nombre || 'Usuario';
        document.getElementById('userRole').textContent = usuario.cargo || usuario.rol || '';
        
        const avatar = document.getElementById('userAvatar');
        if (avatar && usuario.nombre) {
            const iniciales = usuario.nombre
                .split(' ')
                .map(n => n.charAt(0))
                .join('')
                .substring(0, 2)
                .toUpperCase();
            avatar.textContent = iniciales || 'U';
            avatar.style.background = '#3b82f6';
        }
    } catch (e) {
        console.error('Error al leer usuario:', e);
    }
}

function cerrarSesion() {
    localStorage.removeItem('usuarioActual');
    fetch('/api/auth/logout', { method: 'POST', credentials: 'include' })
        .catch(() => {})
        .finally(() => window.location.href = '/login');
}

// ═══════════════════════════════════════════
// PROYECTOS - CRUD COMPLETO
// ═══════════════════════════════════════════

async function cargarProyectos(filtro = '') {
    try {
        let url = `${PROYECTOS_ENDPOINT}?action=listar`;
        if (filtro) url += `&estado=${encodeURIComponent(filtro)}`;
        
        console.log('📡 Cargando proyectos:', url);
        
        const response = await fetch(url);
        const data = await response.json();
        
        console.log('✅ Proyectos cargados:', data);
        
        if (data.success) {
            proyectosCache = data.data.proyectos || [];
            const total = data.data.total || 0;
            
            document.getElementById('badgeProyectos').textContent = total;
            document.getElementById('totalProyectos').textContent = total;
            
            llenarSelectorProyectos(proyectosCache);
            renderizarTablaProyectos(proyectosCache);
        } else {
            mostrarToast(data.message || 'Error al cargar proyectos', 'error');
        }
    } catch (error) {
        console.error('❌ Error al cargar proyectos:', error);
        mostrarToast('Error de conexión al cargar proyectos', 'error');
    }
}

function renderizarTablaProyectos(proyectos) {
    const tbody = document.getElementById('tablaProyectosBody');
    if (!tbody) return;
    
    if (!proyectos || proyectos.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-4 text-muted">
                    <i class="bi bi-inbox fs-4 d-block mb-2"></i>
                    No hay proyectos creados. ¡Crea tu primer proyecto!
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = proyectos.map(proy => `
        <tr>
            <td>
                <div class="d-flex align-items-center gap-2">
                    <span class="badge" style="background:${proy.color_estado || '#6b7280'}; color:white; font-size:10px;">
                        ${proy.estado || 'Activo'}
                    </span>
                    <strong>${proy.nombre}</strong>
                </div>
                <small class="text-muted">${proy.descripcion || 'Sin descripción'}</small>
            </td>
            <td>${proy.tipo || 'No especificado'}</td>
            <td>
                <div class="d-flex align-items-center gap-2">
                    <div class="progress" style="width:80px; height:6px;">
                        <div class="progress-bar" role="progressbar" 
                             style="width:${proy.porcentaje || 0}%;" 
                             aria-valuenow="${proy.porcentaje || 0}" 
                             aria-valuemin="0" aria-valuemax="100">
                        </div>
                    </div>
                    <small>${proy.porcentaje || 0}%</small>
                </div>
            </td>
            <td>${proy.total_tareas || 0}</td>
            <td>
                <span class="badge bg-light text-dark">
                    ${'⭐'.repeat(Math.min(proy.importancia || 1, 4))}
                </span>
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="editarProyecto(${proy.id})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-outline-success" onclick="cambiarEstadoProyecto(${proy.id})" title="Cambiar estado">
                        <i class="bi bi-arrow-repeat"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="eliminarProyecto(${proy.id})" title="Eliminar">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function llenarSelectorProyectos(proyectos) {
    const select = document.getElementById('selectProyecto');
    select.innerHTML = '<option value="">-- Selecciona un proyecto --</option>';
    
    if (!proyectos || proyectos.length === 0) {
        select.innerHTML += '<option value="" disabled>No hay proyectos creados</option>';
        return;
    }
    
    proyectos.forEach(proy => {
        const option = document.createElement('option');
        option.value = proy.id;
        option.textContent = `${proy.nombre} (${proy.porcentaje || 0}%)`;
        select.appendChild(option);
    });
}

async function seleccionarProyecto(idProyecto) {
    proyectoSeleccionado = idProyecto;
    
    if (!idProyecto) {
        limpiarKanban();
        return;
    }
    
    try {
        const response = await fetch(`${PROYECTOS_ENDPOINT}?action=kanban&id=${idProyecto}`);
        const data = await response.json();
        
        if (data.success) {
            renderizarKanban(data.data.columnas);
        } else {
            mostrarToast(data.message || 'Error al cargar tareas', 'error');
        }
    } catch (error) {
        console.error('Error al cargar kanban:', error);
        mostrarToast('Error de conexión', 'error');
    }
}

// ═══════════════════════════════════════════
// CRUD - CREAR PROYECTO
// ═══════════════════════════════════════════

async function crearProyecto() {
    const nombre = document.getElementById('proyectoNombre').value.trim();
    
    if (!nombre) {
        mostrarToast('El nombre del proyecto es obligatorio', 'error');
        return;
    }
    
    const estado = document.getElementById('proyectoEstado')?.value || 'Activo';
    
    const datos = {
        nombre: nombre,
        descripcion: document.getElementById('proyectoDescripcion').value.trim(),
        tipo_proyecto: document.getElementById('proyectoTipo').value,
        nivel_importancia: parseInt(document.getElementById('proyectoImportancia').value),
        fecha_inicio: new Date().toISOString().split('T')[0],
        fecha_fin: document.getElementById('proyectoFechaFin').value || null,
        estado: estado
    };
    
    try {
        const response = await fetch(`${PROYECTOS_ENDPOINT}?action=crear`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datos)
        });
        
        const data = await response.json();
        
        if (data.success) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalNuevoProyecto'));
            modal.hide();
            
            document.getElementById('proyectoNombre').value = '';
            document.getElementById('proyectoDescripcion').value = '';
            document.getElementById('proyectoFechaFin').value = '';
            
            mostrarToast('✅ Proyecto creado exitosamente', 'success');
            
            await cargarProyectos();
            
            if (data.data && data.data.id) {
                document.getElementById('selectProyecto').value = data.data.id;
                seleccionarProyecto(data.data.id);
            }
        } else {
            mostrarToast(data.message || 'Error al crear proyecto', 'error');
        }
    } catch (error) {
        console.error('Error al crear proyecto:', error);
        mostrarToast('Error de conexión', 'error');
    }
}

// ═══════════════════════════════════════════
// CRUD - EDITAR PROYECTO
// ═══════════════════════════════════════════

function editarProyecto(idProyecto) {
    const proyecto = proyectosCache.find(p => p.id === idProyecto);
    if (!proyecto) {
        mostrarToast('Proyecto no encontrado', 'error');
        return;
    }
    
    document.getElementById('editarProyectoId').value = proyecto.id;
    document.getElementById('editarProyectoNombre').value = proyecto.nombre;
    document.getElementById('editarProyectoDescripcion').value = proyecto.descripcion || '';
    document.getElementById('editarProyectoTipo').value = proyecto.tipo || '';
    document.getElementById('editarProyectoImportancia').value = proyecto.importancia || 1;
    document.getElementById('editarProyectoEstado').value = proyecto.estado || 'Activo';
    document.getElementById('editarProyectoFechaFin').value = proyecto.fecha_fin || '';
    
    const modal = new bootstrap.Modal(document.getElementById('modalEditarProyecto'));
    modal.show();
}

async function actualizarProyecto() {
    const id = parseInt(document.getElementById('editarProyectoId').value);
    const nombre = document.getElementById('editarProyectoNombre').value.trim();
    
    if (!nombre) {
        mostrarToast('El nombre es obligatorio', 'error');
        return;
    }
    
    const datos = {
        id_proyecto: id,
        nombre: nombre,
        descripcion: document.getElementById('editarProyectoDescripcion').value.trim(),
        tipo_proyecto: document.getElementById('editarProyectoTipo').value,
        nivel_importancia: parseInt(document.getElementById('editarProyectoImportancia').value),
        estado: document.getElementById('editarProyectoEstado').value,
        fecha_fin: document.getElementById('editarProyectoFechaFin').value || null
    };
    
    try {
        const response = await fetch(`${PROYECTOS_ENDPOINT}?action=actualizar`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datos)
        });
        
        const data = await response.json();
        
        if (data.success) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalEditarProyecto'));
            modal.hide();
            
            mostrarToast('✅ Proyecto actualizado', 'success');
            await cargarProyectos();
            
            if (proyectoSeleccionado == id) {
                seleccionarProyecto(id);
            }
        } else {
            mostrarToast(data.message || 'Error al actualizar', 'error');
        }
    } catch (error) {
        console.error('Error al actualizar proyecto:', error);
        mostrarToast('Error de conexión', 'error');
    }
}

// ═══════════════════════════════════════════
// CRUD - CAMBIAR ESTADO
// ═══════════════════════════════════════════

function cambiarEstadoProyecto(idProyecto) {
    const proyecto = proyectosCache.find(p => p.id === idProyecto);
    if (!proyecto) return;
    
    document.getElementById('estadoProyectoId').value = proyecto.id;
    document.getElementById('estadoProyectoNombre').textContent = proyecto.nombre;
    document.getElementById('estadoProyectoActual').textContent = proyecto.estado || 'Activo';
    document.getElementById('estadoProyectoSelect').value = proyecto.estado || 'Activo';
    
    const modal = new bootstrap.Modal(document.getElementById('modalCambiarEstado'));
    modal.show();
}

async function confirmarCambioEstado() {
    const id = parseInt(document.getElementById('estadoProyectoId').value);
    const nuevoEstado = document.getElementById('estadoProyectoSelect').value;
    
    if (!nuevoEstado) {
        mostrarToast('Selecciona un estado', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${PROYECTOS_ENDPOINT}?action=cambiar_estado`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id_proyecto: id,
                estado: nuevoEstado
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalCambiarEstado'));
            modal.hide();
            
            mostrarToast(`✅ Estado cambiado a "${nuevoEstado}"`, 'success');
            await cargarProyectos();
            
            if (proyectoSeleccionado == id) {
                seleccionarProyecto(id);
            }
        } else {
            mostrarToast(data.message || 'Error al cambiar estado', 'error');
        }
    } catch (error) {
        console.error('Error al cambiar estado:', error);
        mostrarToast('Error de conexión', 'error');
    }
}

// ═══════════════════════════════════════════
// CRUD - ELIMINAR PROYECTO
// ═══════════════════════════════════════════

function eliminarProyecto(idProyecto) {
    const proyecto = proyectosCache.find(p => p.id === idProyecto);
    if (!proyecto) return;
    
    if (!confirm(`¿Estás seguro de eliminar el proyecto "${proyecto.nombre}"?\nEsta acción eliminará todas las tareas asociadas.`)) {
        return;
    }
    
    fetch(`${PROYECTOS_ENDPOINT}?action=eliminar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_proyecto: idProyecto })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            mostrarToast('✅ Proyecto eliminado', 'success');
            
            if (proyectoSeleccionado == idProyecto) {
                proyectoSeleccionado = null;
                document.getElementById('selectProyecto').value = '';
                limpiarKanban();
            }
            
            cargarProyectos();
        } else {
            mostrarToast(data.message || 'Error al eliminar', 'error');
        }
    })
    .catch(error => {
        console.error('Error al eliminar proyecto:', error);
        mostrarToast('Error de conexión', 'error');
    });
}

// ═══════════════════════════════════════════
// KANBAN
// ═══════════════════════════════════════════

function renderizarKanban(columnas) {
    if (!columnas) return;
    
    renderizarColumna('tareasPendiente', columnas.pendiente);
    renderizarColumna('tareasProgreso', columnas.en_progreso);
    renderizarColumna('tareasRevision', columnas.en_revision);
    renderizarColumna('tareasHecho', columnas.hecho);
    
    document.getElementById('countPendiente').textContent = columnas.pendiente?.total || 0;
    document.getElementById('countProgreso').textContent = columnas.en_progreso?.total || 0;
    document.getElementById('countRevision').textContent = columnas.en_revision?.total || 0;
    document.getElementById('countHecho').textContent = columnas.hecho?.total || 0;
}

function renderizarColumna(containerId, datosColumna) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    
    if (!datosColumna || !datosColumna.tareas || datosColumna.tareas.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-inbox"></i>
                <p>Sin tareas</p>
            </div>`;
        return;
    }
    
    datosColumna.tareas.forEach(tarea => {
        const card = crearTarjetaTarea(tarea);
        container.appendChild(card);
    });
}

function crearTarjetaTarea(tarea) {
    const div = document.createElement('div');
    div.className = 'task-card';
    div.draggable = true;
    div.dataset.tareaId = tarea.id;
    div.dataset.estado = tarea.estado;
    
    const fecha = tarea.fecha_vencimiento 
        ? new Date(tarea.fecha_vencimiento + 'T12:00:00').toLocaleDateString('es-CO', { 
            day: 'numeric', month: 'short' 
          })
        : 'Sin fecha';
    
    div.innerHTML = `
        <span class="tag tag-blue mb-2">${tarea.estado || 'Pendiente'}</span>
        <div class="task-title">${tarea.titulo}</div>
        <div class="task-meta">
            <div class="task-assignees">
                <div class="xnx-avatar sm" style="background:#3b82f6;width:28px;height:28px;font-size:11px;">
                    ${tarea.asignado?.iniciales || 'SA'}
                </div>
                <small class="ms-2 text-muted">${tarea.asignado?.nombre || 'Sin asignar'}</small>
            </div>
            <span class="task-due">
                <i class="bi bi-calendar3 me-1"></i>${fecha}
            </span>
        </div>
    `;
    
    div.addEventListener('dragstart', (e) => {
        div.style.opacity = '0.5';
        e.dataTransfer.setData('text/plain', JSON.stringify({
            id: tarea.id,
            estado: tarea.estado
        }));
    });
    
    div.addEventListener('dragend', () => {
        div.style.opacity = '1';
    });
    
    return div;
}

function limpiarKanban() {
    ['tareasPendiente', 'tareasProgreso', 'tareasRevision', 'tareasHecho'].forEach(id => {
        const container = document.getElementById(id);
        if (container) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-inbox"></i>
                    <p>Selecciona un proyecto</p>
                </div>`;
        }
    });
    
    ['countPendiente', 'countProgreso', 'countRevision', 'countHecho'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = '0';
    });
}

// ═══════════════════════════════════════════
// CREAR TAREA
// ═══════════════════════════════════════════

function abrirModalTarea(estado) {
    if (!proyectoSeleccionado) {
        mostrarToast('⚠️ Selecciona un proyecto primero', 'error');
        return;
    }
    
    document.getElementById('tareaEstado').value = estado;
    document.getElementById('tareaTitulo').value = '';
    document.getElementById('tareaDescripcion').value = '';
    document.getElementById('tareaFechaVencimiento').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('modalNuevaTarea'));
    modal.show();
}

async function crearTarea() {
    const titulo = document.getElementById('tareaTitulo').value.trim();
    
    if (!titulo) {
        mostrarToast('El título es obligatorio', 'error');
        return;
    }
    
    if (!proyectoSeleccionado) {
        mostrarToast('No hay proyecto seleccionado', 'error');
        return;
    }
    
    const estado = document.getElementById('tareaEstado').value;
    const mapeoEstados = {
        'pendiente': 'Por Hacer',
        'progreso': 'En Progreso',
        'revision': 'En Revisión',
        'hecho': 'Completada'
    };
    
    const datos = {
        titulo: titulo,
        descripcion: document.getElementById('tareaDescripcion').value.trim(),
        id_proyecto: proyectoSeleccionado,
        estado: mapeoEstados[estado] || 'Por Hacer',
        fecha_vencimiento: document.getElementById('tareaFechaVencimiento').value || null
    };
    
    try {
        const response = await fetch(`${PROYECTOS_ENDPOINT}?action=crear_tarea`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datos)
        });
        
        const data = await response.json();
        
        if (data.success) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalNuevaTarea'));
            modal.hide();
            
            document.getElementById('tareaTitulo').value = '';
            document.getElementById('tareaDescripcion').value = '';
            document.getElementById('tareaFechaVencimiento').value = '';
            
            mostrarToast('✅ Tarea creada', 'success');
            seleccionarProyecto(proyectoSeleccionado);
        } else {
            mostrarToast(data.message || 'Error al crear tarea', 'error');
        }
    } catch (error) {
        console.error('Error al crear tarea:', error);
        mostrarToast('Error de conexión', 'error');
    }
}

// ═══════════════════════════════════════════
// DRAG & DROP
// ═══════════════════════════════════════════

function inicializarDragDrop() {
    document.querySelectorAll('.kanban-col').forEach(col => {
        col.addEventListener('dragover', (e) => {
            e.preventDefault();
        });
        
        col.addEventListener('drop', async (e) => {
            e.preventDefault();
            
            const rawData = e.dataTransfer.getData('text/plain');
            if (!rawData) return;
            
            let tareaData;
            try {
                tareaData = JSON.parse(rawData);
            } catch {
                return;
            }
            
            const columnaId = col.id;
            const mapaEstados = {
                'col-pendiente': 'pendiente',
                'col-progreso': 'en_progreso',
                'col-revision': 'en_revision',
                'col-hecho': 'hecho'
            };
            
            const nuevoEstado = mapaEstados[columnaId];
            if (!nuevoEstado) return;
            
            try {
                await fetch(`${PROYECTOS_ENDPOINT}?action=mover_tarea`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        id_tarea: tareaData.id, 
                        estado: nuevoEstado 
                    })
                });
                
                seleccionarProyecto(proyectoSeleccionado);
            } catch (error) {
                console.error('Error al mover tarea:', error);
                mostrarToast('Error al mover tarea', 'error');
            }
        });
    });
}

// ═══════════════════════════════════════════
// TOAST
// ═══════════════════════════════════════════

function mostrarToast(mensaje, tipo = 'info') {
    const toastEl = document.getElementById('liveToast');
    const toastMsg = document.getElementById('toastMessage');
    if (!toastEl || !toastMsg) return;
    
    const bgClass = tipo === 'error' ? 'text-bg-danger' : 
                    tipo === 'success' ? 'text-bg-success' : 
                    'text-bg-info';
    
    toastEl.className = `toast align-items-center ${bgClass} border-0`;
    toastMsg.textContent = mensaje;
    
    if (toastInstance) {
        toastInstance.show();
    } else {
        const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
        toast.show();
    }
}