package com.Xincronix.security;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import com.Xincronix.model.Usuario;
import com.Xincronix.repository.UsuarioRepository;
import com.Xincronix.service.AuthService;

import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@Component
public class GoogleOAuthSuccessHandler implements AuthenticationSuccessHandler {

    private final UsuarioRepository usuarioRepository;
    private final CustomUserDetailsService userDetailsService;
    private final JwtService jwtService;
    private final AuthCookieService authCookieService;

    public GoogleOAuthSuccessHandler(UsuarioRepository usuarioRepository,
                                     CustomUserDetailsService userDetailsService,
                                     JwtService jwtService,
                                     AuthCookieService authCookieService) {
        this.usuarioRepository = usuarioRepository;
        this.userDetailsService = userDetailsService;
        this.jwtService = jwtService;
        this.authCookieService = authCookieService;
    }

    @Override
    @Transactional(readOnly = true)
    public void onAuthenticationSuccess(HttpServletRequest request,
                                        HttpServletResponse response,
                                        Authentication authentication)
            throws IOException, ServletException {

        OAuth2User oauthUser = (OAuth2User) authentication.getPrincipal();
        String email = oauthUser.getAttribute("email");

        if (email == null || email.isBlank()) {
            response.sendRedirect("/login?error=google_no_email");
            return;
        }

        String normalizedEmail = email.trim().toLowerCase(java.util.Locale.ROOT);
        Usuario usuario = usuarioRepository.findByEmailIgnoreCase(normalizedEmail).orElse(null);
        if (usuario == null) {
            response.sendRedirect("/login?error=google_user_not_found");
            return;
        }

        String rolNombre = "Empleado";
        if (usuario.getRol() != null) {
            rolNombre = usuario.getRol().getNombre();
        }

        UserDetails userDetails = userDetailsService.loadUserByUsername(usuario.getEmail());

        Map<String, Object> claims = new HashMap<>();
        claims.put("uid", usuario.getIdUsuario());
        claims.put("rol", rolNombre);
        if (usuario.getEmpresa() != null) {
            claims.put("empresaId", usuario.getEmpresa().getIdEmpresa());
        }

        String token = jwtService.generateToken(claims, userDetails);
        authCookieService.write(response, token, false);

        String redirect = AuthService.redirectByRole(rolNombre);
        response.sendRedirect(response.encodeRedirectURL(redirect));
    }
}
