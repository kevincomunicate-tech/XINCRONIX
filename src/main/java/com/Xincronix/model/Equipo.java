package com.Xincronix.model;

import java.time.LocalDateTime;
import jakarta.persistence.*;

@Entity @Table(name = "equipos")
public class Equipo {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) @Column(name = "id_equipo") private Integer idEquipo;
    @Column(nullable = false, length = 150) private String nombre;
    @Column(columnDefinition = "TEXT") private String descripcion;
    @Column(nullable = false) private Integer miembros;
    @Column(name = "fecha_inicio") private LocalDateTime fechaInicio;
    @Column(name = "fecha_fin") private LocalDateTime fechaFin;
    @ManyToOne(fetch = FetchType.LAZY, optional = false) @JoinColumn(name = "id_empresa", nullable = false) private Empresa empresa;
    public Integer getIdEquipo() { return idEquipo; }
    public String getNombre() { return nombre; }
    public void setNombre(String nombre) { this.nombre = nombre; }
    public String getDescripcion() { return descripcion; }
    public void setDescripcion(String descripcion) { this.descripcion = descripcion; }
    public Integer getMiembros() { return miembros; }
    public void setMiembros(Integer miembros) { this.miembros = miembros; }
    public LocalDateTime getFechaInicio() { return fechaInicio; }
    public void setFechaInicio(LocalDateTime fechaInicio) { this.fechaInicio = fechaInicio; }
    public LocalDateTime getFechaFin() { return fechaFin; }
    public void setFechaFin(LocalDateTime fechaFin) { this.fechaFin = fechaFin; }
    public Empresa getEmpresa() { return empresa; }
    public void setEmpresa(Empresa empresa) { this.empresa = empresa; }
}
