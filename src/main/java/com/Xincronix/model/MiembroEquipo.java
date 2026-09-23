package com.Xincronix.model;

import java.time.LocalDateTime;
import jakarta.persistence.*;

@Entity @Table(name = "miembros_equipo", uniqueConstraints = @UniqueConstraint(name = "uq_miembro", columnNames = {"id_equipo", "id_usuario"}))
public class MiembroEquipo {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) private Integer id;
    @ManyToOne(fetch = FetchType.LAZY, optional = false) @JoinColumn(name = "id_equipo", nullable = false) private Equipo equipo;
    @ManyToOne(fetch = FetchType.LAZY, optional = false) @JoinColumn(name = "id_usuario", nullable = false) private Usuario usuario;
    @Column(name = "rol_en_equipo", length = 80) private String rolEnEquipo;
    @Column(name = "fecha_ingreso", nullable = false) private LocalDateTime fechaIngreso;
    public Integer getId() { return id; }
    public Equipo getEquipo() { return equipo; }
    public void setEquipo(Equipo equipo) { this.equipo = equipo; }
    public Usuario getUsuario() { return usuario; }
    public void setUsuario(Usuario usuario) { this.usuario = usuario; }
    public String getRolEnEquipo() { return rolEnEquipo; }
    public void setRolEnEquipo(String rolEnEquipo) { this.rolEnEquipo = rolEnEquipo; }
    public LocalDateTime getFechaIngreso() { return fechaIngreso; }
    public void setFechaIngreso(LocalDateTime fechaIngreso) { this.fechaIngreso = fechaIngreso; }
}
