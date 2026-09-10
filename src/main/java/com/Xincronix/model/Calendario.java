package com.Xincronix.model;

import java.time.LocalDateTime;
import jakarta.persistence.*;

@Entity @Table(name = "calendario")
public class Calendario {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) @Column(name = "id_calendario") private Integer idCalendario;
    @Column(name = "fecha_evento", nullable = false) private LocalDateTime fechaEvento;
    @Column(columnDefinition = "TEXT") private String nota;
    @ManyToOne(fetch = FetchType.LAZY, optional = false) @JoinColumn(name = "id_usuario", nullable = false) private Usuario usuario;
    public Integer getIdCalendario() { return idCalendario; }
}
