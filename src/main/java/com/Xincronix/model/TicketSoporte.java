package com.Xincronix.model;

import java.time.LocalDateTime;
import jakarta.persistence.*;

@Entity @Table(name = "tickets_soporte")
public class TicketSoporte {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) @Column(name = "id_ticket") private Integer idTicket;
    @Column(nullable = false, length = 200) private String asunto;
    @Column(columnDefinition = "TEXT") private String descripcion;
    @Column(nullable = false, length = 20) private String prioridad;
    @Column(nullable = false, length = 30) private String estado;
    @ManyToOne(fetch = FetchType.LAZY) @JoinColumn(name = "id_empresa") private Empresa empresa;
    @Column(name = "fecha_creacion", nullable = false) private LocalDateTime fechaCreacion;
    @Column(name = "fecha_cierre") private LocalDateTime fechaCierre;
    public Integer getIdTicket() { return idTicket; }
    public String getAsunto() { return asunto; }
    public String getDescripcion() { return descripcion; }
    public String getPrioridad() { return prioridad; }
    public String getEstado() { return estado; }
    public Empresa getEmpresa() { return empresa; }
    public void setEmpresa(Empresa empresa) { this.empresa = empresa; }
    public LocalDateTime getFechaCreacion() { return fechaCreacion; }
    public LocalDateTime getFechaCierre() { return fechaCierre; }
    public void setAsunto(String asunto) { this.asunto = asunto; }
    public void setDescripcion(String descripcion) { this.descripcion = descripcion; }
    public void setPrioridad(String prioridad) { this.prioridad = prioridad; }
    public void setEstado(String estado) { this.estado = estado; }
    public void setFechaCreacion(LocalDateTime fechaCreacion) { this.fechaCreacion = fechaCreacion; }
    public void setFechaCierre(LocalDateTime fechaCierre) { this.fechaCierre = fechaCierre; }

    @PrePersist
    void onCreate() { if (fechaCreacion == null) fechaCreacion = LocalDateTime.now(); }
}
