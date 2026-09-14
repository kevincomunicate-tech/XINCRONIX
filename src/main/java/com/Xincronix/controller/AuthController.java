package com.Xincronix.controller;

import com.Xincronix.dto.AuthResponse;
import com.Xincronix.dto.LoginRequest;
import com.Xincronix.dto.RegistroEmpresaRequest;
import com.Xincronix.model.Usuario;
import com.Xincronix.repository.UsuarioRepository;
import com.Xincronix.security.JwtService;
import com.Xincronix.service.RegistroEmpresaService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.time.Duration;
import java.util.Map;
import org.springframework.http.ResponseCookie;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthenticationManager authenticationManager;
    private final UserDetailsService userDetailsService;
    private final JwtService jwtService;
    private final UsuarioRepository usuarioRepository;
    private final RegistroEmpresaService registroEmpresaService;

    public AuthController(AuthenticationManager authenticationManager,
                          UserDetailsService userDetailsService,
                          JwtService jwtService,
                          UsuarioRepository usuarioRepository,
                          RegistroEmpresaService registroEmpresaService) {
        this.authenticationManager = authenticationManager;
        this.userDetailsService = userDetailsService;
        this.jwtService = jwtService;
        this.usuarioRepository = usuarioRepository;
        this.registroEmpresaService = registroEmpresaService;
    }

    @PostMapping(value = {"/register", "/registro"}, consumes = "multipart/form-data")
    public ResponseEntity<?> register(@Valid @ModelAttribute RegistroEmpresaRequest request,
                                      @RequestParam("comprobante") MultipartFile comprobante) {
        Usuario usuario = registroEmpresaService.registrar(request, comprobante);
        UserDetails userDetails = userDetailsService.loadUserByUsername(usuario.getEmail());
        String token = jwtService.generateToken(userDetails);
        AuthResponse response = new AuthResponse(token, "Bearer", usuario.getIdUsuario(),
                usuario.getNombres() + " " + usuario.getApellidos(), usuario.getEmail(),
                usuario.getRol().getNombre(), usuario.getEmpresa().getIdEmpresa(), usuario.getEmpresa().getNombre());
        return ResponseEntity.status(201)
                .header("Set-Cookie", accessTokenCookie(token).toString())
                .body(Map.of("success", true,
                "message", "Empresa y administrador registrados correctamente", "data", response));
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@Valid @RequestBody LoginRequest request) {
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.email(), request.password())
        );

        UserDetails userDetails = userDetailsService.loadUserByUsername(request.email());
        String token = jwtService.generateToken(userDetails);

        Usuario usuario = usuarioRepository.findByEmail(request.email()).orElseThrow();

        AuthResponse response = new AuthResponse(
                token,
                "Bearer",
                usuario.getIdUsuario(),
                usuario.getNombres() + " " + usuario.getApellidos(),
                usuario.getEmail(),
                usuario.getRol() != null ? usuario.getRol().getNombre() : "Empleado",
                usuario.getEmpresa() != null ? usuario.getEmpresa().getIdEmpresa() : null,
                usuario.getEmpresa() != null ? usuario.getEmpresa().getNombre() : null
        );

        return ResponseEntity.ok()
                .header("Set-Cookie", accessTokenCookie(token).toString())
                .body(Map.of(
                "success", true,
                "message", "Login exitoso",
                "data", response
        ));
    }

    private ResponseCookie accessTokenCookie(String token) {
        return ResponseCookie.from("xincronix_token", token)
                .httpOnly(true)
                .secure(false)
                .sameSite("Lax")
                .path("/")
                .maxAge(Duration.ofDays(1))
                .build();
    }

    @GetMapping("/me")
        public ResponseEntity<?> me(@AuthenticationPrincipal UserDetails userDetails) {
                if (userDetails == null) {
                        return ResponseEntity.status(401).body(Map.of("success", false, "message", "No autenticado"));
                }

                Usuario usuario = usuarioRepository.findByEmail(userDetails.getUsername()).orElseThrow();

        return ResponseEntity.ok(Map.of(
                "success", true,
                "data", Map.of(
                        "id", usuario.getIdUsuario(),
                        "nombres", usuario.getNombres(),
                        "apellidos", usuario.getApellidos(),
                        "email", usuario.getEmail(),
                        "rol", usuario.getRol() != null ? usuario.getRol().getNombre() : "Empleado",
                        "empresaId", usuario.getEmpresa() != null ? usuario.getEmpresa().getIdEmpresa() : null,
                        "empresaNombre", usuario.getEmpresa() != null ? usuario.getEmpresa().getNombre() : null
                )
        ));
    }

        @PostMapping("/logout")
        public ResponseEntity<?> logout() {
                ResponseCookie expiredCookie = ResponseCookie.from("xincronix_token", "")
                                .httpOnly(true)
                                .secure(false)
                                .sameSite("Lax")
                                .path("/")
                                .maxAge(Duration.ZERO)
                                .build();
                return ResponseEntity.ok()
                                .header("Set-Cookie", expiredCookie.toString())
                                .body(Map.of("success", true, "message", "Sesión cerrada"));
        }
}
