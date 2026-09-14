package com.Xincronix.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.server.ResponseStatusException;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.Set;
import java.util.UUID;

@Service
public class ComprobanteStorageService {
    private static final long MAX_SIZE = 10 * 1024 * 1024;
    private static final Set<String> TYPES = Set.of("application/pdf", "image/png", "image/jpeg");
    private final Path directory;

    public ComprobanteStorageService(@Value("${xincronix.uploads.directory:uploads/comprobantes}") String directory) {
        this.directory = Path.of(directory).toAbsolutePath().normalize();
    }

    public String store(MultipartFile file) {
        if (file == null || file.isEmpty()) throw new ResponseStatusException(HttpStatus.UNPROCESSABLE_ENTITY, "El comprobante es obligatorio");
        if (file.getSize() > MAX_SIZE) throw new ResponseStatusException(HttpStatus.PAYLOAD_TOO_LARGE, "El comprobante supera los 10 MB");
        if (!TYPES.contains(file.getContentType())) throw new ResponseStatusException(HttpStatus.UNSUPPORTED_MEDIA_TYPE, "El comprobante debe ser PDF, PNG o JPG");
        String extension = switch (file.getContentType()) { case "application/pdf" -> ".pdf"; case "image/png" -> ".png"; default -> ".jpg"; };
        try {
            Files.createDirectories(directory);
            Path target = directory.resolve(UUID.randomUUID() + extension);
            Files.copy(file.getInputStream(), target, StandardCopyOption.REPLACE_EXISTING);
            return target.toString();
        } catch (IOException ex) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "No fue posible guardar el comprobante", ex);
        }
    }
}
