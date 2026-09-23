package com.Xincronix.dto;

import com.Xincronix.model.MiembroEquipo;
import java.time.LocalDateTime;

/** Safe member projection returned only after the team tenant has been verified. */
public record MiembroEquipoResponse(
        Integer idUsuario,
        String nombres,
        String apellidos,
        String cargo,
        String rolEnEquipo,
        LocalDateTime fechaIngreso) {

    public static MiembroEquipoResponse from(MiembroEquipo miembro) {
        return new MiembroEquipoResponse(
                miembro.getUsuario().getIdUsuario(),
                miembro.getUsuario().getNombres(),
                miembro.getUsuario().getApellidos(),
                miembro.getUsuario().getCargo(),
                miembro.getRolEnEquipo(),
                miembro.getFechaIngreso());
    }
}
