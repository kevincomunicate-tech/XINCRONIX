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
}
