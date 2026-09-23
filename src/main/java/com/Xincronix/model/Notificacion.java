package com.Xincronix.model;

import java.time.LocalDateTime;
import jakarta.persistence.*;

@Entity @Table(name = "notificaciones")
public class Notificacion {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) @Column(name = "id_notificaciones") private Integer idNotificaciones;
    @Column(nullable = false, length = 100) private String titulo;
    @Column(nullable = false, columnDefinition = "TEXT") private String mensaje;
    @Column(length = 50) private String tipo;
    @Column(name = "fecha_envio", nullable = false) private LocalDateTime fechaEnvio;
    @Column(nullable = false) private Boolean estado;
    @Column(nullable = false) private Boolean leida;
    @ManyToOne(fetch = FetchType.LAZY, optional = false) @JoinColumn(name = "id_usuario", nullable = false) private Usuario usuario;
    public Integer getIdNotificaciones() { return idNotificaciones; }
}
