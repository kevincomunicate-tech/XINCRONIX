package com.Xincronix.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

import com.Xincronix.model.Rol;

public interface RolRepository extends JpaRepository<Rol, Integer> {
    Optional<Rol> findByNombre(String nombre);
}
