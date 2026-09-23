package com.Xincronix.service;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import com.Xincronix.dto.UsuarioRequest;
import com.Xincronix.model.Empresa;
import com.Xincronix.model.PerfilEspecifico;
import com.Xincronix.model.Rol;
import com.Xincronix.model.Usuario;
import com.Xincronix.repository.EmpresaRepository;
import com.Xincronix.repository.PerfilEspecificoRepository;
import com.Xincronix.repository.RolRepository;
import com.Xincronix.repository.UsuarioRepository;

@Service
public class UsuarioService {

    private final UsuarioRepository usuarios;
    private final EmpresaRepository empresas;
    private final RolRepository roles;
    private final PerfilEspecificoRepository perfiles;
    private final PasswordEncoder passwordEncoder;

    public UsuarioService(UsuarioRepository usuarios, EmpresaRepository empresas,
            RolRepository roles, PerfilEspecificoRepository perfiles, PasswordEncoder passwordEncoder) {
        this.usuarios = usuarios;
        this.empresas = empresas;
        this.roles = roles;
        this.perfiles = perfiles;
        this.passwordEncoder = passwordEncoder;
    }

    public List<Usuario> listar(Usuario actor) {
        return esAdministrador(actor)
                ? usuarios.findAllByOrderByNombresAscApellidosAsc()
                : usuarios.findByEmpresaIdEmpresaOrderByNombresAscApellidosAsc(actor.getIdEmpresa());
    }

    public Usuario crear(Usuario actor, UsuarioRequest request) {
        exigirAdministrador(actor);
        if (request.password() == null || request.password().isBlank()) {
            throw new ResponseStatusException(HttpStatus.UNPROCESSABLE_ENTITY, "La contraseña es obligatoria");
        }
        if (usuarios.existsByEmail(request.email())) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "El email ya está registrado");
        }
        Usuario usuario = new Usuario();
        copiar(usuario, request);
        copiarPrivilegios(usuario, request);
        usuario.setPassword(passwordEncoder.encode(request.password()));
        if (usuario.getEmpresa() == null) usuario.setEmpresa(actor.getEmpresa());
        return usuarios.save(usuario);
    }

    public Usuario obtener(Usuario actor, Integer id) {
        Usuario usuario = usuarios.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Usuario no encontrado"));
        exigirMismoAlcance(actor, usuario);
        return usuario;
    }

    public Usuario actualizar(Usuario actor, Integer id, UsuarioRequest request) {
        Usuario usuario = obtener(actor, id);
        if (request.email() != null && !request.email().equals(usuario.getEmail()) && usuarios.existsByEmail(request.email())) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "El email ya está registrado");
        }
        copiar(usuario, request);
        if (request.password() != null && !request.password().isBlank()) {
            usuario.setPassword(passwordEncoder.encode(request.password()));
        }
        if (esAdministrador(actor)) copiarPrivilegios(usuario, request);
        return usuarios.save(usuario);
    }

    public void eliminar(Usuario actor, Integer id) {
        exigirAdministrador(actor);
        if (actor.getIdUsuario().equals(id)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "No puedes eliminar tu propio usuario");
        }
        if (!usuarios.existsById(id)) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Usuario no encontrado");
        }
        usuarios.deleteById(id);
    }

    private void copiar(Usuario usuario, UsuarioRequest request) {
        usuario.setNombres(request.nombres());
        usuario.setApellidos(request.apellidos());
        usuario.setEmail(request.email());
        usuario.setCargo(request.cargo());
        usuario.setTelefono(request.telefono());
        usuario.setAvatar(request.avatar());
        if (request.estado() != null) usuario.setEstado(request.estado());
    }

    private void copiarPrivilegios(Usuario usuario, UsuarioRequest request) {
        if (request.idEmpresa() != null) usuario.setEmpresa(referenciaEmpresa(request.idEmpresa()));
        if (request.idRoles() != null) usuario.setRol(referenciaRol(request.idRoles()));
        if (request.idPerfil() != null) usuario.setPerfil(referenciaPerfil(request.idPerfil()));
    }

    private Empresa referenciaEmpresa(Integer id) {
        return empresas.findById(id).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Empresa no encontrada"));
    }

    private Rol referenciaRol(Integer id) {
        return roles.findById(id).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Rol no encontrado"));
    }

    private PerfilEspecifico referenciaPerfil(Integer id) {
        return perfiles.findById(id).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Perfil no encontrado"));
    }

    private boolean esAdministrador(Usuario actor) {
        if (actor == null || actor.getRol() == null || actor.getRol().getNombre() == null) return false;
        String role = actor.getRol().getNombre().trim().toUpperCase().replace(' ', '_');
        return role.equals("ADMIN") || role.equals("ADMINISTRADOR")
                || role.equals("SUPERADMIN") || role.equals("SUPER_ADMIN");
    }

    private void exigirAdministrador(Usuario actor) {
        if (!esAdministrador(actor)) throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Permiso insuficiente");
    }

    private void exigirMismoAlcance(Usuario actor, Usuario objetivo) {
        if (!esAdministrador(actor) && (actor == null || actor.getIdEmpresa() == null
                || !actor.getIdEmpresa().equals(objetivo.getIdEmpresa()))) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "No tienes permiso para acceder al usuario");
        }
    }
}
