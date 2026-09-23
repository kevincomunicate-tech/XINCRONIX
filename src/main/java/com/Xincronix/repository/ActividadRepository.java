package com.Xincronix.repository;

import com.Xincronix.model.Actividad;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface ActividadRepository extends JpaRepository<Actividad, Integer> {
    @Query("select a from Actividad a where a.usuario.idUsuario = :idUsuario order by a.fechaCreacion desc")
    List<Actividad> findRecientes(@Param("idUsuario") Integer idUsuario,
                                  org.springframework.data.domain.Pageable pageable);
}
