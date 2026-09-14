package com.Xincronix.security;

import com.Xincronix.model.Usuario;
import com.Xincronix.repository.UsuarioRepository;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class CustomUserDetailsService implements UserDetailsService {

    private final UsuarioRepository usuarioRepository;

    public CustomUserDetailsService(UsuarioRepository usuarioRepository) {
        this.usuarioRepository = usuarioRepository;
    }

    @Override
    @Transactional(readOnly = true)
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        Usuario usuario = usuarioRepository.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("Usuario no encontrado: " + email));

        String roleName = usuario.getRol() != null
                ? usuario.getRol().getNombre().toUpperCase().replace(" ", "_")
                : "EMPLEADO";

        roleName = normalizeRole(roleName);

        return User.builder()
                .username(usuario.getEmail())
                .password(usuario.getPassword())
                .authorities(List.of(new SimpleGrantedAuthority("ROLE_" + roleName)))
                .disabled(!Boolean.TRUE.equals(usuario.getEstado()))
                .accountExpired(false)
                .credentialsExpired(false)
                .accountLocked(false)
                .build();
    }

    private String normalizeRole(String role) {
        return switch (role) {
            case "ADMINISTRADOR", "ADMIN" -> "ADMINISTRADOR";
            case "MANAGER", "GERENTE" -> "MANAGER";
            case "SUPERVISOR" -> "SUPERVISOR";
            case "COLABORADOR", "EMPLEADO", "USER" -> "EMPLEADO";
            default -> "EMPLEADO";
        };
    }
}

