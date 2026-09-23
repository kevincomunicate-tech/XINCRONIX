package com.Xincronix.controller;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

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
import com.Xincronix.repository.EquipoRepository;
import com.Xincronix.repository.MiembroEquipoRepository;
import com.Xincronix.repository.AutomatizacionRepository;
import com.Xincronix.repository.ActividadRepository;
import com.Xincronix.service.ActividadService;

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
            private final EquipoRepository equiposRepository;
            private final MiembroEquipoRepository miembrosEquipoRepository;
            private final AutomatizacionRepository automatizacionesRepository;
            private final ActividadService actividadService;

            public LegacyUiApiController(ProyectoRepository proyectos, TareaRepository tareasRepository,
                         UsuarioRepository usuarios, EquipoRepository equiposRepository,
                         MiembroEquipoRepository miembrosEquipoRepository,
                         AutomatizacionRepository automatizacionesRepository,
                         ActividadService actividadService) {
            this.proyectos = proyectos;
            this.tareasRepository = tareasRepository;
            this.usuarios = usuarios;
            this.equiposRepository = equiposRepository;
            this.miembrosEquipoRepository = miembrosEquipoRepository;
            this.automatizacionesRepository = automatizacionesRepository;
            this.actividadService = actividadService;
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
                    "tareas_total", tareasEmpresa.size(),
                    "equipos_total", empresaId == null ? 0 : equiposRepository.findByEmpresaIdEmpresa(empresaId).size(),
                    "automatizaciones_total", empresaId == null ? 0 : automatizacionesRepository.findByEmpresaIdEmpresaOrderByFechaCreacionDesc(empresaId).size(),
                    "tareas_esta_semana", tareasEmpresa.size(),
                    "issues_abiertos", 0),
                "actividades", actividadesSeguras(usuario), "proyectos", proyectosEmpresa.stream()
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

    private List<Map<String, Object>> actividadesDelUsuario(Usuario usuario, List<Tarea> tareasEmpresa) {
        List<Map<String, Object>> actividades = new ArrayList<>();
        tareasEmpresa.stream()
                .filter(tarea -> tarea.getUsuario() != null
                        && usuario.getIdUsuario().equals(tarea.getUsuario().getIdUsuario()))
                .sorted((a, b) -> fecha(b.getFechaCreacion()).compareTo(fecha(a.getFechaCreacion())))
                .limit(8)
                .forEach(tarea -> actividades.add(Map.of(
                        "usuario", nombreUsuario(usuario),
                        "descripcion", "actualizó la tarea",
                        "detalle", text(tarea.getTitulo()),
                        "tiempo_relativo", relativo(fecha(tarea.getFechaCreacion())))));
        automatizacionesRepository.findByCreadorIdUsuarioOrderByFechaCreacionDesc(usuario.getIdUsuario())
                .stream().limit(8).forEach(flujo -> actividades.add(Map.of(
                        "usuario", nombreUsuario(usuario),
                        "descripcion", "creó la automatización",
                        "detalle", text(flujo.getNombre()),
                        "tiempo_relativo", relativo(flujo.getFechaCreacion()))));
        return actividades.stream().limit(10).toList();
    }

    private List<Map<String, Object>> actividadesSeguras(Usuario usuario) {
        try {
            return actividadService.recientes(usuario);
        } catch (RuntimeException ex) {
            return List.of();
        }
    }

    private String nombreUsuario(Usuario usuario) {
        return (text(usuario.getNombres()) + " " + text(usuario.getApellidos())).trim();
    }

    private java.time.LocalDateTime fecha(java.time.LocalDateTime fecha) {
        return fecha == null ? java.time.LocalDateTime.MIN : fecha;
    }

    private String relativo(java.time.LocalDateTime fecha) {
        if (fecha.equals(java.time.LocalDateTime.MIN)) return "Sin fecha";
        long minutos = java.time.Duration.between(fecha, java.time.LocalDateTime.now()).toMinutes();
        if (minutos < 1) return "Ahora";
        if (minutos < 60) return "Hace " + minutos + " min";
        long horas = minutos / 60;
        if (horas < 24) return "Hace " + horas + " h";
        return "Hace " + (horas / 24) + " d";
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
            String titulo = tarea.getTitulo();
            tareasRepository.delete(tarea);
            actividadService.registrar(usuario, "Tareas", "ELIMINAR", titulo);
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

        String titulo = form.getOrDefault("titulo", "").trim();

        Tarea tarea;
        if ("actualizar".equals(action)) {
            tarea = tareaDeEmpresa(usuario, integer(form.get("id")));
            if (tarea == null) return error("Tarea no encontrada");
            if (!titulo.isBlank()) {
                if (titulo.length() < 5 || titulo.length() > 200) return error("El titulo debe tener entre 5 y 200 caracteres");
                tarea.setTitulo(titulo);
            }
        } else if ("crear".equals(action)) {
            Proyecto proyecto = proyectoDeEmpresa(usuario, idProyecto);
            if (proyecto == null) return error("El proyecto no existe o no pertenece a tu empresa");
            if (titulo.length() < 5 || titulo.length() > 200) return error("El titulo debe tener entre 5 y 200 caracteres");
            tarea = new Tarea();
            tarea.setProyecto(proyecto);
        } else {
            return error("Accion no soportada");
        }

        if (form.containsKey("descripcion")) tarea.setDescripcion(form.get("descripcion").trim());
        if (form.containsKey("estado")) tarea.setEstado(form.get("estado"));
        if (form.containsKey("fecha_vencimiento")) tarea.setFechaVencimiento(parseDate(form.get("fecha_vencimiento")));
        Tarea saved = tareasRepository.save(tarea);
        actividadService.registrar(usuario, "Tareas",
                "actualizar".equals(action) ? "ACTUALIZAR" : "CREAR", saved.getTitulo());
        return ResponseEntity.ok(Map.of("success", true,
                "message", "actualizar".equals(action) ? "Tarea actualizada" : "Tarea creada",
                "data", tareaData(saved)));
    }

    @GetMapping("/equipos")
    public Map<String, Object> equipos(@RequestParam(defaultValue = "init") String action,
                                       @org.springframework.security.core.annotation.AuthenticationPrincipal
                                       org.springframework.security.core.userdetails.UserDetails principal) {
        if ("no_leidos".equals(action)) return Map.of("success", true, "data", Map.of("total", 0));
        Usuario usuario = usuario(principal);
        if (usuario == null) return Map.of("success", false, "message", "No autenticado");
        var equipos = usuario.getIdEmpresa() == null ? List.<com.Xincronix.model.Equipo>of()
                : equiposRepository.findByEmpresaIdEmpresa(usuario.getIdEmpresa());
        var miembros = equipos.stream().flatMap(equipo -> miembrosEquipoRepository.findByEquipoIdEquipo(equipo.getIdEquipo()).stream())
                .filter(miembro -> !usuario.getIdUsuario().equals(miembro.getUsuario().getIdUsuario()))
                .map(miembro -> {
                    Usuario miembroUsuario = miembro.getUsuario();
                    Map<String, Object> data = new HashMap<>(usuarioData(miembroUsuario));
                    data.put("id_equipo", miembro.getEquipo().getIdEquipo());
                    data.put("id_usuario", miembroUsuario.getIdUsuario());
                    data.put("email", text(miembroUsuario.getEmail()));
                    data.put("rol_en_equipo", text(miembro.getRolEnEquipo()));
                    data.put("estado", 1);
                    data.put("tareas_activas", 0);
                    data.put("proyectos", 0);
                    data.put("on_time", 100);
                    data.put("carga_pct", 0);
                    return data;
                }).toList();
        return Map.of("success", true, "data", Map.of("usuario", usuarioData(usuario),
                "equipos", equipos.stream().map(equipo -> Map.of("id_equipo", equipo.getIdEquipo(), "nombre", text(equipo.getNombre()),
                        "descripcion", text(equipo.getDescripcion()), "miembros", equipo.getMiembros() == null ? 0 : equipo.getMiembros())).toList(),
                "miembros", miembros, "mensajes", List.of()));
    }

    /**
     * Reportes de tareas aislados por empresa. El alcance individual sólo incluye
     * tareas asignadas al usuario de la sesión; ningún filtro puede salir de su empresa.
     */
    @GetMapping("/analytics")
    @Transactional
    public ResponseEntity<Map<String, Object>> analytics(
            @RequestParam(defaultValue = "empresa") String alcance,
            @RequestParam(required = false) String estado,
            @RequestParam(required = false) String prioridad,
            @RequestParam(required = false) String desde,
            @RequestParam(required = false) String hasta,
            @org.springframework.security.core.annotation.AuthenticationPrincipal
            org.springframework.security.core.userdetails.UserDetails principal) {
        Usuario usuario = usuario(principal);
        if (usuario == null) return noAutenticado();

        boolean individual = "individual".equalsIgnoreCase(alcance);
        LocalDate fechaDesde = parseDate(desde);
        LocalDate fechaHasta = parseDate(hasta);
        List<Tarea> filtradas = proyectosDeEmpresa(usuario).stream()
                .flatMap(proyecto -> tareasRepository.findByProyectoIdProyecto(proyecto.getIdProyecto()).stream())
                .filter(tarea -> !individual || (tarea.getUsuario() != null
                        && usuario.getIdUsuario().equals(tarea.getUsuario().getIdUsuario())))
                .filter(tarea -> coincide(tarea.getEstado(), estado))
                .filter(tarea -> coincide(tarea.getPrioridad(), prioridad))
                .filter(tarea -> dentroDelPeriodo(tarea, fechaDesde, fechaHasta))
                .toList();

        long completadas = filtradas.stream().filter(this::estaCompletada).count();
        long enProgreso = filtradas.stream().filter(tarea -> "en progreso".equals(normalizar(tarea.getEstado()))).count();
        long vencidas = filtradas.stream().filter(this::estaVencida).count();
        List<Map<String, Object>> tendencia = tendencia(filtradas);
        List<Map<String, Object>> metricas = metricasPorProyecto(filtradas);

        return ResponseEntity.ok(Map.of("success", true, "data", Map.of(
                "usuario", usuarioData(usuario),
                "alcance", individual ? "individual" : "empresa",
                "alcance_label", individual ? "Mis tareas asignadas" : "Operación de mi empresa",
                "criterios", Map.of("estado", text(estado), "prioridad", text(prioridad),
                        "desde", fechaDesde == null ? "" : fechaDesde.toString(),
                        "hasta", fechaHasta == null ? "" : fechaHasta.toString()),
                "stats", List.of(
                        analyticsStat("Tareas analizadas", filtradas.size(), "Según los filtros aplicados", "up"),
                        analyticsStat("Completadas", completadas, porcentaje(completadas, filtradas.size()) + " del total", "up"),
                        analyticsStat("En progreso", enProgreso, "Pendientes de completar", "up"),
                        analyticsStat("Vencidas", vencidas, vencidas == 0 ? "Sin retrasos" : "Requieren atención", vencidas == 0 ? "up" : "down")),
                "tendencia", tendencia,
                "top_metricas", metricas,
                "tiene_datos", !filtradas.isEmpty())));
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
        return Map.of("id_usuario", usuario.getIdUsuario(), "iniciales", iniciales, "nombres", nombres, "apellidos", apellidos,
                "nombre_rol", usuario.getRol() == null ? "Usuario" : usuario.getRol().getNombre(),
                "cargo", usuario.getCargo() == null || usuario.getCargo().isBlank()
                        ? (usuario.getRol() == null ? "Usuario" : usuario.getRol().getNombre())
                        : usuario.getCargo());
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

    private List<Map<String, Object>> tendencia(List<Tarea> tareas) {
        LocalDate primerDia = LocalDate.now().minusDays(6);
        List<Map<String, Object>> resultado = new ArrayList<>();
        for (int offset = 0; offset < 7; offset++) {
            LocalDate fecha = primerDia.plusDays(offset);
            long total = tareas.stream().filter(tarea -> tarea.getFechaCreacion() != null
                    && fecha.equals(tarea.getFechaCreacion().toLocalDate())).count();
            resultado.add(Map.of("fecha", fecha.toString(), "total", total));
        }
        return resultado;
    }

    private List<Map<String, Object>> metricasPorProyecto(List<Tarea> tareas) {
        Map<Proyecto, List<Tarea>> porProyecto = new LinkedHashMap<>();
        for (Tarea tarea : tareas) {
            if (tarea.getProyecto() != null) porProyecto.computeIfAbsent(tarea.getProyecto(), ignored -> new ArrayList<>()).add(tarea);
        }
        return porProyecto.entrySet().stream().map(entry -> {
            int total = entry.getValue().size();
            long completadas = entry.getValue().stream().filter(this::estaCompletada).count();
            int progreso = total == 0 ? 0 : (int) Math.round(completadas * 100.0 / total);
            return Map.<String, Object>of(
                    "indicador", text(entry.getKey().getNombre()),
                    "valor", completadas + " / " + total + " tareas",
                    "meta", "100% completadas (" + progreso + "% actual)",
                    "cumplida", total > 0 && completadas == total);
        }).sorted((primera, segunda) -> String.valueOf(segunda.get("valor")).compareTo(String.valueOf(primera.get("valor"))))
                .limit(10).toList();
    }

    private Map<String, Object> analyticsStat(String label, Object valor, String tendencia, String direccion) {
        return Map.of("label", label, "valor", String.valueOf(valor), "tendencia", tendencia, "direccion", direccion);
    }

    private boolean dentroDelPeriodo(Tarea tarea, LocalDate desde, LocalDate hasta) {
        if (desde == null && hasta == null) return true;
        if (tarea.getFechaCreacion() == null) return false;
        LocalDate fecha = tarea.getFechaCreacion().toLocalDate();
        return (desde == null || !fecha.isBefore(desde)) && (hasta == null || !fecha.isAfter(hasta));
    }

    private boolean coincide(String valor, String criterio) {
        return criterio == null || criterio.isBlank() || "todos".equalsIgnoreCase(criterio)
                || normalizar(valor).equals(normalizar(criterio));
    }

    private boolean estaCompletada(Tarea tarea) { return normalizar(tarea.getEstado()).contains("complet"); }
    private boolean estaVencida(Tarea tarea) {
        return tarea.getFechaVencimiento() != null && tarea.getFechaVencimiento().isBefore(LocalDate.now()) && !estaCompletada(tarea);
    }
    private String porcentaje(long valor, int total) { return total == 0 ? "0%" : Math.round(valor * 100.0 / total) + "%"; }
    private String normalizar(String value) { return text(value).toLowerCase(Locale.ROOT); }

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
