package com.Xincronix.repository;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import com.Xincronix.model.IaMensaje;
public interface IaMensajeRepository extends JpaRepository<IaMensaje, Integer> {
    List<IaMensaje> findByConversacionIdConversacionOrderByFechaEnvioAsc(Integer idConversacion);
}
