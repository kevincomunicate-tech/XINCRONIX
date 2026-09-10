package com.Xincronix.model;

import java.math.BigDecimal;
import java.time.LocalDate;
import jakarta.persistence.*;

@Entity @Table(name = "metrica_rendimiento")
public class MetricaRendimiento {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) @Column(name = "id_metrica") private Integer idMetrica;
    @Column(name = "tipo_metrica", nullable = false, length = 100) private String tipoMetrica;
    @Column(nullable = false, precision = 12, scale = 4) private BigDecimal valor;
    @Column(precision = 12, scale = 4) private BigDecimal meta;
    @Column(length = 20) private String unidad;
    @Column(name = "fecha_inicio_periodo", nullable = false) private LocalDate fechaInicioPeriodo;
    @Column(name = "fecha_fin_periodo", nullable = false) private LocalDate fechaFinPeriodo;
    @ManyToOne(fetch = FetchType.LAZY, optional = false) @JoinColumn(name = "id_usuario", nullable = false) private Usuario usuario;
    public Integer getIdMetrica() { return idMetrica; }
}
