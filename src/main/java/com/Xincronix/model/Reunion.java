package com.Xincronix.model;

import java.time.LocalDateTime;
import jakarta.persistence.*;

@Entity @Table(name = "reuniones")
public class Reunion {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) @Column(name = "id_reunion") private Integer idReunion;
    @Column(nullable = false, length = 150) private String nombre;
    @Column(length = 300) private String enlace;
    @Column(nullable = false) private LocalDateTime fecha;
    @Column(nullable = false, length = 50) private String estado;
    @Column(name = "grabacion_url", length = 500) private String grabacionUrl;
    @ManyToOne(fetch = FetchType.LAZY) @JoinColumn(name = "id_equipo") private Equipo equipo;
    @ManyToOne(fetch = FetchType.LAZY) @JoinColumn(name = "id_usuario") private Usuario usuario;
    public Integer getIdReunion() { return idReunion; }
}
