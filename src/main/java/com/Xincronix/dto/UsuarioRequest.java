package com.Xincronix.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record UsuarioRequest(
        @NotBlank String nombres,
        @NotBlank String apellidos,
        @NotBlank @Email String email,
        @Size(min = 8, max = 128) String password,
        String cargo,
        String telefono,
        String avatar,
        Boolean estado,
        Integer idEmpresa,
        Integer idRoles,
        Integer idPerfil) {
}
