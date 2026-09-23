package com.Xincronix.service;

public final class AuthService {
    private AuthService() {
    }

    public static String redirectByRole(String role) {
        return "/panel";
    }
}
