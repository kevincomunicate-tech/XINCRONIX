package com.Xincronix.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

import com.Xincronix.model.Usuario;

public interface UsuarioRepository extends JpaRepository<Usuario, Integer> {
    boolean existsByEmail(String email);
    Optional<com.Xincronix.model.Usuario> findByEmail(String email);
    List<Usuario> findAllByOrderByNombresAscApellidosAsc();
    List<Usuario> findByEmpresaIdEmpresaOrderByNombresAscApellidosAsc(Integer idEmpresa);
}
