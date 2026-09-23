package com.Xincronix;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

import com.Xincronix.service.AuthService;

class AuthServiceTest {

    @Test
    void allAuthenticatedFlowsUseTheMainPanel() {
        assertEquals("/panel", AuthService.redirectByRole("ADMINISTRADOR"));
        assertEquals("/panel", AuthService.redirectByRole("SUPERVISOR"));
        assertEquals("/panel", AuthService.redirectByRole("Empleado"));
    }
}