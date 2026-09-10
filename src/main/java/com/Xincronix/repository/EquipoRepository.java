package com.Xincronix.repository;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import com.Xincronix.model.Equipo;
public interface EquipoRepository extends JpaRepository<Equipo, Integer> {
    List<Equipo> findByEmpresaIdEmpresa(Integer idEmpresa);
}
