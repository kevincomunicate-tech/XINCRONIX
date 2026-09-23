package com.Xincronix.controller;

import com.Xincronix.model.Proyecto;
import com.Xincronix.model.Tarea;
import com.Xincronix.model.Usuario;
import com.Xincronix.model.Equipo;
import com.Xincronix.repository.EquipoRepository;
import com.Xincronix.repository.ProyectoRepository;
import com.Xincronix.repository.TareaRepository;
import com.Xincronix.repository.UsuarioRepository;
import com.Xincronix.service.ActividadService;
import jakarta.transaction.Transactional;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/proyectos")
public class ProyectoApiController {
    private final ProyectoRepository proyectos;
    private final TareaRepository tareas;
    private final UsuarioRepository usuarios;
    private final EquipoRepository equipos;
    private final ActividadService actividadService;

    public ProyectoApiController(ProyectoRepository proyectos, TareaRepository tareas,
                                 UsuarioRepository usuarios, EquipoRepository equipos, ActividadService actividadService) {
        this.proyectos = proyectos;
        this.tareas = tareas;
        this.usuarios = usuarios;
        this.equipos = equipos;
        this.actividadService = actividadService;
    }

    @GetMapping
    public ResponseEntity<Map<String, Object>> get(@RequestParam(defaultValue = "listar") String action,
                                                    @RequestParam(required = false) String estado,
                                                    @RequestParam(required = false) Integer id,
                                                    @AuthenticationPrincipal UserDetails principal) {
        Usuario actor = actor(principal);
        if ("kanban".equals(action)) return kanban(actor, id);
        if (!"listar".equals(action)) return error(HttpStatus.BAD_REQUEST, "Accion no soportada");

        List<Map<String, Object>> data = proyectos.findByEmpresaIdEmpresa(actor.getIdEmpresa()).stream()
                .filter(proyecto -> estado == null || estado.isBlank() || estado.equalsIgnoreCase(proyecto.getEstado()))
                .map(this::projectData)
                .toList();
        return success(Map.of("proyectos", data, "total", data.size()));
    }

    @PostMapping
    @Transactional
    public ResponseEntity<Map<String, Object>> post(@RequestParam(defaultValue = "crear") String action,
                                                     @RequestBody(required = false) Map<String, Object> body,
                                                     @AuthenticationPrincipal UserDetails principal) {
        Usuario actor = actor(principal);
        if ("crear".equals(action)) {
            Proyecto proyecto = new Proyecto();
            applyProjectData(proyecto, body, actor);
            proyecto.setEmpresa(actor.getEmpresa());
            Proyecto saved = proyectos.save(proyecto);
            actividadService.registrar(actor, "Proyectos", "CREAR", saved.getNombre());
            return success(Map.of("id", saved.getIdProyecto(), "proyecto", projectData(saved)));
        }
        if ("crear_tarea".equals(action)) return createTask(actor, body);
        if ("eliminar".equals(action)) return delete(actor, body);
        return error(HttpStatus.BAD_REQUEST, "Accion no soportada");
    }

    @PutMapping
    @Transactional
    public ResponseEntity<Map<String, Object>> put(@RequestParam(defaultValue = "actualizar") String action,
                                                    @RequestBody Map<String, Object> body,
                                                    @AuthenticationPrincipal UserDetails principal) {
        Usuario actor = actor(principal);
        Integer id = integer(body, "id_proyecto");
        if ("mover_tarea".equals(action)) return moveTask(actor, body);

        Proyecto proyecto = findProject(actor, id);
        if (proyecto == null) return error(HttpStatus.NOT_FOUND, "Proyecto no encontrado");
        if ("cambiar_estado".equals(action)) {
            proyecto.setEstado(text(body, "estado", proyecto.getEstado()));
        } else if ("actualizar".equals(action)) {
            applyProjectData(proyecto, body, actor);
        } else {
            return error(HttpStatus.BAD_REQUEST, "Accion no soportada");
        }
        Proyecto saved = proyectos.save(proyecto);
        actividadService.registrar(actor, "Proyectos", "ACTUALIZAR", saved.getNombre());
        return success(Map.of("proyecto", projectData(saved)));
    }

    private ResponseEntity<Map<String, Object>> kanban(Usuario actor, Integer id) {
        Proyecto proyecto = findProject(actor, id);
        if (proyecto == null) return error(HttpStatus.NOT_FOUND, "Proyecto no encontrado");

        Map<String, List<Map<String, Object>>> grouped = new HashMap<>();
        grouped.put("pendiente", new ArrayList<>());
        grouped.put("en_progreso", new ArrayList<>());
        grouped.put("en_revision", new ArrayList<>());
        grouped.put("hecho", new ArrayList<>());
        for (Tarea tarea : tareas.findByProyectoIdProyecto(id)) {
            grouped.get(columnFor(tarea.getEstado())).add(taskData(tarea));
        }

        Map<String, Object> columns = new HashMap<>();
        grouped.forEach((key, value) -> columns.put(key, Map.of("total", value.size(), "tareas", value)));
        return success(Map.of("columnas", columns));
    }

    private ResponseEntity<Map<String, Object>> createTask(Usuario actor, Map<String, Object> body) {
        Proyecto proyecto = findProject(actor, integer(body, "id_proyecto"));
        if (proyecto == null) return error(HttpStatus.NOT_FOUND, "Proyecto no encontrado");
        String titulo = text(body, "titulo", "").trim();
        if (titulo.isBlank()) return error(HttpStatus.BAD_REQUEST, "El titulo es obligatorio");

        Tarea tarea = new Tarea();
        tarea.setTitulo(titulo);
        tarea.setDescripcion(text(body, "descripcion", ""));
        tarea.setEstado(text(body, "estado", "Por Hacer"));
        tarea.setPrioridad(text(body, "prioridad", "Media"));
        tarea.setFechaVencimiento(date(body, "fecha_vencimiento"));
        tarea.setProyecto(proyecto);
        Tarea saved = tareas.save(tarea);
        actividadService.registrar(actor, "Tareas", "CREAR", saved.getTitulo());
        return success(Map.of("id", saved.getIdTarea(), "tarea", taskData(saved)));
    }

    private ResponseEntity<Map<String, Object>> moveTask(Usuario actor, Map<String, Object> body) {
        Integer id = integer(body, "id_tarea");
        Tarea tarea = id == null ? null : tareas.findById(id).orElse(null);
        if (tarea == null || !belongsTo(tarea.getProyecto(), actor)) {
            return error(HttpStatus.NOT_FOUND, "Tarea no encontrada");
        }
        tarea.setEstado(text(body, "estado", tarea.getEstado()));
        tareas.save(tarea);
        actividadService.registrar(actor, "Tareas", "ACTUALIZAR", tarea.getTitulo());
        return success(Map.of("tarea", taskData(tarea)));
    }

    private ResponseEntity<Map<String, Object>> delete(Usuario actor, Map<String, Object> body) {
        Proyecto proyecto = findProject(actor, integer(body, "id_proyecto"));
        if (proyecto == null) return error(HttpStatus.NOT_FOUND, "Proyecto no encontrado");
        tareas.deleteAll(tareas.findByProyectoIdProyecto(proyecto.getIdProyecto()));
        proyectos.delete(proyecto);
        actividadService.registrar(actor, "Proyectos", "ELIMINAR", proyecto.getNombre());
        return success(Map.of("id", proyecto.getIdProyecto()));
    }

    private void applyProjectData(Proyecto proyecto, Map<String, Object> body, Usuario actor) {
        proyecto.setNombre(text(body, "nombre", proyecto.getNombre()));
        proyecto.setDescripcion(text(body, "descripcion", proyecto.getDescripcion()));
        proyecto.setTipoProyecto(text(body, "tipo_proyecto", proyecto.getTipoProyecto()));
        proyecto.setNivelImportancia(integer(body, "nivel_importancia", proyecto.getNivelImportancia()));
        proyecto.setEstado(text(body, "estado", proyecto.getEstado()));
        if (body.containsKey("fecha_inicio")) proyecto.setFechaInicio(date(body, "fecha_inicio"));
        if (body.containsKey("fecha_fin")) proyecto.setFechaFin(date(body, "fecha_fin"));
        if (body.containsKey("equipo_id")) {
            Integer equipoId = integer(body, "equipo_id");
            Equipo equipo = equipoId == null ? null : equipos.findById(equipoId)
                    .filter(item -> actor.getIdEmpresa().equals(item.getEmpresa().getIdEmpresa()))
                    .orElse(null);
            if (equipoId != null && equipo == null) throw new IllegalArgumentException("El equipo no pertenece a tu empresa");
            proyecto.setEquipo(equipo);
        }
    }

    private Map<String, Object> projectData(Proyecto proyecto) {
        List<Tarea> projectTasks = tareas.findByProyectoIdProyecto(proyecto.getIdProyecto());
        long completed = projectTasks.stream().filter(task -> columnFor(task.getEstado()).equals("hecho")).count();
        int percentage = projectTasks.isEmpty() ? 0 : (int) (completed * 100 / projectTasks.size());
        String status = text(proyecto.getEstado());
        Equipo equipo = proyecto.getEquipo();
        Map<String, Object> data = new HashMap<>();
        data.put("id", proyecto.getIdProyecto());
        data.put("nombre", text(proyecto.getNombre()));
        data.put("descripcion", text(proyecto.getDescripcion()));
        data.put("tipo", text(proyecto.getTipoProyecto()));
        data.put("porcentaje", percentage);
        data.put("total_tareas", projectTasks.size());
        data.put("importancia", proyecto.getNivelImportancia() == null ? 1 : proyecto.getNivelImportancia());
        data.put("estado", status);
        data.put("equipo_id", equipo == null ? 0 : equipo.getIdEquipo());
        data.put("equipo_nombre", equipo == null ? "" : text(equipo.getNombre()));
        data.put("color_estado", colorFor(status));
        data.put("fecha_fin", proyecto.getFechaFin() == null ? "" : proyecto.getFechaFin().toString());
        return data;
    }

    private Map<String, Object> taskData(Tarea tarea) {
        String name = tarea.getUsuario() == null ? "Sin asignar" : text(tarea.getUsuario().getNombres()) + " " + text(tarea.getUsuario().getApellidos());
        String initials = name.trim().isBlank() ? "SA" : name.trim().substring(0, 1).toUpperCase();
        Map<String, Object> data = new HashMap<>();
        data.put("id", tarea.getIdTarea());
        data.put("titulo", text(tarea.getTitulo()));
        data.put("descripcion", text(tarea.getDescripcion()));
        data.put("estado", text(tarea.getEstado()));
        data.put("prioridad", text(tarea.getPrioridad()));
        data.put("fecha_vencimiento", tarea.getFechaVencimiento() == null ? "" : tarea.getFechaVencimiento().toString());
        data.put("asignado", Map.of("nombre", name.trim(), "iniciales", initials));
        return data;
    }

    private String columnFor(String value) {
        String status = text(value).toLowerCase();
        if (status.contains("complet") || status.contains("hecho")) return "hecho";
        if (status.contains("revisi")) return "en_revision";
        if (status.contains("progres")) return "en_progreso";
        return "pendiente";
    }

    private String colorFor(String status) {
        return switch (status.toLowerCase()) {
            case "activo" -> "#10b981";
            case "pendiente" -> "#f59e0b";
            case "en progreso" -> "#3b82f6";
            case "en espera" -> "#6b7280";
            default -> "#6b7280";
        };
    }

    private Usuario actor(UserDetails principal) {
        return usuarios.findByEmail(principal.getUsername()).orElseThrow();
    }

    private Proyecto findProject(Usuario actor, Integer id) {
        if (id == null || actor.getIdEmpresa() == null) return null;
        return proyectos.findById(id)
                .filter(project -> actor.getIdEmpresa().equals(project.getEmpresa().getIdEmpresa()))
                .orElse(null);
    }

    private boolean belongsTo(Proyecto proyecto, Usuario actor) {
        return proyecto != null && proyecto.getEmpresa() != null
                && actor.getIdEmpresa().equals(proyecto.getEmpresa().getIdEmpresa());
    }

    private ResponseEntity<Map<String, Object>> success(Map<String, Object> data) {
        return ResponseEntity.ok(Map.of("success", true, "data", data));
    }

    private ResponseEntity<Map<String, Object>> error(HttpStatus status, String message) {
        return ResponseEntity.status(status).body(Map.of("success", false, "message", message));
    }

    private String text(Map<String, Object> body, String key, String fallback) {
        Object value = body == null ? null : body.get(key);
        return value == null ? fallback : String.valueOf(value);
    }

    private String text(String value) { return value == null ? "" : value; }

    private Integer integer(Map<String, Object> body, String key) { return integer(body, key, null); }

    private Integer integer(Map<String, Object> body, String key, Integer fallback) {
        Object value = body == null ? null : body.get(key);
        if (value == null) return fallback;
        try { return value instanceof Number number ? number.intValue() : Integer.valueOf(value.toString()); }
        catch (NumberFormatException ignored) { return fallback; }
    }

    private LocalDate date(Map<String, Object> body, String key) {
        String value = text(body, key, "");
        return value.isBlank() || "null".equals(value) ? null : LocalDate.parse(value);
    }
}
