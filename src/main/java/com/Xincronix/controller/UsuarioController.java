package com.Xincronix.controller;

import java.util.List;
import java.util.Map;

import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestAttribute;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.Xincronix.dto.UsuarioRequest;
import com.Xincronix.dto.UsuarioResponse;
import com.Xincronix.model.Usuario;
import com.Xincronix.service.UsuarioService;

@RestController
@RequestMapping("/api/usuarios")
public class UsuarioController {
    private final UsuarioService usuarioService;

    public UsuarioController(UsuarioService usuarioService) { this.usuarioService = usuarioService; }

    @GetMapping
    public ResponseEntity<?> index(@RequestAttribute Usuario usuarioActual) {
        List<UsuarioResponse> usuarios = usuarioService.listar(usuarioActual).stream()
                .map(UsuarioResponse::from).toList();
        return ResponseEntity.ok(Map.of("success", true, "message", "Usuarios obtenidos", "data", usuarios));
    }

    @PostMapping
    public ResponseEntity<?> store(@RequestAttribute Usuario usuarioActual, @Valid @RequestBody UsuarioRequest request) {
        Usuario creado = usuarioService.crear(usuarioActual, request);
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of("success", true,
                "message", "Usuario creado", "data", UsuarioResponse.from(creado)));
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> show(@RequestAttribute Usuario usuarioActual, @PathVariable Integer id) {
        return ResponseEntity.ok(Map.of("success", true,
                "data", UsuarioResponse.from(usuarioService.obtener(usuarioActual, id))));
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> update(@RequestAttribute Usuario usuarioActual, @PathVariable Integer id,
            @Valid @RequestBody UsuarioRequest request) {
        Usuario actualizado = usuarioService.actualizar(usuarioActual, id, request);
        return ResponseEntity.ok(Map.of("success", true, "message", "Usuario actualizado",
                "data", UsuarioResponse.from(actualizado)));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> destroy(@RequestAttribute Usuario usuarioActual, @PathVariable Integer id) {
        usuarioService.eliminar(usuarioActual, id);
        return ResponseEntity.ok(Map.of("success", true, "message", "Usuario eliminado"));
    }
}
