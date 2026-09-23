<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Xincronix — Proyectos</title>

    <!-- Bootstrap -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" />
    
    <!-- Estilos -->
    <link rel="stylesheet" href="/css/Index.css" />
    <link rel="stylesheet" href="/css/Proyecto.css" />
    <link rel="icon" href="/img/logo xincronix.png" />
    
    <style>
        /* Estilos generales */
        .modal-content {
            background: #fff;
            border: none;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .modal-header {
            border-bottom: 1px solid rgba(0,0,0,0.08);
            padding: 20px 24px;
        }
        .modal-title {
            font-weight: 700;
            font-size: 20px;
            color: #0d1f3c;
        }
        .modal-body { padding: 24px; }
        .modal-footer {
            border-top: 1px solid rgba(0,0,0,0.08);
            padding: 16px 24px;
        }
        .form-label {
            font-weight: 600;
            font-size: 12px;
            color: rgba(0,0,0,0.55);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }
        .form-control, .form-select {
            border: 1.5px solid rgba(0,0,0,0.15);
            border-radius: 10px;
            padding: 10px 14px;
            font-size: 14px;
        }
        .form-control:focus, .form-select:focus {
            border-color: #2a5bff;
            box-shadow: 0 0 0 3px rgba(42,91,255,0.1);
        }
        .empty-state {
            text-align: center;
            padding: 30px 15px;
            color: #9ca3af;
        }
        .empty-state i {
            font-size: 36px;
            margin-bottom: 10px;
            opacity: 0.4;
        }
        .empty-state p {
            font-size: 13px;
            margin: 0;
        }
        .task-card {
            cursor: grab;
        }
        .task-card:active {
            cursor: grabbing;
        }
        
        /* Tabla de proyectos */
        .table-proyectos th {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #6b7280;
            border-bottom: 2px solid #e5e7eb;
        }
        .table-proyectos td {
            vertical-align: middle;
            font-size: 13px;
        }
        .table-proyectos tr:hover {
            background: #f8fafc;
        }
        .badge-estado {
            font-size: 10px;
            padding: 4px 10px;
            border-radius: 20px;
        }
        
        /* Progress bar */
        .progress {
            background: #e5e7eb;
            border-radius: 10px;
        }
        .progress-bar {
            border-radius: 10px;
            background: linear-gradient(90deg, #3b82f6, #6366f1);
        }
    </style>
</head>
<body>
    <div class="app-shell">

        <!-- ══════════════ SIDEBAR ══════════════ -->
        <aside class="xnx-sidebar">
            <div class="xnx-sidebar-logo">
                <div class="xnx-logo">
                    <img src="/img/logo xincronix.png"
                        onerror="this.outerHTML='<svg width=\'28\' height=\'28\' viewBox=\'0 0 36 36\' fill=\'none\'><rect width=\'36\' height=\'36\' rx=\'8\' fill=\'rgba(37,99,235,0.2)\'/><line x1=\'5\' y1=\'10\' x2=\'15\' y2=\'26\' stroke=\'#3b82f6\' stroke-width=\'2.5\' stroke-linecap=\'round\'/><line x1=\'15\' y1=\'10\' x2=\'5\' y2=\'26\' stroke=\'#3b82f6\' stroke-width=\'2.5\' stroke-linecap=\'round\'/><line x1=\'15\' y1=\'18\' x2=\'21\' y2=\'18\' stroke=\'rgba(59,130,246,0.4)\' stroke-width=\'1.5\' stroke-dasharray=\'2 2\' stroke-linecap=\'round\'/><line x1=\'21\' y1=\'10\' x2=\'31\' y2=\'26\' stroke=\'#93c5fd\' stroke-width=\'2.5\' stroke-linecap=\'round\'/><line x1=\'31\' y1=\'10\' x2=\'21\' y2=\'26\' stroke=\'#93c5fd\' stroke-width=\'2.5\' stroke-linecap=\'round\'/></svg>'"
                        alt="" />
                    <div class="xnx-logo-text">Xin<span>cronix</span></div>
                </div>
            </div>

            <div class="xnx-sidebar-section">
                <div class="xnx-sidebar-section-label">General</div>
                <a href="Panel" class="xnx-sidebar-item">
                    <i class="bi bi-grid"></i> Dashboard
                </a>
                <a href="Proyecto" class="xnx-sidebar-item active">
                    <i class="bi bi-kanban"></i> Proyectos 
                    <span class="xnx-sidebar-badge" id="badgeProyectos">0</span>
                </a>
                <a href="Tareas" class="xnx-sidebar-item">
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

            <div class="xnx-sidebar-bottom">
                <div class="xnx-sidebar-user">
                    <div class="xnx-avatar" id="userAvatar">--</div>
                    <div>
                        <div class="user-name" id="userName">Cargando...</div>
                        <div class="user-role" id="userRole">--</div>
                    </div>
                    <button class="btn btn-sm ms-auto p-0 text-white-50 border-0 bg-transparent" 
                            title="Cerrar sesión" onclick="window.location.href='Login'">
                        <i class="bi bi-box-arrow-right"></i>
                    </button>
                </div>
            </div>
        </aside>

        <!-- ══════════════ MAIN ══════════════ -->
        <main class="xnx-main">
            <div class="xnx-topbar">
                <div>
                    <span class="xnx-topbar-title">Proyectos</span>
                    <span class="xnx-topbar-sub">
                        <span id="totalProyectos">0</span> proyectos
                    </span>
                </div>
                <div class="xnx-topbar-right">
                    <button class="btn btn-outline-secondary btn-sm px-3" onclick="cargarProyectos('')">
                        <i class="bi bi-grid me-1"></i>Todos
                    </button>
                    <button class="btn btn-outline-secondary btn-sm px-3" onclick="cargarProyectos('Activo')">
                        <i class="bi bi-play-circle me-1"></i>Activos
                    </button>
                    <button class="btn btn-outline-secondary btn-sm px-3" onclick="cargarProyectos('Pendiente')">
                        <i class="bi bi-clock me-1"></i>Pendientes
                    </button>
                    <button class="btn btn-primary btn-sm px-3" data-bs-toggle="modal" data-bs-target="#modalNuevoProyecto">
                        <i class="bi bi-plus-lg me-1"></i>Nuevo proyecto
                    </button>
                </div>
            </div>

            <div class="xnx-content">

                <!-- ═══════ TABLA DE PROYECTOS ═══════ -->
                <div class="card border-0 shadow-sm mb-4">
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-proyectos mb-0">
                                <thead>
                                    <tr>
                                        <th style="min-width:200px;">Proyecto</th>
                                        <th>Tipo</th>
                                        <th>Progreso</th>
                                        <th>Tareas</th>
                                        <th>Importancia</th>
                                        <th style="width:120px;">Acciones</th>
                                    </tr>
                                </thead>
                                <tbody id="tablaProyectosBody">
                                    <tr>
                                        <td colspan="6" class="text-center py-4 text-muted">
                                            <i class="bi bi-inbox fs-4 d-block mb-2"></i>
                                            Cargando proyectos...
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- ═══════ KANBAN ═══════ -->
                <div class="mt-4">
                    <h6 class="fw-bold mb-3">
                        <i class="bi bi-kanban me-2"></i>Tablero
                    </h6>
                    
                    <!-- Selector de proyecto para kanban -->
                    <div class="mb-3 d-flex align-items-center gap-2">
                        <select class="form-select form-select-sm d-inline-block" 
                                style="width: auto; min-width: 300px;"
                                id="selectProyecto" onchange="seleccionarProyecto(this.value)">
                            <option value="">-- Selecciona un proyecto --</option>
                        </select>
                        <button class="btn btn-outline-secondary btn-sm" onclick="location.reload()" title="Recargar">
                            <i class="bi bi-arrow-clockwise"></i>
                        </button>
                    </div>

                    <!-- Kanban Board -->
                    <div class="kanban-board" id="kanbanBoard">
                        
                        <!-- Pendiente -->
                        <div class="kanban-col" id="col-pendiente">
                            <div class="kanban-col-header">
                                <span class="kanban-col-title">📋 Pendiente</span>
                                <span class="kanban-count" id="countPendiente">0</span>
                            </div>
                            <div id="tareasPendiente" class="kanban-tasks">
                                <div class="empty-state">
                                    <i class="bi bi-inbox"></i>
                                    <p>Sin tareas</p>
                                </div>
                            </div>
                            <button class="kanban-add-btn mt-2" onclick="abrirModalTarea('pendiente')">
                                <i class="bi bi-plus me-1"></i>Agregar tarea
                            </button>
                        </div>

                        <!-- En progreso -->
                        <div class="kanban-col" id="col-progreso">
                            <div class="kanban-col-header">
                                <span class="kanban-col-title">🔄 En progreso</span>
                                <span class="kanban-count" id="countProgreso">0</span>
                            </div>
                            <div id="tareasProgreso" class="kanban-tasks">
                                <div class="empty-state">
                                    <i class="bi bi-inbox"></i>
                                    <p>Sin tareas</p>
                                </div>
                            </div>
                            <button class="kanban-add-btn mt-2" onclick="abrirModalTarea('progreso')">
                                <i class="bi bi-plus me-1"></i>Agregar tarea
                            </button>
                        </div>

                        <!-- En revisión -->
                        <div class="kanban-col" id="col-revision">
                            <div class="kanban-col-header">
                                <span class="kanban-col-title">🔍 En revisión</span>
                                <span class="kanban-count" id="countRevision">0</span>
                            </div>
                            <div id="tareasRevision" class="kanban-tasks">
                                <div class="empty-state">
                                    <i class="bi bi-inbox"></i>
                                    <p>Sin tareas</p>
                                </div>
                            </div>
                            <button class="kanban-add-btn mt-2" onclick="abrirModalTarea('revision')">
                                <i class="bi bi-plus me-1"></i>Agregar tarea
                            </button>
                        </div>

                        <!-- Hecho -->
                        <div class="kanban-col" id="col-hecho">
                            <div class="kanban-col-header">
                                <span class="kanban-col-title">✅ Hecho</span>
                                <span class="kanban-count" id="countHecho">0</span>
                            </div>
                            <div id="tareasHecho" class="kanban-tasks">
                                <div class="empty-state">
                                    <i class="bi bi-inbox"></i>
                                    <p>Sin tareas</p>
                                </div>
                            </div>
                            <button class="kanban-add-btn mt-2" onclick="abrirModalTarea('hecho')">
                                <i class="bi bi-plus me-1"></i>Agregar tarea
                            </button>
                        </div>

                    </div>
                </div>
            </div>
        </main>
    </div>

    <!-- ══════════════ MODAL: NUEVO PROYECTO ══════════════ -->
    <div class="modal fade" id="modalNuevoProyecto" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">🚀 Nuevo Proyecto</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row g-3">
                        <div class="col-md-8">
                            <label class="form-label">Nombre del proyecto *</label>
                            <input type="text" class="form-control" id="proyectoNombre" 
                                   placeholder="Ej: Dashboard v2" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Estado</label>
                            <select class="form-select" id="proyectoEstado">
                                <option value="Activo">Activo</option>
                                <option value="Pendiente">Pendiente</option>
                                <option value="En Progreso">En Progreso</option>
                                <option value="En Espera">En Espera</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Tipo</label>
                            <select class="form-select" id="proyectoTipo">
                                <option value="">Seleccionar...</option>
                                <option>Frontend</option>
                                <option>Backend</option>
                                <option>Full Stack</option>
                                <option>IA / ML</option>
                                <option>QA / Testing</option>
                                <option>Otro</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Nivel de importancia</label>
                            <select class="form-select" id="proyectoImportancia">
                                <option value="1">⭐ Baja</option>
                                <option value="2" selected>⭐⭐ Media</option>
                                <option value="3">⭐⭐⭐ Alta</option>
                                <option value="4">⭐⭐⭐⭐ Crítica</option>
                            </select>
                        </div>
                        <div class="col-12">
                            <label class="form-label">Descripción</label>
                            <textarea class="form-control" id="proyectoDescripcion" rows="2" 
                                      placeholder="Describe el objetivo..."></textarea>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Equipo responsable</label>
                            <select class="form-select" id="proyectoEquipo">
                                <option value="">Sin equipo asignado</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Fecha de inicio</label>
                            <input type="date" class="form-control" id="proyectoFechaInicio"
                                   value="">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Fecha de fin (opcional)</label>
                            <input type="date" class="form-control" id="proyectoFechaFin">
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary px-4" onclick="crearProyecto()">
                        <i class="bi bi-check-lg me-1"></i>Crear proyecto
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- ══════════════ MODAL: EDITAR PROYECTO ══════════════ -->
    <div class="modal fade" id="modalEditarProyecto" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">✏️ Editar Proyecto</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <input type="hidden" id="editarProyectoId">
                    <div class="row g-3">
                        <div class="col-md-8">
                            <label class="form-label">Nombre del proyecto *</label>
                            <input type="text" class="form-control" id="editarProyectoNombre" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Estado</label>
                            <select class="form-select" id="editarProyectoEstado">
                                <option value="Activo">Activo</option>
                                <option value="Pendiente">Pendiente</option>
                                <option value="En Progreso">En Progreso</option>
                                <option value="Completado">Completado</option>
                                <option value="Cancelado">Cancelado</option>
                                <option value="En Espera">En Espera</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Tipo</label>
                            <select class="form-select" id="editarProyectoTipo">
                                <option value="">Seleccionar...</option>
                                <option>Frontend</option>
                                <option>Backend</option>
                                <option>Full Stack</option>
                                <option>IA / ML</option>
                                <option>QA / Testing</option>
                                <option>Otro</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Nivel de importancia</label>
                            <select class="form-select" id="editarProyectoImportancia">
                                <option value="1">⭐ Baja</option>
                                <option value="2">⭐⭐ Media</option>
                                <option value="3">⭐⭐⭐ Alta</option>
                                <option value="4">⭐⭐⭐⭐ Crítica</option>
                            </select>
                        </div>
                        <div class="col-12">
                            <label class="form-label">Descripción</label>
                            <textarea class="form-control" id="editarProyectoDescripcion" rows="2"></textarea>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Equipo responsable</label>
                            <select class="form-select" id="editarProyectoEquipo">
                                <option value="">Sin equipo asignado</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Fecha de fin (opcional)</label>
                            <input type="date" class="form-control" id="editarProyectoFechaFin">
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary px-4" onclick="actualizarProyecto()">
                        <i class="bi bi-check-lg me-1"></i>Actualizar proyecto
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- ══════════════ MODAL: CAMBIAR ESTADO ══════════════ -->
    <div class="modal fade" id="modalCambiarEstado" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">🔄 Cambiar Estado</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <input type="hidden" id="estadoProyectoId">
                    <p class="mb-2">
                        <strong>Proyecto:</strong> <span id="estadoProyectoNombre"></span>
                    </p>
                    <p class="mb-3">
                        <strong>Estado actual:</strong> 
                        <span class="badge bg-secondary" id="estadoProyectoActual"></span>
                    </p>
                    <div class="mb-3">
                        <label class="form-label">Nuevo estado</label>
                        <select class="form-select" id="estadoProyectoSelect">
                            <option value="Activo">Activo</option>
                            <option value="Pendiente">Pendiente</option>
                            <option value="En Progreso">En Progreso</option>
                            <option value="Completado">Completado</option>
                            <option value="Cancelado">Cancelado</option>
                            <option value="En Espera">En Espera</option>
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary px-4" onclick="confirmarCambioEstado()">
                        <i class="bi bi-check-lg me-1"></i>Cambiar estado
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- ══════════════ MODAL: NUEVA TAREA ══════════════ -->
    <div class="modal fade" id="modalNuevaTarea" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">📝 Nueva Tarea</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <input type="hidden" id="tareaEstado">
                    <div class="mb-3">
                        <label class="form-label">Título *</label>
                        <input type="text" class="form-control" id="tareaTitulo" 
                               placeholder="Nombre de la tarea" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Descripción</label>
                        <textarea class="form-control" id="tareaDescripcion" rows="2" 
                                  placeholder="Detalles..."></textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Fecha de vencimiento</label>
                        <input type="date" class="form-control" id="tareaFechaVencimiento">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary px-4" onclick="crearTarea()">
                        <i class="bi bi-plus-lg me-1"></i>Crear tarea
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast -->
    <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 9999">
        <div id="liveToast" class="toast align-items-center border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body" id="toastMessage"></div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/js/proyectos.js"></script>
    <script src="/js/session-user.js"></script>
</body>
</html>
