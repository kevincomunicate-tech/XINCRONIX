package com.Xincronix.service;

public final class AuthService {
    private AuthService() {
    }

    public static String redirectByRole(String role) {
        String normalized = role == null ? "" : role.trim()
                .toUpperCase()
                .replace(' ', '_');
        return switch (normalized) {
            case "ADMIN", "ADMINISTRADOR" -> "/panel/admin";
            case "SUPERVISOR", "MANAGER", "GERENTE" -> "/panel/supervisor";
            default -> "/panel";
        };
    }
}
