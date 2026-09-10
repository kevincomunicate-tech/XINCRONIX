package com.Xincronix.repository;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import com.Xincronix.model.Reunion;
public interface ReunionRepository extends JpaRepository<Reunion, Integer> {
    List<Reunion> findByUsuarioIdUsuario(Integer idUsuario);
}
