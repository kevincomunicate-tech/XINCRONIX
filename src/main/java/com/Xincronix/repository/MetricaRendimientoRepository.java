package com.Xincronix.repository;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import com.Xincronix.model.MetricaRendimiento;
public interface MetricaRendimientoRepository extends JpaRepository<MetricaRendimiento, Integer> {
    List<MetricaRendimiento> findByUsuarioIdUsuario(Integer idUsuario);
}
