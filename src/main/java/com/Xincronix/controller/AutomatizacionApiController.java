package com.Xincronix.controller;

import com.Xincronix.model.Automatizacion;
import com.Xincronix.model.Usuario;
import com.Xincronix.repository.AutomatizacionRepository;
import com.Xincronix.repository.UsuarioRepository;
import com.Xincronix.service.ActividadService;
import jakarta.transaction.Transactional;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PutMapping;

/** Company-scoped workflow definitions used by the Automations screen. */
@RestController
@RequestMapping("/api/automatizaciones")
public class AutomatizacionApiController {
    private static final DateTimeFormatter DATE_TIME = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm");

    private final AutomatizacionRepository automatizaciones;
    private final UsuarioRepository usuarios;
    private final ActividadService actividadService;

    public AutomatizacionApiController(AutomatizacionRepository automatizaciones, UsuarioRepository usuarios,
                                       ActividadService actividadService) {
        this.automatizaciones = automatizaciones;
        this.usuarios = usuarios;
        this.actividadService = actividadService;
    }

    @GetMapping
    @Transactional
    public ResponseEntity<Map<String, Object>> listar(@AuthenticationPrincipal UserDetails principal) {
        Usuario usuario = usuario(principal);
        if (usuario == null) return noAutenticado();

        List<Automatizacion> flujos = usuario.getIdEmpresa() == null
                ? List.of()
                : automatizaciones.findByEmpresaIdEmpresaOrderByFechaCreacionDesc(usuario.getIdEmpresa());
        long activas = flujos.stream().filter(flujo -> Boolean.TRUE.equals(flujo.getActiva())).count();
        long ejecuciones = flujos.stream().mapToLong(flujo -> numero(flujo.getEjecuciones())).sum();
        long exitos = flujos.stream().mapToLong(flujo -> numero(flujo.getExitos())).sum();
        long errores = flujos.stream().mapToLong(flujo -> numero(flujo.getErrores())).sum();
        String tasaExito = ejecuciones == 0 ? "—" : String.format(Locale.ROOT, "%.1f%%", exitos * 100.0 / ejecuciones);

        return ResponseEntity.ok(Map.of("success", true, "data", Map.of(
                "usuario", usuarioData(usuario),
                "stats", List.of(
                        stat("Flujos activos", activas, "Configurados para tu empresa"),
                        stat("Ejecuciones", ejecuciones, "Registradas por tus flujos"),
                        stat("Éxitos", tasaExito, ejecuciones == 0 ? "Aún sin ejecuciones" : exitos + " completadas"),
                        stat("Errores", errores, errores == 0 ? "Sin errores registrados" : "Revisa los flujos afectados")),
                "flujos", flujos.stream().map(this::flujoData).toList(),
                "tiene_datos", !flujos.isEmpty())));
    }

    @PostMapping
    @Transactional
    public ResponseEntity<Map<String, Object>> crear(@Valid @RequestBody CrearFlujoRequest request,
                                                      @AuthenticationPrincipal UserDetails principal) {
        Usuario usuario = usuario(principal);
        if (usuario == null) return noAutenticado();
        if (usuario.getEmpresa() == null) return error("Tu cuenta no tiene una empresa asignada.");

        Automatizacion flujo = new Automatizacion();
        flujo.setEmpresa(usuario.getEmpresa());
        flujo.setCreador(usuario);
        flujo.setNombre(request.nombre().trim());
        flujo.setDisparador(request.disparador().trim());
        flujo.setDescripcion(text(request.descripcion()));
        flujo.setActiva(Boolean.TRUE);
        Automatizacion saved = automatizaciones.save(flujo);
        actividadService.registrar(usuario, "Automatizaciones", "CREAR", saved.getNombre());
        return ResponseEntity.status(201).body(Map.of("success", true, "message", "Flujo creado.",
                "data", flujoData(saved)));
    }

    @PatchMapping("/{id}/estado")
    @Transactional
    public ResponseEntity<Map<String, Object>> cambiarEstado(@PathVariable Integer id,
                                                              @Valid @RequestBody EstadoFlujoRequest request,
                                                              @AuthenticationPrincipal UserDetails principal) {
        Usuario usuario = usuario(principal);
        if (usuario == null) return noAutenticado();
        if (usuario.getIdEmpresa() == null) return error("Tu cuenta no tiene una empresa asignada.");
        Automatizacion flujo = automatizaciones.findByIdAutomatizacionAndEmpresaIdEmpresa(id, usuario.getIdEmpresa())
                .orElse(null);
        if (flujo == null) return ResponseEntity.status(404).body(Map.of("success", false, "message", "Flujo no encontrado."));

        flujo.setActiva(request.activa());
        actividadService.registrar(usuario, "Automatizaciones", "ACTUALIZAR", flujo.getNombre());
        return ResponseEntity.ok(Map.of("success", true,
                "message", Boolean.TRUE.equals(request.activa()) ? "Flujo activado." : "Flujo pausado.",
                "data", flujoData(flujo)));
    }

    @PutMapping("/{id}")
    @Transactional
    public ResponseEntity<Map<String, Object>> actualizar(@PathVariable Integer id,
            @Valid @RequestBody CrearFlujoRequest request,
            @AuthenticationPrincipal UserDetails principal) {
        Usuario usuario = usuario(principal);
        if (usuario == null) return noAutenticado();
        Automatizacion flujo = automatizaciones.findByIdAutomatizacionAndEmpresaIdEmpresa(id, usuario.getIdEmpresa()).orElse(null);
        if (flujo == null) return ResponseEntity.status(404).body(Map.of("success", false, "message", "Flujo no encontrado."));
        flujo.setNombre(request.nombre().trim());
        flujo.setDisparador(request.disparador().trim());
        flujo.setDescripcion(text(request.descripcion()));
        Automatizacion saved = automatizaciones.save(flujo);
        actividadService.registrar(usuario, "Automatizaciones", "ACTUALIZAR", saved.getNombre());
        return ResponseEntity.ok(Map.of("success", true, "message", "Flujo actualizado.",
                "data", flujoData(saved)));
    }

    @DeleteMapping("/{id}")
    @Transactional
    public ResponseEntity<Map<String, Object>> eliminar(@PathVariable Integer id,
            @AuthenticationPrincipal UserDetails principal) {
        Usuario usuario = usuario(principal);
        if (usuario == null) return noAutenticado();
        Automatizacion flujo = automatizaciones.findByIdAutomatizacionAndEmpresaIdEmpresa(id, usuario.getIdEmpresa()).orElse(null);
        if (flujo == null) return ResponseEntity.status(404).body(Map.of("success", false, "message", "Flujo no encontrado."));
        String nombre = flujo.getNombre();
        automatizaciones.delete(flujo);
        actividadService.registrar(usuario, "Automatizaciones", "ELIMINAR", nombre);
        return ResponseEntity.ok(Map.of("success", true, "message", "Flujo eliminado.", "data", Map.of("id", id)));
    }

    private Usuario usuario(UserDetails principal) {
        return principal == null ? null : usuarios.findByEmailIgnoreCase(principal.getUsername()).orElse(null);
    }

    private Map<String, Object> flujoData(Automatizacion flujo) {
        String creador = flujo.getCreador() == null ? "" : nombre(flujo.getCreador());
        long ejecuciones = numero(flujo.getEjecuciones());
        long exitos = numero(flujo.getExitos());
        String resultado = ejecuciones == 0 ? "Aún sin ejecuciones" : String.format(Locale.ROOT, "Éxito %.1f%%", exitos * 100.0 / ejecuciones);
        return Map.ofEntries(
                Map.entry("id", flujo.getIdAutomatizacion()),
                Map.entry("nombre", text(flujo.getNombre())),
                Map.entry("disparador", text(flujo.getDisparador())),
                Map.entry("descripcion", text(flujo.getDescripcion())),
                Map.entry("activa", Boolean.TRUE.equals(flujo.getActiva())),
                Map.entry("ejecuciones", ejecuciones),
                Map.entry("exitos", exitos),
                Map.entry("errores", numero(flujo.getErrores())),
                Map.entry("resultado", resultado),
                Map.entry("ultima_ejecucion", flujo.getUltimaEjecucion() == null ? "Sin ejecuciones" : DATE_TIME.format(flujo.getUltimaEjecucion())),
                Map.entry("creador", creador));
    }

    private Map<String, Object> usuarioData(Usuario usuario) {
        String nombre = nombre(usuario);
        String cargo = text(usuario.getCargo());
        return Map.of("iniciales", nombre.isBlank() ? "US" : nombre.substring(0, 1).toUpperCase(Locale.ROOT),
                "nombre", nombre,
                "cargo", cargo.isBlank()
                        ? (usuario.getRol() == null ? "Usuario" : text(usuario.getRol().getNombre()))
                        : cargo,
                "rol", usuario.getRol() == null ? "Usuario" : text(usuario.getRol().getNombre()));
    }

    private static Map<String, Object> stat(String label, Object valor, String detalle) {
        return Map.of("label", label, "valor", String.valueOf(valor), "detalle", detalle);
    }
    private static long numero(Long valor) { return valor == null ? 0L : valor; }
    private static String nombre(Usuario usuario) { return (text(usuario.getNombres()) + " " + text(usuario.getApellidos())).trim(); }
    private static String text(String value) { return value == null ? "" : value.trim(); }
    private static ResponseEntity<Map<String, Object>> noAutenticado() { return ResponseEntity.status(401).body(Map.of("success", false, "message", "No autenticado")); }
    private static ResponseEntity<Map<String, Object>> error(String message) { return ResponseEntity.badRequest().body(Map.of("success", false, "message", message)); }

    public record CrearFlujoRequest(
            @NotBlank @Size(max = 150) String nombre,
            @NotBlank @Size(max = 150) String disparador,
            @Size(max = 5000) String descripcion) { }
    public record EstadoFlujoRequest(@NotNull Boolean activa) { }
}
