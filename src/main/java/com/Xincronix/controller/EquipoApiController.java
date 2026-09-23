package com.Xincronix.controller;

import com.Xincronix.dto.EquipoRequest;
import com.Xincronix.dto.EquipoResponse;
import com.Xincronix.dto.MiembroEquipoRequest;
import com.Xincronix.dto.MiembroEquipoResponse;
import com.Xincronix.model.Equipo;
import com.Xincronix.model.MiembroEquipo;
import com.Xincronix.model.Usuario;
import com.Xincronix.repository.EquipoRepository;
import com.Xincronix.repository.MiembroEquipoRepository;
import com.Xincronix.repository.UsuarioRepository;
import com.Xincronix.service.ActividadService;
import jakarta.transaction.Transactional;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/equipos")
/** All team exports and mutations are scoped to the authenticated user's empresa. */
public class EquipoApiController {
    private final EquipoRepository equipos;
    private final MiembroEquipoRepository miembros;
    private final UsuarioRepository usuarios;
    private final ActividadService actividadService;

    public EquipoApiController(EquipoRepository equipos, MiembroEquipoRepository miembros, UsuarioRepository usuarios,
                               ActividadService actividadService) {
        this.equipos = equipos; this.miembros = miembros; this.usuarios = usuarios; this.actividadService = actividadService;
    }

    @PostMapping(consumes = "application/json") @Transactional
    public ResponseEntity<Map<String, Object>> crear(@Valid @RequestBody EquipoRequest request, @AuthenticationPrincipal UserDetails principal) {
        Usuario actor = actor(principal); Equipo equipo = new Equipo(); apply(equipo, request, actor);
        Equipo saved = equipos.save(equipo); syncMiembros(saved, request.miembrosIds(), actor);
        saved.setMiembros(miembros.findByEquipoIdEquipo(saved.getIdEquipo()).size());
        saved = equipos.save(saved);
        actividadService.registrar(actor, "Equipo", "CREAR", saved.getNombre());
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of("success", true, "data", Map.of("equipo", EquipoResponse.from(saved))));
    }

    @PutMapping(consumes = "application/json") @Transactional
    public ResponseEntity<Map<String, Object>> actualizar(@RequestParam Integer id, @Valid @RequestBody EquipoRequest request, @AuthenticationPrincipal UserDetails principal) {
        Usuario actor = actor(principal); Equipo equipo = equipoDeEmpresa(id, actor); if (equipo == null) return notFound();
        apply(equipo, request, actor); Equipo saved = equipos.save(equipo); syncMiembros(saved, request.miembrosIds(), actor);
        actividadService.registrar(actor, "Equipo", "ACTUALIZAR", saved.getNombre());
        return ResponseEntity.ok(Map.of("success", true, "data", Map.of("equipo", EquipoResponse.from(saved))));
    }

    @DeleteMapping @Transactional
    public ResponseEntity<Map<String, Object>> eliminar(@RequestParam Integer id, @AuthenticationPrincipal UserDetails principal) {
        Equipo equipo = equipoDeEmpresa(id, actor(principal)); if (equipo == null) return notFound();
        String nombre = equipo.getNombre();
        miembros.deleteAll(miembros.findByEquipoIdEquipo(equipo.getIdEquipo())); equipos.delete(equipo);
        actividadService.registrar(actor(principal), "Equipo", "ELIMINAR", nombre);
        return ResponseEntity.ok(Map.of("success", true, "data", Map.of("id", id)));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> obtener(@PathVariable Integer id, @AuthenticationPrincipal UserDetails principal) {
        Equipo equipo = equipoDeEmpresa(id, actor(principal)); if (equipo == null) return notFound();
        return ResponseEntity.ok(Map.of("success", true, "data", Map.of("equipo", EquipoResponse.from(equipo))));
    }

    @GetMapping("/{id}/miembros") @Transactional
    public ResponseEntity<Map<String, Object>> listarMiembros(@PathVariable Integer id, @AuthenticationPrincipal UserDetails principal) {
        Usuario usuarioActual = actor(principal);
        Equipo equipo = equipoDeEmpresa(id, usuarioActual); if (equipo == null) return notFound();
        return ResponseEntity.ok(Map.of("success", true, "data", Map.of("miembros",
                miembros.findByEquipoIdEquipo(equipo.getIdEquipo()).stream()
                        .map(MiembroEquipoResponse::from).toList())));
    }

    @PostMapping(path = "/{id}/miembros", consumes = "application/json") @Transactional
    public ResponseEntity<Map<String, Object>> agregarMiembro(@PathVariable Integer id,
            @Valid @RequestBody MiembroEquipoRequest request, @AuthenticationPrincipal UserDetails principal) {
        Usuario actor = actor(principal); Equipo equipo = equipoDeEmpresa(id, actor); if (equipo == null) return notFound();
        Usuario usuario = usuarioDeEmpresa(request.idUsuario(), actor);
        if (usuario == null) throw new IllegalArgumentException("El usuario no pertenece a tu empresa");
        if (miembros.findByEquipoIdEquipoAndUsuarioIdUsuario(id, request.idUsuario()).isPresent()) {
            throw new IllegalArgumentException("El usuario ya pertenece al equipo");
        }
        MiembroEquipo miembro = new MiembroEquipo(); miembro.setEquipo(equipo); miembro.setUsuario(usuario);
        miembro.setRolEnEquipo(request.rolEnEquipo()); miembro.setFechaIngreso(LocalDateTime.now());
        MiembroEquipo saved = miembros.save(miembro);
        equipo.setMiembros(miembros.findByEquipoIdEquipo(id).size());
        equipos.save(equipo);
        actividadService.registrar(actor, "Equipo", "AGREGAR", usuario.getNombres() + " al equipo " + equipo.getNombre());
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of("success", true,
                "data", Map.of("miembro", MiembroEquipoResponse.from(saved))));
    }

    @DeleteMapping("/{id}/miembros/{idUsuario}") @Transactional
    public ResponseEntity<Map<String, Object>> quitarMiembro(@PathVariable Integer id, @PathVariable Integer idUsuario,
            @AuthenticationPrincipal UserDetails principal) {
        Equipo equipo = equipoDeEmpresa(id, actor(principal)); if (equipo == null) return notFound();
        MiembroEquipo miembro = miembros.findByEquipoIdEquipoAndUsuarioIdUsuario(equipo.getIdEquipo(), idUsuario).orElse(null);
        if (miembro == null) return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(Map.of("success", false, "message", "Miembro no encontrado"));
        miembros.delete(miembro);
        equipo.setMiembros(miembros.findByEquipoIdEquipo(equipo.getIdEquipo()).size());
        equipos.save(equipo);
        actividadService.registrar(actor(principal), "Equipo", "QUITAR", miembro.getUsuario().getNombres() + " del equipo " + equipo.getNombre());
        return ResponseEntity.ok(Map.of("success", true, "data", Map.of("idUsuario", idUsuario)));
    }

    private void apply(Equipo equipo, EquipoRequest request, Usuario actor) {
        equipo.setNombre(request.nombre().trim()); equipo.setDescripcion(request.descripcion()); equipo.setMiembros(request.miembros());
        equipo.setFechaInicio(request.fechaInicio()); equipo.setFechaFin(request.fechaFin()); equipo.setEmpresa(actor.getEmpresa());
    }
    private void syncMiembros(Equipo equipo, List<Integer> ids, Usuario actor) {
        if (ids == null) return; miembros.deleteAll(miembros.findByEquipoIdEquipo(equipo.getIdEquipo()));
        for (Integer idUsuario : ids.stream().distinct().toList()) {
            Usuario usuario = usuarios.findById(idUsuario).orElseThrow(() -> new IllegalArgumentException("Usuario no encontrado"));
            if (!actor.getIdEmpresa().equals(usuario.getIdEmpresa())) throw new IllegalArgumentException("El usuario no pertenece a tu empresa");
            MiembroEquipo miembro = new MiembroEquipo(); miembro.setEquipo(equipo); miembro.setUsuario(usuario);
            miembro.setRolEnEquipo(actor.getIdUsuario().equals(idUsuario) ? "Creador del equipo" : "Miembro");
            miembro.setFechaIngreso(LocalDateTime.now()); miembros.save(miembro);
        }
    }
    private Usuario actor(UserDetails principal) { return usuarios.findByEmail(principal.getUsername()).orElseThrow(); }
    private Usuario usuarioDeEmpresa(Integer id, Usuario actor) {
        return usuarios.findById(id).filter(usuario -> actor.getIdEmpresa().equals(usuario.getIdEmpresa())).orElse(null);
    }
    private Equipo equipoDeEmpresa(Integer id, Usuario actor) { return equipos.findById(id).filter(e -> actor.getIdEmpresa().equals(e.getEmpresa().getIdEmpresa())).orElse(null); }
    private ResponseEntity<Map<String, Object>> notFound() { return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("success", false, "message", "Equipo no encontrado")); }
}
