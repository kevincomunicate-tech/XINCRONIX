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
    public void setEmpresa(Empresa empresa) { this.empresa = empresa; }
}
