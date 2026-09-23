package com.Xincronix.dto;

import com.Xincronix.model.Equipo;
import java.time.LocalDateTime;

public record EquipoResponse(Integer idEquipo, String nombre, String descripcion, Integer miembros,
                             LocalDateTime fechaInicio, LocalDateTime fechaFin) {
    public static EquipoResponse from(Equipo equipo) {
        return new EquipoResponse(equipo.getIdEquipo(), equipo.getNombre(), equipo.getDescripcion(),
                equipo.getMiembros(), equipo.getFechaInicio(), equipo.getFechaFin());
    }
}
