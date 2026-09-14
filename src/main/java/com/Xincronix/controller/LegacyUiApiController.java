package com.Xincronix.controller;

import java.util.List;
import java.util.Map;
import java.time.LocalDate;

import jakarta.transaction.Transactional;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.Xincronix.model.Usuario;
import com.Xincronix.model.Proyecto;
import com.Xincronix.model.Tarea;
import com.Xincronix.repository.ProyectoRepository;
import com.Xincronix.repository.TareaRepository;
import com.Xincronix.repository.UsuarioRepository;

/**
 * Transitional JSON endpoints used by the migrated screens.
 *
 * <p>They replace the former {@code controller/*.php} URLs.  Feature-specific
 * services can replace these empty initial payloads without changing the UI
 * route or JavaScript contract.</p>
 */
@RestController
@RequestMapping("/api")
public class LegacyUiApiController {

    private static final Map<String, Object> USER = Map.of(
            "iniciales", "XN", "nombres", "Usuario", "apellidos", "Xincronix",
            "nombre_rol", "Usuario", "cargo", "Usuario");

            private final ProyectoRepository proyectos;
            private final TareaRepository tareasRepository;
            private final UsuarioRepository usuarios;

            public LegacyUiApiController(ProyectoRepository proyectos, TareaRepository tareasRepository,
                         UsuarioRepository usuarios) {
            this.proyectos = proyectos;
            this.tareasRepository = tareasRepository;
            this.usuarios = usuarios;
            }

    @GetMapping("/dashboard")
            public ResponseEntity<Map<String, Object>> dashboard(@org.springframework.security.core.annotation.AuthenticationPrincipal
                             org.springframework.security.core.userdetails.UserDetails principal) {
            if (principal == null) {
            return ResponseEntity.status(401).body(Map.of(
                "status", "error", "message", "No autenticado"));
            }

            Usuario usuario = usuarios.findByEmail(principal.getUsername()).orElse(null);
            if (usuario == null) {
            return ResponseEntity.status(401).body(Map.of(
                "status", "error", "message", "Usuario no encontrado"));
            }
            Integer empresaId = usuario.getIdEmpresa();
            var proyectosEmpresa = empresaId == null ? List.<com.Xincronix.model.Proyecto>of()
                : proyectos.findByEmpresaIdEmpresa(empresaId);
            var tareasEmpresa = proyectosEmpresa.stream()
                .flatMap(proyecto -> tareasRepository.findByProyectoIdProyecto(proyecto.getIdProyecto()).stream())
                .toList();
            long tareasCompletadas = tareasEmpresa.stream()
                .filter(tarea -> tarea.getEstado() != null
                    && tarea.getEstado().toLowerCase().contains("complet"))
                .count();
            Map<String, Object> usuarioData = Map.of(
                "nombre", (usuario.getNombres() + " " + usuario.getApellidos()).trim(),
                "rol", usuario.getRol() != null ? usuario.getRol().getNombre() : "Usuario",
                "cargo", usuario.getCargo() == null ? "Usuario" : usuario.getCargo());
        return ResponseEntity.ok(Map.of("status", "success", "data", Map.of(
                "usuario", usuarioData,
                "estadisticas", Map.of(
                    "proyectos_activos", proyectosEmpresa.size(),
                    "proyectos_este_mes", proyectosEmpresa.size(),
                    "tareas_completadas", tareasCompletadas,
                    "tareas_esta_semana", tareasEmpresa.size(),
                    "agentes_activos", 0,
                    "agentes_en_espera", 0,
                    "issues_abiertos", 0),
                "actividades", List.of(), "proyectos", proyectosEmpresa.stream()
                    .map(proyecto -> {
                        var tareas = tareasRepository.findByProyectoIdProyecto(proyecto.getIdProyecto());
                        long completadas = tareas.stream()
                                .filter(tarea -> tarea.getEstado() != null
                                        && tarea.getEstado().toLowerCase().contains("complet"))
                                .count();
                        int porcentaje = tareas.isEmpty() ? 0 : (int) (completadas * 100 / tareas.size());
                        return Map.of("nombre", proyecto.getNombre(), "porcentaje", porcentaje);
                    })
                    .toList())));
    }

    @GetMapping("/tareas")
    @Transactional
    public ResponseEntity<Map<String, Object>> tareas(
            @RequestParam(defaultValue = "init") String action,
            @RequestParam(required = false) Integer id,
            @org.springframework.security.core.annotation.AuthenticationPrincipal
            org.springframework.security.core.userdetails.UserDetails principal) {
        Usuario usuario = usuario(principal);
        if (usuario == null) return noAutenticado();
        if ("eliminar".equals(action)) {
            Tarea tarea = tareaDeEmpresa(usuario, id);
            if (tarea == null) return error("Tarea no encontrada");
            tareasRepository.delete(tarea);
            return ResponseEntity.ok(Map.of("success", true, "message", "Tarea eliminada"));
        }
        if (!"init".equals(action)) return error("Accion no soportada");

        List<Proyecto> proyectosEmpresa = proyectosDeEmpresa(usuario);
        List<Tarea> tareasEmpresa = proyectosEmpresa.stream()
                .flatMap(proyecto -> tareasRepository.findByProyectoIdProyecto(proyecto.getIdProyecto()).stream())
                .toList();
        return ResponseEntity.ok(Map.of("success", true, "data", Map.of(
                "usuario", usuarioData(usuario),
                "proyectos", proyectosEmpresa.stream().map(this::proyectoData).toList(),
                "tareas", tareasEmpresa.stream().map(this::tareaData).toList(),
                "stats", stats(tareasEmpresa))));
    }

    @PostMapping("/tareas")
    @Transactional
    public ResponseEntity<Map<String, Object>> modificarTarea(
            @RequestParam Map<String, String> form,
            @org.springframework.security.core.annotation.AuthenticationPrincipal
            org.springframework.security.core.userdetails.UserDetails principal) {
        Usuario usuario = usuario(principal);
        if (usuario == null) return noAutenticado();

        String action = form.getOrDefault("action", "crear");
        Integer idProyecto = integer(form.get("proyecto_id"));
        Proyecto proyecto = proyectoDeEmpresa(usuario, idProyecto);
        if (proyecto == null) return error("El proyecto no existe o no pertenece a tu empresa");

        String titulo = form.getOrDefault("titulo", "").trim();
        if (titulo.length() < 5 || titulo.length() > 200) return error("El titulo debe tener entre 5 y 200 caracteres");

        Tarea tarea;
        if ("actualizar".equals(action)) {
            tarea = tareaDeEmpresa(usuario, integer(form.get("id")));
            if (tarea == null) return error("Tarea no encontrada");
        } else if ("crear".equals(action)) {
            tarea = new Tarea();
        } else {
            return error("Accion no soportada");
        }

        tarea.setTitulo(titulo);
        tarea.setDescripcion(form.getOrDefault("descripcion", "").trim());
        tarea.setEstado(form.getOrDefault("estado", "Por Hacer"));
        tarea.setFechaVencimiento(parseDate(form.get("fecha_vencimiento")));
        tarea.setProyecto(proyecto);
        Tarea saved = tareasRepository.save(tarea);
        return ResponseEntity.ok(Map.of("success", true,
                "message", "actualizar".equals(action) ? "Tarea actualizada" : "Tarea creada",
                "data", tareaData(saved)));
    }

    @GetMapping("/equipos")
    public Map<String, Object> equipos(@RequestParam(defaultValue = "init") String action) {
        if ("no_leidos".equals(action)) return Map.of("success", true, "data", Map.of("total", 0));
        return Map.of("success", true, "data", Map.of("usuario", USER, "miembros", List.of(), "mensajes", List.of()));
    }

    @GetMapping("/analytics")
    public Map<String, Object> analytics() {
        return Map.of("success", true, "data", Map.of(
                "usuario", USER, "stats", List.of(), "tendencia", List.of(),
                "top_metricas", List.of(), "tiene_datos", false));
    }

    @PostMapping("/equipos")
    public ResponseEntity<Map<String, Object>> mutationPendingMigration() {
        return ResponseEntity.status(501).body(Map.of("success", false,
                "message", "Esta operación aún debe migrarse al servicio Spring Boot."));
    }

    private Usuario usuario(org.springframework.security.core.userdetails.UserDetails principal) {
        return principal == null ? null : usuarios.findByEmail(principal.getUsername()).orElse(null);
    }

    private List<Proyecto> proyectosDeEmpresa(Usuario usuario) {
        return usuario.getIdEmpresa() == null ? List.of() : proyectos.findByEmpresaIdEmpresa(usuario.getIdEmpresa());
    }

    private Proyecto proyectoDeEmpresa(Usuario usuario, Integer id) {
        if (id == null) return null;
        return proyectosDeEmpresa(usuario).stream().filter(proyecto -> id.equals(proyecto.getIdProyecto())).findFirst().orElse(null);
    }

    private Tarea tareaDeEmpresa(Usuario usuario, Integer id) {
        if (id == null) return null;
        Tarea tarea = tareasRepository.findById(id).orElse(null);
        return tarea != null && tarea.getProyecto() != null
                && usuario.getIdEmpresa() != null && tarea.getProyecto().getEmpresa() != null
                && usuario.getIdEmpresa().equals(tarea.getProyecto().getEmpresa().getIdEmpresa()) ? tarea : null;
    }

    private Map<String, Object> usuarioData(Usuario usuario) {
        String nombres = usuario.getNombres() == null ? "" : usuario.getNombres();
        String apellidos = usuario.getApellidos() == null ? "" : usuario.getApellidos();
        String nombre = (nombres + " " + apellidos).trim();
        String iniciales = nombre.isBlank() ? "US" : nombre.substring(0, 1).toUpperCase();
        return Map.of("iniciales", iniciales, "nombres", nombres, "apellidos", apellidos,
                "nombre_rol", usuario.getRol() == null ? "Usuario" : usuario.getRol().getNombre(),
                "cargo", usuario.getCargo() == null ? "Usuario" : usuario.getCargo());
    }

    private Map<String, Object> proyectoData(Proyecto proyecto) {
        return Map.of("id_proyecto", proyecto.getIdProyecto(), "nombre", text(proyecto.getNombre()));
    }

    private Map<String, Object> tareaData(Tarea tarea) {
        String estado = text(tarea.getEstado());
        boolean vencida = tarea.getFechaVencimiento() != null
                && tarea.getFechaVencimiento().isBefore(LocalDate.now()) && !"Completada".equalsIgnoreCase(estado);
        Usuario asignado = tarea.getUsuario();
        return Map.ofEntries(
                Map.entry("id_tarea", tarea.getIdTarea()), Map.entry("titulo", text(tarea.getTitulo())),
                Map.entry("descripcion", text(tarea.getDescripcion())), Map.entry("estado", estado),
                Map.entry("id_proyecto", tarea.getProyecto().getIdProyecto()),
                Map.entry("proyecto_nombre", text(tarea.getProyecto().getNombre())),
                Map.entry("fecha_vencimiento", tarea.getFechaVencimiento() == null ? "" : tarea.getFechaVencimiento().toString()),
                Map.entry("vencida", vencida), Map.entry("usuario_nombres", asignado == null ? "" : text(asignado.getNombres())),
                Map.entry("usuario_apellidos", asignado == null ? "" : text(asignado.getApellidos())));
    }

    private Map<String, Object> stats(List<Tarea> tareas) {
        long completadas = tareas.stream().filter(t -> "Completada".equalsIgnoreCase(t.getEstado())).count();
        long progreso = tareas.stream().filter(t -> "En Progreso".equalsIgnoreCase(t.getEstado())).count();
        long vencidas = tareas.stream().filter(t -> t.getFechaVencimiento() != null
                && t.getFechaVencimiento().isBefore(LocalDate.now())
                && !"Completada".equalsIgnoreCase(t.getEstado())).count();
        return Map.of("total", tareas.size(), "completadas", completadas, "en_progreso", progreso, "vencidas", vencidas);
    }

    private Integer integer(String value) { try { return value == null ? null : Integer.valueOf(value); } catch (NumberFormatException ex) { return null; } }
    private LocalDate parseDate(String value) { try { return value == null || value.isBlank() ? null : LocalDate.parse(value); } catch (RuntimeException ex) { return null; } }
    private String text(String value) { return value == null ? "" : value; }
    private ResponseEntity<Map<String, Object>> noAutenticado() { return ResponseEntity.status(401).body(Map.of("success", false, "message", "No autenticado")); }
    private ResponseEntity<Map<String, Object>> error(String message) { return ResponseEntity.badRequest().body(Map.of("success", false, "message", message)); }

    /** Keeps the supervisor shell on Spring while its individual services move. */
    @RequestMapping("/supervisor/**")
    public Map<String, Object> supervisorShellApi() {
        return Map.of("status", "success", "data", List.of());
    }

    /** Keeps the administrator shell on Spring while its individual services move. */
    @RequestMapping("/admin/**")
    public Map<String, Object> adminShellApi() {
        return Map.of("status", "success", "data", List.of());
    }
}
