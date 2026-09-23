package com.Xincronix.repository;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import com.Xincronix.model.Proyecto;
public interface ProyectoRepository extends JpaRepository<Proyecto, Integer> {
    List<Proyecto> findByEmpresaIdEmpresa(Integer idEmpresa);
    boolean existsByEmpresaIdEmpresa(Integer idEmpresa);
}
