package com.Xincronix.repository;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import com.Xincronix.model.Mensaje;
public interface MensajeRepository extends JpaRepository<Mensaje, Integer> {
    List<Mensaje> findByRemitenteIdUsuarioOrDestinatarioIdUsuarioOrderByFechaEnvioAsc(Integer remitente, Integer destinatario);
}
