package com.Xincronix.dto;

import com.Xincronix.model.Usuario;

public record UsuarioResponse(
        Integer idUsuario,
        String nombres,
        String apellidos,
        String email,
        String cargo,
        String telefono,
        String avatar,
        Boolean estado,
        Integer idEmpresa,
        Integer idRoles,
        Integer idPerfil) {

    public static UsuarioResponse from(Usuario usuario) {
        return new UsuarioResponse(usuario.getIdUsuario(), usuario.getNombres(), usuario.getApellidos(),
                usuario.getEmail(), usuario.getCargo(), usuario.getTelefono(), usuario.getAvatar(),
                usuario.getEstado(), usuario.getIdEmpresa(), usuario.getIdRoles(), usuario.getIdPerfil());
    }
}
