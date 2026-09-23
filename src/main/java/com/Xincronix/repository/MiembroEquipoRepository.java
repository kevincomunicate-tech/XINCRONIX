package com.Xincronix.repository;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import com.Xincronix.model.MiembroEquipo;
public interface MiembroEquipoRepository extends JpaRepository<MiembroEquipo, Integer> {
    List<MiembroEquipo> findByEquipoIdEquipo(Integer idEquipo);
    Optional<MiembroEquipo> findByEquipoIdEquipoAndUsuarioIdUsuario(Integer idEquipo, Integer idUsuario);
}
