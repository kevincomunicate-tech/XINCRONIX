package com.Xincronix.controller;

import com.Xincronix.dto.AuthResponse;
import com.Xincronix.dto.LoginRequest;
import com.Xincronix.dto.RegistroEmpresaRequest;
import com.Xincronix.model.Usuario;
import com.Xincronix.repository.UsuarioRepository;
import com.Xincronix.security.JwtService;
import com.Xincronix.security.AuthCookieService;
import com.Xincronix.security.GoogleOAuthSuccessHandler;
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
import org.springframework.http.HttpStatus;
import org.springframework.mail.MailException;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;

import java.util.Map;
import java.util.LinkedHashMap;
import java.util.Locale;

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
                                      HttpServletResponse httpResponse,
                                      HttpServletRequest httpRequest) {
        HttpSession session = httpRequest.getSession(false);
        Object pendingGoogleEmail = session == null ? null
                : session.getAttribute(GoogleOAuthSuccessHandler.REGISTRATION_EMAIL_SESSION_KEY);
        if (pendingGoogleEmail instanceof String googleEmail
                && !googleEmail.equalsIgnoreCase(request.email().trim())) {
            return ResponseEntity.badRequest().body(Map.of("success", false,
                    "message", "El registro iniciado con Google debe usar el correo verificado por Google."));
        }
        Usuario usuario = registroEmpresaService.registrar(request, comprobante);
        if (session != null) {
            session.removeAttribute(GoogleOAuthSuccessHandler.REGISTRATION_EMAIL_SESSION_KEY);
        }
        UserDetails userDetails = userDetailsService.loadUserByUsername(usuario.getEmail());
        String token = jwtService.generateToken(userDetails);
        AuthResponse response = new AuthResponse(token, "Bearer", usuario.getIdUsuario(),
                usuario.getNombres() + " " + usuario.getApellidos(), usuario.getEmail(),
                usuario.getRol().getNombre(), usuario.getCargo(), usuario.getEmpresa().getIdEmpresa(), usuario.getEmpresa().getNombre());
        authCookieService.write(httpResponse, token, false);
        return ResponseEntity.status(201).body(Map.of("success", true,
                "message", "Empresa y administrador registrados correctamente", "data", response));
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@Valid @RequestBody LoginRequest request, HttpServletResponse httpResponse) {
        String email = request.email().trim().toLowerCase(Locale.ROOT);
        Usuario usuario = usuarioRepository.findByEmailIgnoreCase(email).orElse(null);
        if (usuario == null) {
            return ResponseEntity.status(404).body(Map.of(
                    "success", false,
                    "code", "EMAIL_NOT_REGISTERED",
                    "message", "Este correo no está registrado. Regístrate para continuar."));
        }

        try {
            authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(usuario.getEmail(), request.password())
            );
            return authenticatedResponse(usuario, httpResponse);
        } catch (BadCredentialsException ex) {
            return ResponseEntity.status(401).body(Map.of(
                    "success", false,
                    "code", "INVALID_CREDENTIALS",
                    "message", "La contraseña no es correcta."));
        }
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
        try {
            passwordResetService.request(request.email());
            return ResponseEntity.ok(Map.of("success", true, "message", "Si existe una cuenta, enviamos un enlace para restablecer la contraseña"));
        } catch (MailException ex) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(Map.of(
                    "success", false,
                    "message", "El servicio de correo no está disponible en este momento. Inténtalo más tarde."));
        }
    }

    @PostMapping("/password/reset")
    public ResponseEntity<?> resetPassword(@Valid @RequestBody ResetPasswordRequest request) {
        passwordResetService.reset(request.token(), request.password());
        return ResponseEntity.ok(Map.of("success", true, "message", "Contraseña actualizada. Ya puedes iniciar sesión"));
    }

    private Usuario currentUser(UserDetails principal) {
        if (principal == null) {
            throw new org.springframework.security.access.AccessDeniedException("No autenticado");
        }
        return usuarioRepository.findByEmailIgnoreCase(principal.getUsername()).orElseThrow();
    }
    private ResponseEntity<?> authenticatedResponse(Usuario usuario, HttpServletResponse httpResponse) {
        UserDetails details = userDetailsService.loadUserByUsername(usuario.getEmail()); String token = jwtService.generateToken(details);
        AuthResponse response = new AuthResponse(token, "Bearer", usuario.getIdUsuario(), usuario.getNombres() + " " + usuario.getApellidos(), usuario.getEmail(), usuario.getRol() == null ? "Empleado" : usuario.getRol().getNombre(), usuario.getCargo(), usuario.getEmpresa() == null ? null : usuario.getEmpresa().getIdEmpresa(), usuario.getEmpresa() == null ? null : usuario.getEmpresa().getNombre());
        authCookieService.write(httpResponse, token, false);
        return ResponseEntity.ok().body(Map.of("success", true, "message", "Login exitoso", "data", response));
    }

    @GetMapping("/me")
        public ResponseEntity<?> me(@AuthenticationPrincipal UserDetails userDetails) {
                if (userDetails == null) {
                        return ResponseEntity.status(401).body(Map.of("success", false, "message", "No autenticado"));
                }

                Usuario usuario = usuarioRepository.findByEmail(userDetails.getUsername()).orElseThrow();

    Map<String, Object> data = new LinkedHashMap<>();
    data.put("id", usuario.getIdUsuario());
    data.put("nombres", usuario.getNombres());
    data.put("apellidos", usuario.getApellidos());
    data.put("email", usuario.getEmail());
    data.put("rol", usuario.getRol() != null ? usuario.getRol().getNombre() : "Empleado");
    data.put("cargo", usuario.getCargo());
    data.put("empresaId", usuario.getEmpresa() != null ? usuario.getEmpresa().getIdEmpresa() : null);
    data.put("empresaNombre", usuario.getEmpresa() != null ? usuario.getEmpresa().getNombre() : null);
    return ResponseEntity.ok(Map.of("success", true, "data", data));
    }

        @PostMapping("/logout")
        public ResponseEntity<?> logout(HttpServletResponse httpResponse) {
            authCookieService.clear(httpResponse);
                return ResponseEntity.ok()
                                .body(Map.of("success", true, "message", "Sesión cerrada"));
        }
}
