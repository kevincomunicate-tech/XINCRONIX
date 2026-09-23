package com.Xincronix.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.time.LocalDateTime;
import java.util.List;

public record EquipoRequest(@NotBlank @Size(max = 150) String nombre, String descripcion,
                            @NotNull Integer miembros, LocalDateTime fechaInicio, LocalDateTime fechaFin,
                            List<Integer> miembrosIds) {}
