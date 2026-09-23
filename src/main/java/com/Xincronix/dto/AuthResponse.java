package com.Xincronix.dto;

public record AuthResponse(
        String accessToken,
        String tokenType,
        Integer userId,
        String nombreCompleto,
        String email,
        String rol,
        String cargo,
        Integer empresaId,
        String empresaNombre
) {}
