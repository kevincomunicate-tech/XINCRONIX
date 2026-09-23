package com.Xincronix.security;

import java.time.Instant;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.jwt.JwtException;
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder;
import org.springframework.stereotype.Service;

/** Validates Google Identity Services ID tokens without a client secret. */
@Service
public class GoogleIdTokenService {
    private static final String GOOGLE_JWKS = "https://www.googleapis.com/oauth2/v3/certs";
    private final NimbusJwtDecoder decoder = NimbusJwtDecoder.withJwkSetUri(GOOGLE_JWKS).build();

    @Value("${xincronix.google.client-id:}")
    private String clientId;

    public String clientId() {
        return clientId == null ? "" : clientId.trim();
    }

    public GoogleIdentity verify(String idToken) {
        if (clientId().isBlank()) throw new GoogleTokenException("El inicio de sesión con Google no está configurado.");
        try {
            Jwt jwt = decoder.decode(idToken);
            String issuer = jwt.getIssuer() == null ? "" : jwt.getIssuer().toString();
            if (!"https://accounts.google.com".equals(issuer) && !"accounts.google.com".equals(issuer)) {
                throw new GoogleTokenException("El token no fue emitido por Google.");
            }
            if (jwt.getExpiresAt() == null || !jwt.getExpiresAt().isAfter(Instant.now())) {
                throw new GoogleTokenException("El token de Google venció. Inténtalo de nuevo.");
            }
            List<String> audience = jwt.getAudience();
            if (audience == null || !audience.contains(clientId())) {
                throw new GoogleTokenException("El token de Google no corresponde a Xincronix.");
            }
            String email = jwt.getClaimAsString("email");
            Object verified = jwt.getClaim("email_verified");
            boolean emailVerified = Boolean.TRUE.equals(verified) || "true".equalsIgnoreCase(String.valueOf(verified));
            if (email == null || email.isBlank() || !emailVerified) {
                throw new GoogleTokenException("Google no confirmó un correo electrónico válido.");
            }
            return new GoogleIdentity(email.trim().toLowerCase(java.util.Locale.ROOT));
        } catch (JwtException ex) {
            throw new GoogleTokenException("Google no pudo validar tu sesión. Vuelve a intentarlo.");
        }
    }

    public record GoogleIdentity(String email) { }
    public static class GoogleTokenException extends RuntimeException {
        public GoogleTokenException(String message) { super(message); }
    }
}
