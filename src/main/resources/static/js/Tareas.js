/**
 * Tareas.js - CRUD completo de Tareas
 * Gestiona creación, lectura, actualización y eliminación de tareas
 */

let tareas = [];
let editingId = null;
let filtroProyecto = null;
let filtroEstado = null;

document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadTareas();
});

/**
 * Configurar event listeners
 */
function setupEventListeners() {
    // Botón Nueva Tarea
    const btnNueva = document.querySelector('[data-action="nueva-tarea"]');
    if (btnNueva) {
        btnNueva.addEventListener('click', () => openCreateModal());
    }
    
    // Botones Filtro y Ordenar
    const btnFiltro = document.querySelector('[data-action="filtrar"]');
    if (btnFiltro) {
        btnFiltro.addEventListener('click', () => toggleFilterPanel());
    }
    
    // Botón Guardar en Modal
    const btnGuardar = document.querySelector('[data-action="guardar"]');
    if (btnGuardar) {
        btnGuardar.addEventListener('click', () => saveTarea());
    }
    
    // Botón Cancelar en Modal
    const btnCancelar = document.querySelector('[data-action="cancelar"]');
    if (btnCancelar) {
        btnCancelar.addEventListener('click', () => closeModal());
    }
    
    // Filtros
    const selectEstado = document.querySelector('[name="filtro-estado"]');
    if (selectEstado) {
        selectEstado.addEventListener('change', (e) => {
            filtroEstado = e.target.value || null;
            renderTareas();
        });
    }
    
    // Enter en búsqueda
    const inputBuscar = document.querySelector('[data-action="buscar"]');
    if (inputBuscar) {
        inputBuscar.addEventListener('keyup', debounce(() => renderTareas(), 300));
    }
}

/**
 * Cargar tareas desde API
 */
async function loadTareas() {
    UI.showLoading?.();
    
    try {
        // Aquí iría: const data = await API.get('/api/tareas.php?action=listar');
        // Por ahora, simulamos con datos de ejemplo
        
        tareas = [
            {
                id_tarea: 1,
                titulo: 'Diseño de sistema v1',
                descripcion: 'Crear wireframes y mockups',
                estado: 'Completada',
                fecha_vencimiento: '2026-06-15',
                id_proyecto: 1
            },
            {
                id_tarea: 2,
                titulo: 'Implementar autenticación',
                descripcion: 'JWT y session management',
                estado: 'En Progreso',
                fecha_vencimiento: '2026-06-20',
                id_proyecto: 1
            },
            {
                id_tarea: 3,
                titulo: 'API de tareas',
                descripcion: 'CRUD completo',
                estado: 'Por Hacer',
                fecha_vencimiento: '2026-06-25',
                id_proyecto: 1
            },
            {
                id_tarea: 4,
                titulo: 'Dashboard analytics',
                descripcion: 'Gráficos Chart.js',
                estado: 'En Progreso',
                fecha_vencimiento: '2026-06-30',
                id_proyecto: 2
            },
            {
                id_tarea: 5,
                titulo: 'Testing unitario',
                descripcion: 'PHPUnit + Jest',
                estado: 'Por Hacer',
                fecha_vencimiento: '2026-07-05',
                id_proyecto: 2
            }
        ];
        
        UI.hideLoading?.();
        renderTareas();
        updateStats();
        Logger?.info?.('Tareas cargadas', { cantidad: tareas.length });
    } catch (error) {
        UI.hideLoading?.();
        UI.showError?.('Error al cargar tareas');
        console.error('Error:', error);
    }
}

/**
 * Renderizar tareas en tabla
 */
function renderTareas() {
    let filtradas = tareas;
    
    // Aplicar filtro de estado
    if (filtroEstado) {
        filtradas = filtradas.filter(t => t.estado === filtroEstado);
    }
    
    // Aplicar búsqueda
    const inputBuscar = document.querySelector('[data-action="buscar"]');
    if (inputBuscar && inputBuscar.value) {
        const termino = inputBuscar.value.toLowerCase();
        filtradas = filtradas.filter(t => 
            t.titulo.toLowerCase().includes(termino) ||
            t.descripcion?.toLowerCase().includes(termino)
        );
    }
    
    const tbody = document.querySelector('[data-tareas-list]');
    if (!tbody) return;
    
    if (filtradas.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted py-4">
                    <i class="bi bi-inbox" style="font-size: 2rem;"></i>
                    <div>No hay tareas</div>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = filtradas.map(tarea => `
        <tr>
            <td>
                <input type="checkbox" class="form-check-input" value="${tarea.id_tarea}" 
                    onchange="toggleTarea(${tarea.id_tarea}, this.checked)">
            </td>
            <td>
                <strong>${tarea.titulo}</strong>
                <div class="text-muted small">${tarea.descripcion || ''}</div>
            </td>
            <td>
                <span class="badge ${getEstadoBadge(tarea.estado)}">
                    ${tarea.estado}
                </span>
            </td>
            <td class="small text-muted">
                ${tarea.fecha_vencimiento ? new Date(tarea.fecha_vencimiento).toLocaleDateString('es-ES') : '-'}
            </td>
            <td class="text-end">
                <button class="btn btn-sm btn-outline-secondary me-1" 
                    onclick="editTarea(${tarea.id_tarea})" title="Editar">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" 
                    onclick="deleteTarea(${tarea.id_tarea})" title="Eliminar">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

/**
 * Actualizar estadísticas
 */
function updateStats() {
    const total = tareas.length;
    const completadas = tareas.filter(t => t.estado === 'Completada').length;
    const enProgreso = tareas.filter(t => t.estado === 'En Progreso').length;
    const porHacer = tareas.filter(t => t.estado === 'Por Hacer').length;
    
    const stats = {
        total,
        completadas,
        enProgreso,
        porHacer
    };
    
    // Actualizar tarjetas de estadísticas
    if (document.querySelector('[data-stat="total"]')) {
        document.querySelector('[data-stat="total"]').textContent = stats.total;
    }
    if (document.querySelector('[data-stat="completadas"]')) {
        document.querySelector('[data-stat="completadas"]').textContent = stats.completadas;
    }
    if (document.querySelector('[data-stat="enProgreso"]')) {
        document.querySelector('[data-stat="enProgreso"]').textContent = stats.enProgreso;
    }
    if (document.querySelector('[data-stat="porHacer"]')) {
        document.querySelector('[data-stat="porHacer"]').textContent = stats.porHacer;
    }
}

/**
 * Abrir modal para crear tarea
 */
function openCreateModal() {
    editingId = null;
    const modal = document.querySelector('[data-modal="tarea"]');
    const form = document.querySelector('[data-form="tarea"]');
    
    document.querySelector('[data-modal-title]').textContent = 'Nueva Tarea';
    form.reset();
    form.querySelector('[name="id"]').value = '0';
    
    if (modal) modal.style.display = 'block';
}

/**
 * Editar tarea existente
 */
function editTarea(id) {
    const tarea = tareas.find(t => t.id_tarea === id);
    if (!tarea) return;
    
    editingId = id;
    const modal = document.querySelector('[data-modal="tarea"]');
    const form = document.querySelector('[data-form="tarea"]');
    
    document.querySelector('[data-modal-title]').textContent = 'Editar Tarea';
    
    form.querySelector('[name="id"]').value = tarea.id_tarea;
    form.querySelector('[name="titulo"]').value = tarea.titulo;
    form.querySelector('[name="descripcion"]').value = tarea.descripcion || '';
    form.querySelector('[name="estado"]').value = tarea.estado;
    if (form.querySelector('[name="fecha_vencimiento"]')) {
        form.querySelector('[name="fecha_vencimiento"]').value = tarea.fecha_vencimiento || '';
    }
    
    if (modal) modal.style.display = 'block';
}

/**
 * Guardar tarea (crear o actualizar)
 */
async function saveTarea() {
    const form = document.querySelector('[data-form="tarea"]');
    const id = parseInt(form.querySelector('[name="id"]').value);
    const titulo = form.querySelector('[name="titulo"]').value.trim();
    const descripcion = form.querySelector('[name="descripcion"]').value.trim();
    const estado = form.querySelector('[name="estado"]').value;
    const fecha_vencimiento = form.querySelector('[name="fecha_vencimiento"]')?.value || null;
    
    // Validar
    if (!titulo || titulo.length < 5) {
        UI.showError?.('El título debe tener al menos 5 caracteres');
        return;
    }
    
    UI.showLoading?.();
    
    try {
        if (id === 0 || editingId === null) {
            // Crear nueva
            // const data = await API.post('/api/tareas.php?action=crear', {
            //     titulo, descripcion, estado, fecha_vencimiento, proyecto_id: 1
            // });
            
            // Simulación
            const newId = Math.max(...tareas.map(t => t.id_tarea), 0) + 1;
            tareas.push({
                id_tarea: newId,
                titulo,
                descripcion,
                estado,
                fecha_vencimiento,
                id_proyecto: 1
            });
            
            UI.showSuccess?.('Tarea creada');
            Logger?.success?.('Tarea creada', { titulo });
        } else {
            // Actualizar existente
            // const data = await API.post('/api/tareas.php?action=actualizar', {
            //     id, titulo, descripcion, estado, fecha_vencimiento
            // });
            
            // Simulación
            const idx = tareas.findIndex(t => t.id_tarea === id);
            if (idx >= 0) {
                tareas[idx] = { ...tareas[idx], titulo, descripcion, estado, fecha_vencimiento };
            }
            
            UI.showSuccess?.('Tarea actualizada');
            Logger?.success?.('Tarea actualizada', { id });
        }
        
        UI.hideLoading?.();
        closeModal();
        renderTareas();
        updateStats();
    } catch (error) {
        UI.hideLoading?.();
        UI.showError?.('Error al guardar tarea');
        console.error('Error:', error);
    }
}

/**
 * Eliminar tarea
 */
async function deleteTarea(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar esta tarea?')) return;
    
    UI.showLoading?.();
    
    try {
        // const data = await API.get(`/api/tareas.php?action=eliminar&id=${id}`);
        
        // Simulación
        tareas = tareas.filter(t => t.id_tarea !== id);
        
        UI.showSuccess?.('Tarea eliminada');
        Logger?.success?.('Tarea eliminada', { id });
        
        UI.hideLoading?.();
        renderTareas();
        updateStats();
    } catch (error) {
        UI.hideLoading?.();
        UI.showError?.('Error al eliminar tarea');
        console.error('Error:', error);
    }
}

/**
 * Marcar tarea como completada/pendiente
 */
function toggleTarea(id, checked) {
    const tarea = tareas.find(t => t.id_tarea === id);
    if (tarea) {
        tarea.estado = checked ? 'Completada' : 'Por Hacer';
        renderTareas();
        updateStats();
    }
}

/**
 * Cerrar modal
 */
function closeModal() {
    const modal = document.querySelector('[data-modal="tarea"]');
    if (modal) modal.style.display = 'none';
}

/**
 * Toggle panel de filtros
 */
function toggleFilterPanel() {
    const panel = document.querySelector('[data-filter-panel]');
    if (panel) {
        panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    }
}

/**
 * Obtener clase badge según estado
 */
function getEstadoBadge(estado) {
    const badges = {
        'Completada': 'bg-success',
        'En Progreso': 'bg-info',
        'Por Hacer': 'bg-secondary'
    };
    return badges[estado] || 'bg-secondary';
}

/**
 * Debounce para búsqueda
 */
function debounce(callback, delay) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => callback(...args), delay);
    };
}

// Cerrar modal al clickear fuera
window.addEventListener('click', (event) => {
    const modal = document.querySelector('[data-modal="tarea"]');
    if (event.target === modal) {
        closeModal();
    }
});
