package com.Xincronix.model;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "empresa")
public class Empresa {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) @Column(name = "id_empresa")
    private Integer idEmpresa;
    @Column(nullable = false, length = 200) private String nombre;
    @Column(nullable = false, unique = true, length = 30) private String nit;
    @Column(nullable = false, unique = true, length = 150) private String email;
    @Column(length = 20) private String telefono;
    @Column(length = 300) private String direccion;
    @Column(length = 100) private String industria;
    @Column(name = "plan_suscripcion", length = 50) private String planSuscripcion;
    @Column(length = 50) private String sector;
    @Column(length = 120) private String administrador;
    @Column(name = "num_empleados", length = 30) private String numEmpleados;
    @Column(length = 250) private String comprobante;
    @Column(name = "fecha_actualizacion", nullable = false) private LocalDateTime fechaActualizacion;
    @Column(name = "fecha_creacion", nullable = false) private LocalDateTime fechaCreacion;

    public Integer getIdEmpresa() { return idEmpresa; }
    public void setIdEmpresa(Integer idEmpresa) { this.idEmpresa = idEmpresa; }
    public String getNombre() { return nombre; }
    public void setNombre(String nombre) { this.nombre = nombre; }
    public String getNit() { return nit; }
    public void setNit(String nit) { this.nit = nit; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getTelefono() { return telefono; }
    public void setTelefono(String telefono) { this.telefono = telefono; }
    public String getDireccion() { return direccion; }
    public void setDireccion(String direccion) { this.direccion = direccion; }
    public String getIndustria() { return industria; }
    public void setIndustria(String industria) { this.industria = industria; }
    public String getPlanSuscripcion() { return planSuscripcion; }
    public void setPlanSuscripcion(String planSuscripcion) { this.planSuscripcion = planSuscripcion; }
    public String getSector() { return sector; }
    public void setSector(String sector) { this.sector = sector; }
    public String getAdministrador() { return administrador; }
    public void setAdministrador(String administrador) { this.administrador = administrador; }
    public String getNumEmpleados() { return numEmpleados; }
    public void setNumEmpleados(String numEmpleados) { this.numEmpleados = numEmpleados; }
    public String getComprobante() { return comprobante; }
    public void setComprobante(String comprobante) { this.comprobante = comprobante; }
    public LocalDateTime getFechaActualizacion() { return fechaActualizacion; }
    public void setFechaActualizacion(LocalDateTime fechaActualizacion) { this.fechaActualizacion = fechaActualizacion; }
    public LocalDateTime getFechaCreacion() { return fechaCreacion; }
    public void setFechaCreacion(LocalDateTime fechaCreacion) { this.fechaCreacion = fechaCreacion; }
}
