package com.Xincronix.model;

import java.time.LocalDateTime;
import jakarta.persistence.*;

@Entity @Table(name = "solicitudes_pago")
public class SolicitudPago {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) @Column(name = "id_solicitud") private Integer idSolicitud;
    @ManyToOne(fetch = FetchType.LAZY, optional = false) @JoinColumn(name = "id_empresa", nullable = false) private Empresa empresa;
    @Column(length = 50) private String plan;
    @Column(name = "metodo_pago", length = 50) private String metodoPago;
    @Column(length = 100) private String referencia;
    @Column(columnDefinition = "TEXT") private String notas;
    @Column(name = "ruta_comprobante", length = 300) private String rutaComprobante;
    @Column(nullable = false, length = 30) private String estado;
    @Column(name = "fecha_creacion", nullable = false) private LocalDateTime fechaCreacion;
    @Column(name = "fecha_revision") private LocalDateTime fechaRevision;
    public Integer getIdSolicitud() { return idSolicitud; }
    public Empresa getEmpresa() { return empresa; }
    public String getPlan() { return plan; }
    public String getMetodoPago() { return metodoPago; }
    public String getReferencia() { return referencia; }
    public String getNotas() { return notas; }
    public String getRutaComprobante() { return rutaComprobante; }
    public String getEstado() { return estado; }
    public LocalDateTime getFechaCreacion() { return fechaCreacion; }
    public void setEmpresa(Empresa empresa) { this.empresa = empresa; }
    public void setPlan(String plan) { this.plan = plan; }
    public void setMetodoPago(String metodoPago) { this.metodoPago = metodoPago; }
    public void setReferencia(String referencia) { this.referencia = referencia; }
    public void setNotas(String notas) { this.notas = notas; }
    public void setRutaComprobante(String rutaComprobante) { this.rutaComprobante = rutaComprobante; }
    public void setEstado(String estado) { this.estado = estado; }
    public void setFechaCreacion(LocalDateTime fechaCreacion) { this.fechaCreacion = fechaCreacion; }

    @PrePersist
    void onCreate() { if (fechaCreacion == null) fechaCreacion = LocalDateTime.now(); }
}
