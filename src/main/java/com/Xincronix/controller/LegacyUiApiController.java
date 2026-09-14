package com.Xincronix.controller;

import java.util.List;
import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.Xincronix.model.Usuario;
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
            public Map<String, Object> dashboard(@org.springframework.security.core.annotation.AuthenticationPrincipal
                             org.springframework.security.core.userdetails.UserDetails principal) {
            Usuario usuario = usuarios.findByEmail(principal.getUsername()).orElseThrow();
            Integer empresaId = usuario.getIdEmpresa();
            var proyectosEmpresa = empresaId == null ? List.<com.Xincronix.model.Proyecto>of()
                : proyectos.findByEmpresaIdEmpresa(empresaId);
            Map<String, Object> usuarioData = Map.of(
                "nombre", (usuario.getNombres() + " " + usuario.getApellidos()).trim(),
                "rol", usuario.getRol() != null ? usuario.getRol().getNombre() : "Usuario",
                "cargo", usuario.getCargo() == null ? "Usuario" : usuario.getCargo());
        return Map.of("status", "success", "data", Map.of(
                "usuario", usuarioData,
                "estadisticas", Map.of(
                    "proyectos_activos", proyectosEmpresa.size(),
                    "proyectos_este_mes", proyectosEmpresa.size(),
                    "tareas_completadas", tareasRepository.count(),
                    "tareas_esta_semana", tareasRepository.count(),
                    "agentes_activos", 0,
                    "agentes_en_espera", 0,
                    "issues_abiertos", 0),
                "actividades", List.of(), "proyectos", proyectosEmpresa.stream()
                    .map(proyecto -> Map.of("nombre", proyecto.getNombre(), "porcentaje", 0))
                    .toList()));
    }

    @GetMapping("/tareas")
    public Map<String, Object> tareas(@RequestParam(defaultValue = "init") String action) {
        return Map.of("success", true, "data", Map.of(
                "usuario", USER, "proyectos", List.of(), "tareas", List.of(),
                "stats", Map.of("total", 0, "pendientes", 0, "progreso", 0, "completadas", 0)));
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

    @PostMapping({"/tareas", "/equipos"})
    public ResponseEntity<Map<String, Object>> mutationPendingMigration() {
        return ResponseEntity.status(501).body(Map.of("success", false,
                "message", "Esta operación aún debe migrarse al servicio Spring Boot."));
    }

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
