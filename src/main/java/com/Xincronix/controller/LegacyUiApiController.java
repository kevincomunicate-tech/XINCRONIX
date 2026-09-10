package com.Xincronix.controller;

import java.util.List;
import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

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

    @GetMapping("/dashboard")
    public Map<String, Object> dashboard() {
        return Map.of("status", "success", "data", Map.of(
                "usuario", Map.of("nombre", "Usuario Xincronix", "rol", "Usuario"),
                "estadisticas", Map.of(), "actividades", List.of(), "proyectos", List.of()));
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

    @PostMapping("/auth/logout")
    public Map<String, Object> logout() {
        return Map.of("success", true, "message", "Sesión cerrada");
    }

    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> loginPendingMigration() {
        return ResponseEntity.status(501).body(Map.of("success", false,
                "message", "La autenticación aún debe migrarse al servicio Spring Boot."));
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
