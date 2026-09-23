package com.Xincronix.service;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;
import java.time.Instant;
import org.springframework.stereotype.Service;

/** RFC 6238 TOTP compatible with Google Authenticator. */
@Service
public class TotpService {
    private static final char[] BASE32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567".toCharArray();
    private final SecureRandom random = new SecureRandom();
    public String newSecret() {
        char[] secret = new char[32];
        for (int i = 0; i < secret.length; i++) secret[i] = BASE32[random.nextInt(BASE32.length)];
        return new String(secret);
    }
    public boolean valid(String secret, String code) {
        long step = Instant.now().getEpochSecond() / 30;
        for (long offset = -1; offset <= 1; offset++) if (code.equals(code(secret, step + offset))) return true;
        return false;
    }
    public String uri(String email, String secret) {
        return "otpauth://totp/Xincronix:" + java.net.URLEncoder.encode(email, java.nio.charset.StandardCharsets.UTF_8)
                + "?secret=" + secret + "&issuer=Xincronix&algorithm=SHA1&digits=6&period=30";
    }
    private String code(String secret, long counter) {
        try {
            byte[] bytes = decodeBase32(secret); byte[] data = java.nio.ByteBuffer.allocate(8).putLong(counter).array();
            Mac mac = Mac.getInstance("HmacSHA1"); mac.init(new SecretKeySpec(bytes, "HmacSHA1")); byte[] hash = mac.doFinal(data);
            int offset = hash[hash.length - 1] & 15;
            int number = ((hash[offset] & 127) << 24) | ((hash[offset + 1] & 255) << 16) | ((hash[offset + 2] & 255) << 8) | (hash[offset + 3] & 255);
            return String.format("%06d", number % 1_000_000);
        } catch (Exception ex) { throw new IllegalStateException("No se pudo validar el segundo factor", ex); }
    }
    private byte[] decodeBase32(String input) {
        int buffer = 0, bits = 0; java.io.ByteArrayOutputStream output = new java.io.ByteArrayOutputStream();
        for (char c : input.replace("=", "").toUpperCase().toCharArray()) { int value = new String(BASE32).indexOf(c); if (value < 0) throw new IllegalArgumentException("Secreto TOTP inválido"); buffer = (buffer << 5) | value; bits += 5; if (bits >= 8) { output.write((buffer >> (bits - 8)) & 255); bits -= 8; } }
        return output.toByteArray();
    }
}
