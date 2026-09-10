package com.Xincronix.repository;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import com.Xincronix.model.SolicitudPago;
public interface SolicitudPagoRepository extends JpaRepository<SolicitudPago, Integer> {
    List<SolicitudPago> findByEmpresaIdEmpresa(Integer idEmpresa);
}
