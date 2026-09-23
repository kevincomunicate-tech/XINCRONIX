package com.Xincronix.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record RegistroEmpresaRequest(
        @NotBlank @Size(max = 200) String nombre,
        @NotBlank @Size(max = 30) String nit,
        @NotBlank @Size(max = 100) String sector,
        @NotBlank @Size(max = 30) String numEmpleados,
        @NotBlank @Size(max = 100) String nombres,
        @NotBlank @Size(max = 100) String apellidos,
        @NotBlank @Size(max = 80) String cargo,
        @NotBlank @Email @Size(max = 150) String email,
        @NotBlank @Size(max = 20) String telefono,
        @NotBlank @Size(min = 8, max = 128) String password,
        @NotBlank @Size(max = 50) String plan,
        @NotBlank @Size(max = 50) String metodoPago,
        @NotBlank @Size(max = 100) String referencia,
        @Size(max = 5000) String notas) {
}
