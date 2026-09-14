package com.Xincronix.model;

import java.time.LocalDate;
import java.time.LocalDateTime;
import jakarta.persistence.*;

@Entity @Table(name = "proyecto")
public class Proyecto {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) @Column(name = "id_proyecto") private Integer idProyecto;
    @Column(nullable = false, length = 150) private String nombre;
    @Column(columnDefinition = "TEXT") private String descripcion;
    @Column(nullable = false, length = 50) private String estado;
    @Column(name = "nivel_importancia", nullable = false) private Integer nivelImportancia;
    @Column(name = "tipo_proyecto", length = 50) private String tipoProyecto;
    @Column(name = "fecha_inicio") private LocalDate fechaInicio;
    @Column(name = "fecha_fin") private LocalDate fechaFin;
    @Column(name = "fecha_creacion", nullable = false) private LocalDateTime fechaCreacion;
    @ManyToOne(fetch = FetchType.LAZY, optional = false) @JoinColumn(name = "id_empresa", nullable = false) private Empresa empresa;
    @ManyToOne(fetch = FetchType.LAZY) @JoinColumn(name = "id_equipo") private Equipo equipo;
    public Integer getIdProyecto() { return idProyecto; }
    public String getNombre() { return nombre; }
    public void setNombre(String nombre) { this.nombre = nombre; }
    public String getDescripcion() { return descripcion; }
    public void setDescripcion(String descripcion) { this.descripcion = descripcion; }
    public String getEstado() { return estado; }
    public void setEstado(String estado) { this.estado = estado; }
    public Integer getNivelImportancia() { return nivelImportancia; }
    public void setNivelImportancia(Integer nivelImportancia) { this.nivelImportancia = nivelImportancia; }
    public String getTipoProyecto() { return tipoProyecto; }
    public void setTipoProyecto(String tipoProyecto) { this.tipoProyecto = tipoProyecto; }
    public LocalDate getFechaInicio() { return fechaInicio; }
    public void setFechaInicio(LocalDate fechaInicio) { this.fechaInicio = fechaInicio; }
    public LocalDate getFechaFin() { return fechaFin; }
    public void setFechaFin(LocalDate fechaFin) { this.fechaFin = fechaFin; }
    public LocalDateTime getFechaCreacion() { return fechaCreacion; }
    public void setFechaCreacion(LocalDateTime fechaCreacion) { this.fechaCreacion = fechaCreacion; }
    public Equipo getEquipo() { return equipo; }
    public void setEquipo(Equipo equipo) { this.equipo = equipo; }
    public Empresa getEmpresa() { return empresa; }
    public void setEmpresa(Empresa empresa) { this.empresa = empresa; }

    @PrePersist
    void onCreate() {
        if (fechaCreacion == null) fechaCreacion = LocalDateTime.now();
        if (nivelImportancia == null) nivelImportancia = 1;
        if (estado == null || estado.isBlank()) estado = "Activo";
    }
}
