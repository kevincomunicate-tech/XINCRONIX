package com.Xincronix.model;

import java.time.LocalDateTime;
import jakarta.persistence.*;

@Entity @Table(name = "ia_mensajes")
public class IaMensaje {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) @Column(name = "id_ia_mensaje") private Integer idIaMensaje;
    @ManyToOne(fetch = FetchType.LAZY, optional = false) @JoinColumn(name = "id_conversacion", nullable = false) private IaConversacion conversacion;
    @Column(nullable = false, length = 20) private String rol;
    @Column(nullable = false, columnDefinition = "TEXT") private String contenido;
    @Column(name = "tokens_usados") private Integer tokensUsados;
    @Column(length = 60) private String modelo;
    @Column(name = "fecha_envio", nullable = false) private LocalDateTime fechaEnvio;
    public Integer getIdIaMensaje() { return idIaMensaje; }
}
