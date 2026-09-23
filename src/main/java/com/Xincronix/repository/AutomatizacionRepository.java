package com.Xincronix.repository;

import com.Xincronix.model.Automatizacion;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AutomatizacionRepository extends JpaRepository<Automatizacion, Integer> {
    List<Automatizacion> findByEmpresaIdEmpresaOrderByFechaCreacionDesc(Integer idEmpresa);
    List<Automatizacion> findByCreadorIdUsuarioOrderByFechaCreacionDesc(Integer idUsuario);
    Optional<Automatizacion> findByIdAutomatizacionAndEmpresaIdEmpresa(Integer idAutomatizacion, Integer idEmpresa);
}
