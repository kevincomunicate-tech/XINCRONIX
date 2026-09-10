package com.Xincronix.repository;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import com.Xincronix.model.Tarea;
public interface TareaRepository extends JpaRepository<Tarea, Integer> {
    List<Tarea> findByProyectoIdProyecto(Integer idProyecto);
    List<Tarea> findByUsuarioIdUsuario(Integer idUsuario);
}
