package com.Xincronix.repository;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import com.Xincronix.model.Calendario;
public interface CalendarioRepository extends JpaRepository<Calendario, Integer> {
    List<Calendario> findByUsuarioIdUsuario(Integer idUsuario);
}
