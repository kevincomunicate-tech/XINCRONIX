package com.Xincronix.controller;

import com.Xincronix.model.Usuario;
import com.Xincronix.repository.UsuarioRepository;
import com.Xincronix.security.AuthCookieService;
import com.Xincronix.security.CustomUserDetailsService;
import com.Xincronix.security.GoogleIdTokenService;
import com.Xincronix.security.GoogleOAuthSuccessHandler;
import com.Xincronix.security.JwtService;
import com.Xincronix.service.AuthService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.util.UriUtils;

/** Google Identity Services sign-in endpoint. It validates an ID token server-side. */
@RestController
@RequestMapping("/api/auth/google")
public class GoogleSignInController {
    private final GoogleIdTokenService googleTokens;
    private final UsuarioRepository users;
    private final CustomUserDetailsService userDetailsService;
    private final JwtService jwtService;
    private final AuthCookieService cookies;

    public GoogleSignInController(GoogleIdTokenService googleTokens, UsuarioRepository users,
                                  CustomUserDetailsService userDetailsService, JwtService jwtService,
                                  AuthCookieService cookies) {
        this.googleTokens = googleTokens;
        this.users = users;
        this.userDetailsService = userDetailsService;
        this.jwtService = jwtService;
        this.cookies = cookies;
    }

    @GetMapping("/config")
    public Map<String, Object> config() {
        String clientId = googleTokens.clientId();
        return Map.of("success", true, "data", Map.of("enabled", !clientId.isBlank(), "clientId", clientId));
    }

    @PostMapping
    public ResponseEntity<Map<String, Object>> signIn(@Valid @RequestBody GoogleCredentialRequest request,
                                                       HttpServletRequest httpRequest,
                                                       HttpServletResponse httpResponse) {
        try {
            String email = googleTokens.verify(request.credential()).email();
            Usuario user = users.findByEmailIgnoreCase(email).orElse(null);
            if (user == null) {
                httpRequest.getSession(true).setAttribute(GoogleOAuthSuccessHandler.REGISTRATION_EMAIL_SESSION_KEY, email);
                String url = "/registro?google=1&email=" + UriUtils.encodeQueryParam(email, StandardCharsets.UTF_8);
                return ResponseEntity.ok(Map.of("success", true, "registrationRequired", true, "registrationUrl", url));
            }
            UserDetails details = userDetailsService.loadUserByUsername(user.getEmail());
            String role = user.getRol() == null ? "Empleado" : user.getRol().getNombre();
            Map<String, Object> claims = new HashMap<>();
            claims.put("uid", user.getIdUsuario());
            claims.put("rol", role);
            if (user.getEmpresa() != null) claims.put("empresaId", user.getEmpresa().getIdEmpresa());
            cookies.write(httpResponse, jwtService.generateToken(claims, details), false);
            return ResponseEntity.ok(Map.of("success", true, "message", "Inicio de sesión con Google completado.",
                    "data", Map.of("userId", user.getIdUsuario(), "nombreCompleto", (user.getNombres() + " " + user.getApellidos()).trim(),
                            "email", user.getEmail(), "rol", role, "cargo", user.getCargo() == null ? "" : user.getCargo(),
                            "empresaId", user.getEmpresa() == null ? 0 : user.getEmpresa().getIdEmpresa(),
                            "empresaNombre", user.getEmpresa() == null ? "" : user.getEmpresa().getNombre(),
                            "redirect", AuthService.redirectByRole(role))));
        } catch (GoogleIdTokenService.GoogleTokenException ex) {
            return ResponseEntity.status(401).body(Map.of("success", false, "message", ex.getMessage()));
        }
    }

    public record GoogleCredentialRequest(@NotBlank @Size(max = 10000) String credential) { }
}
