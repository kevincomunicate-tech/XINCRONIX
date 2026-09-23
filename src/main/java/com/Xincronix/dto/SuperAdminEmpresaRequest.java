package com.Xincronix.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/** Input accepted by the global company administration API. */
public record SuperAdminEmpresaRequest(
        @NotBlank @Size(max = 200) String nombre,
        @NotBlank @Size(max = 30) String nit,
        @NotBlank @Email @Size(max = 150) String email,
        @Size(max = 20) String telefono,
        @Size(max = 300) String direccion,
        @Size(max = 100) String industria,
        @Size(max = 50) String planSuscripcion,
        @Size(max = 50) String sector,
        @Size(max = 120) String administrador,
        @Size(max = 30) String numEmpleados) {
}
