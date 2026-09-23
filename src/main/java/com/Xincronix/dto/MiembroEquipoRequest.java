package com.Xincronix.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

/** Request for adding one existing user to an existing team. */
public record MiembroEquipoRequest(
        @NotNull Integer idUsuario,
        @Size(max = 80) String rolEnEquipo) {
}
