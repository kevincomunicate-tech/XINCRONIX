package com.Xincronix.controller;

import com.Xincronix.dto.AuthResponse;
import com.Xincronix.dto.LoginRequest;
import com.Xincronix.dto.RegistroEmpresaRequest;
import com.Xincronix.model.Usuario;
import com.Xincronix.repository.UsuarioRepository;
import com.Xincronix.security.JwtService;
import com.Xincronix.security.AuthCookieService;
import com.Xincronix.service.RegistroEmpresaService;
import com.Xincronix.service.PasswordResetService;
import com.Xincronix.service.TotpService;
import com.Xincronix.dto.TwoFactorCodeRequest;
import com.Xincronix.dto.ForgotPasswordRequest;
import com.Xincronix.dto.ResetPasswordRequest;
import com.Xincronix.dto.EmailVerificationRequest;
import com.Xincronix.service.EmailLoginVerificationService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import jakarta.servlet.http.HttpServletResponse;

import java.time.Duration;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthenticationManager authenticationManager;
    private final UserDetailsService userDetailsService;
    private final JwtService jwtService;
    private final UsuarioRepository usuarioRepository;
    private final RegistroEmpresaService registroEmpresaService;
    private final TotpService totpService;
    private final PasswordResetService passwordResetService;
    private final EmailLoginVerificationService emailLoginVerificationService;
    private final AuthCookieService authCookieService;

    public AuthController(AuthenticationManager authenticationManager,
                          UserDetailsService userDetailsService,
                          JwtService jwtService,
                          UsuarioRepository usuarioRepository,
                          RegistroEmpresaService registroEmpresaService, TotpService totpService,
                          PasswordResetService passwordResetService, EmailLoginVerificationService emailLoginVerificationService,
                          AuthCookieService authCookieService) {
        this.authenticationManager = authenticationManager;
        this.userDetailsService = userDetailsService;
        this.jwtService = jwtService;
        this.usuarioRepository = usuarioRepository;
        this.registroEmpresaService = registroEmpresaService;
        this.totpService = totpService;
        this.passwordResetService = passwordResetService;
        this.emailLoginVerificationService = emailLoginVerificationService;
        this.authCookieService = authCookieService;
    }

    @PostMapping(value = {"/register", "/registro"}, consumes = "multipart/form-data")
    public ResponseEntity<?> register(@Valid @ModelAttribute RegistroEmpresaRequest request,
                                      @RequestParam("comprobante") MultipartFile comprobante,
                                      HttpServletResponse httpResponse) {
        Usuario usuario = registroEmpresaService.registrar(request, comprobante);
        UserDetails userDetails = userDetailsService.loadUserByUsername(usuario.getEmail());
        String token = jwtService.generateToken(userDetails);
        AuthResponse response = new AuthResponse(token, "Bearer", usuario.getIdUsuario(),
                usuario.getNombres() + " " + usuario.getApellidos(), usuario.getEmail(),
                usuario.getRol().getNombre(), usuario.getEmpresa().getIdEmpresa(), usuario.getEmpresa().getNombre());
        authCookieService.write(httpResponse, token, false);
        return ResponseEntity.status(201).body(Map.of("success", true,
                "message", "Empresa y administrador registrados correctamente", "data", response));
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@Valid @RequestBody LoginRequest request, HttpServletResponse httpResponse) {
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.email(), request.password())
        );

        Usuario usuario = usuarioRepository.findByEmail(request.email()).orElseThrow();
        return authenticatedResponse(usuario, httpResponse);
    }

    @PostMapping("/two-factor/verify-login")
    public ResponseEntity<?> verifyLoginTwoFactor(@Valid @RequestBody TwoFactorCodeRequest request,
                                                  HttpServletResponse httpResponse) {
        String email;
        try { email = jwtService.extractUsername(request.challenge()); }
        catch (Exception ex) { return ResponseEntity.status(401).body(Map.of("success", false, "message", "El desafío venció o no es válido")); }
        if (!jwtService.hasClaim(request.challenge(), "purpose", "mfa")) return ResponseEntity.status(401).body(Map.of("success", false, "message", "Desafío inválido"));
        Usuario usuario = usuarioRepository.findByEmail(email).orElseThrow();
        if (!Boolean.TRUE.equals(usuario.getTwoFactorEnabled()) || !totpService.valid(usuario.getTwoFactorSecret(), request.code())) return ResponseEntity.status(401).body(Map.of("success", false, "message", "Código inválido"));
        return authenticatedResponse(usuario, httpResponse);
    }

    @PostMapping("/email-verification/verify")
    public ResponseEntity<?> verifyEmailLogin(@Valid @RequestBody EmailVerificationRequest request,
                                              HttpServletResponse httpResponse) {
        String email;
        try { email = jwtService.extractUsername(request.challenge()); }
        catch (Exception ex) { return ResponseEntity.status(401).body(Map.of("success", false, "message", "El código venció; inicia sesión otra vez")); }
        if (!jwtService.hasClaim(request.challenge(), "purpose", "email-login")) return ResponseEntity.status(401).body(Map.of("success", false, "message", "Desafío inválido"));
        Usuario usuario = usuarioRepository.findByEmail(email).orElseThrow();
        if (!emailLoginVerificationService.verify(usuario, request.code())) return ResponseEntity.status(401).body(Map.of("success", false, "message", "Código inválido o vencido"));
        return authenticatedResponse(usuario, httpResponse);
    }

    @PostMapping("/two-factor/setup")
    public ResponseEntity<?> setupTwoFactor(@AuthenticationPrincipal UserDetails principal) {
        Usuario usuario = currentUser(principal); String secret = totpService.newSecret(); usuario.setTwoFactorSecret(secret); usuario.setTwoFactorEnabled(false); usuarioRepository.save(usuario);
        return ResponseEntity.ok(Map.of("success", true, "secret", secret, "otpauthUri", totpService.uri(usuario.getEmail(), secret), "message", "Escanea el código en Google Authenticator y confirma con un código"));
    }

    @PostMapping("/two-factor/confirm")
    public ResponseEntity<?> confirmTwoFactor(@AuthenticationPrincipal UserDetails principal, @RequestBody Map<String, String> body) {
        Usuario usuario = currentUser(principal); String code = body.get("code");
        if (code == null || !code.matches("\\d{6}") || !totpService.valid(usuario.getTwoFactorSecret(), code)) return ResponseEntity.badRequest().body(Map.of("success", false, "message", "Código inválido"));
        usuario.setTwoFactorEnabled(true); usuarioRepository.save(usuario); return ResponseEntity.ok(Map.of("success", true, "message", "Segundo factor activado"));
    }

    @PostMapping("/password/forgot")
    public ResponseEntity<?> forgotPassword(@Valid @RequestBody ForgotPasswordRequest request) {
        passwordResetService.request(request.email());
        return ResponseEntity.ok(Map.of("success", true, "message", "Si existe una cuenta, enviamos un enlace para restablecer la contraseña"));
    }

    @PostMapping("/password/reset")
    public ResponseEntity<?> resetPassword(@Valid @RequestBody ResetPasswordRequest request) {
        passwordResetService.reset(request.token(), request.password());
        return ResponseEntity.ok(Map.of("success", true, "message", "Contraseña actualizada. Ya puedes iniciar sesión"));
    }

    private Usuario currentUser(UserDetails principal) { if (principal == null) throw new org.springframework.security.access.AccessDeniedException("No autenticado"); return usuarioRepository.findByEmail(principal.getUsername()).orElseThrow(); }
    private ResponseEntity<?> authenticatedResponse(Usuario usuario, HttpServletResponse httpResponse) {
        UserDetails details = userDetailsService.loadUserByUsername(usuario.getEmail()); String token = jwtService.generateToken(details);
        AuthResponse response = new AuthResponse(token, "Bearer", usuario.getIdUsuario(), usuario.getNombres() + " " + usuario.getApellidos(), usuario.getEmail(), usuario.getRol() == null ? "Empleado" : usuario.getRol().getNombre(), usuario.getEmpresa() == null ? null : usuario.getEmpresa().getIdEmpresa(), usuario.getEmpresa() == null ? null : usuario.getEmpresa().getNombre());
        authCookieService.write(httpResponse, token, false);
        return ResponseEntity.ok().body(Map.of("success", true, "message", "Login exitoso", "data", response));
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
        public ResponseEntity<?> logout(HttpServletResponse httpResponse) {
            authCookieService.clear(httpResponse);
                return ResponseEntity.ok()
                                .body(Map.of("success", true, "message", "Sesión cerrada"));
        }
}
