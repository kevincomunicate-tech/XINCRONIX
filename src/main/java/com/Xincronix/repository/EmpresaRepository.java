package com.Xincronix.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.Xincronix.model.Empresa;

public interface EmpresaRepository extends JpaRepository<Empresa, Integer> {
    boolean existsByNit(String nit);
    boolean existsByEmail(String email);
}
