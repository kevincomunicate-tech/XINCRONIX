package com.Xincronix.service;

import com.Xincronix.model.PasswordResetToken;
import com.Xincronix.model.Usuario;
import com.Xincronix.repository.PasswordResetTokenRepository;
import com.Xincronix.repository.UsuarioRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.util.Base64;
import java.util.Locale;

@Service
public class PasswordResetService {
    private final UsuarioRepository usuarios; private final PasswordResetTokenRepository tokens;
    private final PasswordEncoder passwordEncoder; private final JavaMailSender mailSender;
    @Value("${xincronix.app.base-url}") private String baseUrl;
    @Value("${xincronix.mail.from}") private String from;
    public PasswordResetService(UsuarioRepository usuarios, PasswordResetTokenRepository tokens, PasswordEncoder passwordEncoder, JavaMailSender mailSender) { this.usuarios = usuarios; this.tokens = tokens; this.passwordEncoder = passwordEncoder; this.mailSender = mailSender; }
    @Transactional
    public void request(String email) {
        String normalizedEmail = email.trim().toLowerCase(Locale.ROOT);
        usuarios.findByEmailIgnoreCase(normalizedEmail).ifPresent(usuario -> {
            tokens.deleteByUsuarioIdUsuario(usuario.getIdUsuario());
            String raw = newToken(); PasswordResetToken token = new PasswordResetToken(); token.setUsuario(usuario); token.setTokenHash(hash(raw)); token.setExpiresAt(LocalDateTime.now().plusMinutes(30)); tokens.save(token);
            SimpleMailMessage message = new SimpleMailMessage(); message.setFrom(from); message.setTo(usuario.getEmail()); message.setSubject("Restablece tu contraseña de Xincronix"); message.setText("Recibimos una solicitud para restablecer tu contraseña. Abre este enlace (válido por 30 minutos):\n" + baseUrl + "/reset-password?token=" + raw + "\n\nSi no la solicitaste, ignora este correo."); mailSender.send(message);
        });
    }
    @Transactional
    public void reset(String rawToken, String newPassword) {
        PasswordResetToken token = tokens.findByTokenHash(hash(rawToken)).orElseThrow(() -> new IllegalArgumentException("El enlace no es válido"));
        if (token.getUsedAt() != null || !token.getExpiresAt().isAfter(LocalDateTime.now())) throw new IllegalArgumentException("El enlace venció o ya fue usado");
        Usuario user = token.getUsuario(); user.setPassword(passwordEncoder.encode(newPassword)); token.setUsedAt(LocalDateTime.now()); usuarios.save(user); tokens.save(token);
    }
    private String newToken() { byte[] bytes = new byte[32]; new SecureRandom().nextBytes(bytes); return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes); }
    private String hash(String value) { try { return java.util.HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8))); } catch (Exception ex) { throw new IllegalStateException(ex); } }
}
