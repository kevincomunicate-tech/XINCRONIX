package com.Xincronix.repository;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import com.Xincronix.model.IaConversacion;
public interface IaConversacionRepository extends JpaRepository<IaConversacion, Integer> {
    List<IaConversacion> findByUsuarioIdUsuarioOrderByFechaUltimaDesc(Integer idUsuario);
}
