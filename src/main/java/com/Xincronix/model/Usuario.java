package com.Xincronix.model;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import jakarta.persistence.PrePersist;

@Entity
@Table(name = "usuarios")
public class Usuario {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) @Column(name = "id_usuario")
    private Integer idUsuario;
    @Column(nullable = false, length = 100) private String nombres;
    @Column(nullable = false, length = 100) private String apellidos;
    @Column(nullable = false, unique = true, length = 150) private String email;
    @Column(nullable = false, length = 255) private String password;
    @Column(length = 80) private String cargo;
    @Column(length = 20) private String telefono;
    @Column(length = 300) private String avatar;
    @Column(nullable = false) private Boolean estado;
    @Column(name = "fecha_creacion", nullable = false) private LocalDateTime fechaCreacion;
    @Column(name = "two_factor_secret", length = 64) private String twoFactorSecret;
    @Column(name = "two_factor_enabled", nullable = false) private Boolean twoFactorEnabled = Boolean.FALSE;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "id_empresa", nullable = false)
    private Empresa empresa;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "id_roles", nullable = false)
    private Rol rol;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "id_perfil")
    private PerfilEspecifico perfil;

    public Integer getIdUsuario() { return idUsuario; }
    public void setIdUsuario(Integer idUsuario) { this.idUsuario = idUsuario; }
    public String getNombres() { return nombres; }
    public void setNombres(String nombres) { this.nombres = nombres; }
    public String getApellidos() { return apellidos; }
    public void setApellidos(String apellidos) { this.apellidos = apellidos; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
    public String getCargo() { return cargo; }
    public void setCargo(String cargo) { this.cargo = cargo; }
    public String getTelefono() { return telefono; }
    public void setTelefono(String telefono) { this.telefono = telefono; }
    public String getAvatar() { return avatar; }
    public void setAvatar(String avatar) { this.avatar = avatar; }
    public Boolean getEstado() { return estado; }
    public void setEstado(Boolean estado) { this.estado = estado; }
    public LocalDateTime getFechaCreacion() { return fechaCreacion; }
    public void setFechaCreacion(LocalDateTime fechaCreacion) { this.fechaCreacion = fechaCreacion; }
    public String getTwoFactorSecret() { return twoFactorSecret; }
    public void setTwoFactorSecret(String twoFactorSecret) { this.twoFactorSecret = twoFactorSecret; }
    public Boolean getTwoFactorEnabled() { return twoFactorEnabled; }
    public void setTwoFactorEnabled(Boolean twoFactorEnabled) { this.twoFactorEnabled = twoFactorEnabled; }
    public Empresa getEmpresa() { return empresa; }
    public void setEmpresa(Empresa empresa) { this.empresa = empresa; }
    public Rol getRol() { return rol; }
    public void setRol(Rol rol) { this.rol = rol; }
    public PerfilEspecifico getPerfil() { return perfil; }
    public void setPerfil(PerfilEspecifico perfil) { this.perfil = perfil; }

    /** Compatibility accessors for the existing controller while it is moved to UsuarioService. */
    public Integer getIdEmpresa() { return empresa == null ? null : empresa.getIdEmpresa(); }
    public void setIdEmpresa(Integer idEmpresa) {
        if (idEmpresa == null) { this.empresa = null; return; }
        Empresa value = new Empresa(); value.setIdEmpresa(idEmpresa); this.empresa = value;
    }
    public Integer getIdRoles() { return rol == null ? null : rol.getIdRoles(); }
    public void setIdRoles(Integer idRoles) {
        if (idRoles == null) { this.rol = null; return; }
        Rol value = new Rol(); value.setIdRoles(idRoles); this.rol = value;
    }
    public Integer getIdPerfil() { return perfil == null ? null : perfil.getIdPerfil(); }
    public void setIdPerfil(Integer idPerfil) {
        if (idPerfil == null) { this.perfil = null; return; }
        PerfilEspecifico value = new PerfilEspecifico(); value.setIdPerfil(idPerfil); this.perfil = value;
    }

    @PrePersist
    void onCreate() {
        if (fechaCreacion == null) fechaCreacion = LocalDateTime.now();
        if (estado == null) estado = Boolean.TRUE;
        if (twoFactorEnabled == null) twoFactorEnabled = Boolean.FALSE;
    }
}
