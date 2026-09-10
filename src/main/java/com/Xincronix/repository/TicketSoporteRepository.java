package com.Xincronix.repository;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import com.Xincronix.model.TicketSoporte;
public interface TicketSoporteRepository extends JpaRepository<TicketSoporte, Integer> {
    List<TicketSoporte> findByEmpresaIdEmpresa(Integer idEmpresa);
}
