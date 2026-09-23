package com.Xincronix.model;

import java.time.LocalDateTime;
import jakarta.persistence.*;

@Entity @Table(name = "ia_conversaciones")
public class IaConversacion {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) @Column(name = "id_conversacion") private Integer idConversacion;
    @ManyToOne(fetch = FetchType.LAZY, optional = false) @JoinColumn(name = "id_usuario", nullable = false) private Usuario usuario;
    @ManyToOne(fetch = FetchType.LAZY, optional = false) @JoinColumn(name = "id_empresa", nullable = false) private Empresa empresa;
    @Column(length = 200) private String titulo;
    @Column(name = "fecha_inicio", nullable = false) private LocalDateTime fechaInicio;
    @Column(name = "fecha_ultima", nullable = false) private LocalDateTime fechaUltima;
    @Column(nullable = false) private Boolean activa;
    public Integer getIdConversacion() { return idConversacion; }
}
