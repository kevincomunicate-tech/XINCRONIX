package com.Xincronix.service;

import com.Xincronix.model.LoginVerificationCode;
import com.Xincronix.model.Usuario;
import com.Xincronix.repository.LoginVerificationCodeRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.time.LocalDateTime;

@Service
public class EmailLoginVerificationService {
    private final LoginVerificationCodeRepository codes;
    private final JavaMailSender mailSender;
    @Value("${xincronix.mail.from}") private String from;
    public EmailLoginVerificationService(LoginVerificationCodeRepository codes, JavaMailSender mailSender) { this.codes = codes; this.mailSender = mailSender; }
    @Transactional
    public void sendCode(Usuario user) {
        String code = String.format("%06d", new SecureRandom().nextInt(1_000_000));
        LoginVerificationCode record = codes.findByUsuarioIdUsuario(user.getIdUsuario()).orElseGet(LoginVerificationCode::new);
        record.setUsuario(user); record.setCodeHash(hash(code)); record.setExpiresAt(LocalDateTime.now().plusMinutes(5)); record.setUsedAt(null); codes.save(record);
        SimpleMailMessage message = new SimpleMailMessage(); message.setFrom(from); message.setTo(user.getEmail()); message.setSubject("Código de verificación - Xincronix");
        message.setText("Hola " + user.getNombres() + ",\n\nTu código para iniciar sesión es: " + code + "\n\nEs válido durante 5 minutos y solo puede usarse una vez. Si no intentaste iniciar sesión, ignora este correo.\n\nEquipo Xincronix");
        mailSender.send(message);
    }
    @Transactional
    public boolean verify(Usuario user, String code) {
        return codes.findByUsuarioIdUsuario(user.getIdUsuario()).filter(record -> record.getUsedAt() == null && record.getExpiresAt().isAfter(LocalDateTime.now()) && record.getCodeHash().equals(hash(code))).map(record -> { record.setUsedAt(LocalDateTime.now()); codes.save(record); return true; }).orElse(false);
    }
    private String hash(String value) { try { return java.util.HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8))); } catch (Exception exception) { throw new IllegalStateException(exception); } }
}
