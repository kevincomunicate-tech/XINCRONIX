package com.Xincronix.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import java.time.LocalDateTime;

/** A workflow definition belonging to one company, never to the whole tenant. */
@Entity
@Table(name = "automatizaciones")
public class Automatizacion {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_automatizacion")
    private Integer idAutomatizacion;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "id_empresa", nullable = false)
    private Empresa empresa;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "id_usuario_creador", nullable = false)
    private Usuario creador;

    @Column(nullable = false, length = 150)
    private String nombre;

    @Column(nullable = false, length = 150)
    private String disparador;

    @Column(columnDefinition = "TEXT")
    private String descripcion;

    @Column(nullable = false)
    private Boolean activa;

    @Column(nullable = false)
    private Long ejecuciones;

    @Column(nullable = false)
    private Long exitos;

    @Column(nullable = false)
    private Long errores;

    @Column(name = "ultima_ejecucion")
    private LocalDateTime ultimaEjecucion;

    @Column(name = "fecha_creacion", nullable = false)
    private LocalDateTime fechaCreacion;

    public Integer getIdAutomatizacion() { return idAutomatizacion; }
    public Empresa getEmpresa() { return empresa; }
    public void setEmpresa(Empresa empresa) { this.empresa = empresa; }
    public Usuario getCreador() { return creador; }
    public void setCreador(Usuario creador) { this.creador = creador; }
    public String getNombre() { return nombre; }
    public void setNombre(String nombre) { this.nombre = nombre; }
    public String getDisparador() { return disparador; }
    public void setDisparador(String disparador) { this.disparador = disparador; }
    public String getDescripcion() { return descripcion; }
    public void setDescripcion(String descripcion) { this.descripcion = descripcion; }
    public Boolean getActiva() { return activa; }
    public void setActiva(Boolean activa) { this.activa = activa; }
    public Long getEjecuciones() { return ejecuciones; }
    public void setEjecuciones(Long ejecuciones) { this.ejecuciones = ejecuciones; }
    public Long getExitos() { return exitos; }
    public void setExitos(Long exitos) { this.exitos = exitos; }
    public Long getErrores() { return errores; }
    public void setErrores(Long errores) { this.errores = errores; }
    public LocalDateTime getUltimaEjecucion() { return ultimaEjecucion; }
    public void setUltimaEjecucion(LocalDateTime ultimaEjecucion) { this.ultimaEjecucion = ultimaEjecucion; }
    public LocalDateTime getFechaCreacion() { return fechaCreacion; }

    @PrePersist
    void onCreate() {
        if (activa == null) activa = Boolean.TRUE;
        if (ejecuciones == null) ejecuciones = 0L;
        if (exitos == null) exitos = 0L;
        if (errores == null) errores = 0L;
        if (fechaCreacion == null) fechaCreacion = LocalDateTime.now();
    }
}
