package com.Xincronix.service;

import com.Xincronix.model.Actividad;
import com.Xincronix.model.Usuario;
import com.Xincronix.repository.ActividadRepository;
import jakarta.transaction.Transactional;
import org.springframework.dao.DataAccessException;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class ActividadService {
    private final ActividadRepository actividades;

    public ActividadService(ActividadRepository actividades) {
        this.actividades = actividades;
    }

    @Transactional
    public void registrar(Usuario usuario, String modulo, String accion, String detalle) {
        if (usuario == null || usuario.getEmpresa() == null) return;
        Actividad actividad = new Actividad();
        actividad.setUsuario(usuario);
        actividad.setEmpresa(usuario.getEmpresa());
        actividad.setModulo(modulo);
        actividad.setAccion(accion);
        actividad.setDetalle(detalle == null || detalle.isBlank() ? modulo : detalle);
        try {
            actividades.save(actividad);
        } catch (DataAccessException ex) {
            // Permite que una operación principal no falle mientras se aplica la migración histórica.
        }
    }

    public List<Map<String, Object>> recientes(Usuario usuario) {
        try {
            return actividades.findRecientes(usuario.getIdUsuario(),
                            org.springframework.data.domain.PageRequest.of(0, 10))
                .stream().map(actividad -> {
                    Map<String, Object> data = new java.util.HashMap<>();
                    data.put("usuario", nombre(usuario));
                    data.put("descripcion", accion(actividad.getAccion()));
                    data.put("detalle", actividad.getDetalle() == null ? "" : actividad.getDetalle());
                    data.put("tiempo_relativo", relativo(actividad.getFechaCreacion()));
                    return data;
                })
                .toList();
        } catch (DataAccessException ex) {
            return List.of();
        }
    }

    private String nombre(Usuario usuario) {
        return ((usuario.getNombres() == null ? "" : usuario.getNombres()) + " "
                + (usuario.getApellidos() == null ? "" : usuario.getApellidos())).trim();
    }

    private String accion(String accion) {
        return switch (accion) {
            case "CREAR" -> "creó";
            case "ACTUALIZAR" -> "actualizó";
            case "ELIMINAR" -> "eliminó";
            case "AGREGAR" -> "agregó";
            case "QUITAR" -> "quitó";
            default -> accion.toLowerCase();
        };
    }

    private String relativo(LocalDateTime fecha) {
        long minutos = Duration.between(fecha, LocalDateTime.now()).toMinutes();
        if (minutos < 1) return "Ahora";
        if (minutos < 60) return "Hace " + minutos + " min";
        long horas = minutos / 60;
        if (horas < 24) return "Hace " + horas + " h";
        return "Hace " + (horas / 24) + " d";
    }
}
