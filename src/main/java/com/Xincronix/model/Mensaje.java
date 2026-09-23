package com.Xincronix.model;

import java.time.LocalDateTime;
import jakarta.persistence.*;

@Entity @Table(name = "mensajes")
public class Mensaje {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) @Column(name = "id_mensajes") private Integer idMensajes;
    @Column(nullable = false, columnDefinition = "TEXT") private String contenido;
    @Column(name = "fecha_envio", nullable = false) private LocalDateTime fechaEnvio;
    @Column(nullable = false) private Boolean estado;
    @Column(nullable = false) private Boolean leido;
    @ManyToOne(fetch = FetchType.LAZY, optional = false) @JoinColumn(name = "id_usuario", nullable = false) private Usuario remitente;
    @ManyToOne(fetch = FetchType.LAZY) @JoinColumn(name = "id_destinatario") private Usuario destinatario;
    public Integer getIdMensajes() { return idMensajes; }
}
