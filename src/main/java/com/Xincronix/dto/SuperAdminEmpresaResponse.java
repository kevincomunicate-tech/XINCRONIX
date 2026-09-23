package com.Xincronix.dto;

import com.Xincronix.model.Empresa;
import java.time.LocalDateTime;

/** Company projection exported by the SUPERADMIN-only API. */
public record SuperAdminEmpresaResponse(
        Integer idEmpresa,
        String nombre,
        String nit,
        String email,
        String telefono,
        String direccion,
        String industria,
        String planSuscripcion,
        String sector,
        String administrador,
        String numEmpleados,
        LocalDateTime fechaCreacion,
        LocalDateTime fechaActualizacion) {

    public static SuperAdminEmpresaResponse from(Empresa empresa) {
        return new SuperAdminEmpresaResponse(empresa.getIdEmpresa(), empresa.getNombre(), empresa.getNit(),
                empresa.getEmail(), empresa.getTelefono(), empresa.getDireccion(), empresa.getIndustria(),
                empresa.getPlanSuscripcion(), empresa.getSector(), empresa.getAdministrador(), empresa.getNumEmpleados(),
                empresa.getFechaCreacion(), empresa.getFechaActualizacion());
    }
}
