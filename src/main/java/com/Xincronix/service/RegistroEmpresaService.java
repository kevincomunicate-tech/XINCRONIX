package com.Xincronix.service;

import com.Xincronix.dto.RegistroEmpresaRequest;
import com.Xincronix.model.Empresa;
import com.Xincronix.model.Rol;
import com.Xincronix.model.SolicitudPago;
import com.Xincronix.model.Usuario;
import com.Xincronix.repository.EmpresaRepository;
import com.Xincronix.repository.RolRepository;
import com.Xincronix.repository.SolicitudPagoRepository;
import com.Xincronix.repository.UsuarioRepository;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.multipart.MultipartFile;

@Service
public class RegistroEmpresaService {
    private final EmpresaRepository empresas;
    private final UsuarioRepository usuarios;
    private final RolRepository roles;
    private final SolicitudPagoRepository solicitudes;
    private final PasswordEncoder passwordEncoder;
    private final ComprobanteStorageService comprobantes;

    public RegistroEmpresaService(EmpresaRepository empresas, UsuarioRepository usuarios, RolRepository roles,
                                  SolicitudPagoRepository solicitudes, PasswordEncoder passwordEncoder,
                                  ComprobanteStorageService comprobantes) {
        this.empresas = empresas;
        this.usuarios = usuarios;
        this.roles = roles;
        this.solicitudes = solicitudes;
        this.passwordEncoder = passwordEncoder;
        this.comprobantes = comprobantes;
    }

    @Transactional
    public Usuario registrar(RegistroEmpresaRequest request, MultipartFile comprobante) {
        String email = request.email().trim().toLowerCase();
        if (empresas.existsByNit(request.nit().trim())) throw new ResponseStatusException(HttpStatus.CONFLICT, "El NIT ya está registrado");
        if (empresas.existsByEmail(email) || usuarios.existsByEmail(email)) throw new ResponseStatusException(HttpStatus.CONFLICT, "El correo ya está registrado");

        String comprobanteGuardado = comprobantes.store(comprobante);
        TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
            @Override
            public void afterCompletion(int status) {
                if (status == STATUS_ROLLED_BACK) {
                    try {
                        java.nio.file.Files.deleteIfExists(java.nio.file.Path.of(comprobanteGuardado));
                    } catch (java.io.IOException ignored) {
                        // El rollback de base de datos no debe ocultarse por un fallo de limpieza de archivo.
                    }
                }
            }
        });
        Empresa empresa = new Empresa();
        empresa.setNombre(request.nombre().trim());
        empresa.setNit(request.nit().trim());
        empresa.setEmail(email);
        empresa.setTelefono(request.telefono().trim());
        empresa.setSector(request.sector().trim());
        empresa.setNumEmpleados(request.numEmpleados().trim());
        empresa.setPlanSuscripcion(request.plan().trim().toUpperCase());
        empresa.setAdministrador((request.nombres().trim() + " " + request.apellidos().trim()).trim());
        empresa.setComprobante(comprobanteGuardado);
        empresa = empresas.save(empresa);

        Usuario admin = new Usuario();
        admin.setNombres(request.nombres().trim());
        admin.setApellidos(request.apellidos().trim());
        admin.setEmail(email);
        admin.setCargo(request.cargo().trim());
        admin.setTelefono(request.telefono().trim());
        admin.setPassword(passwordEncoder.encode(request.password()));
        admin.setEstado(true);
        admin.setEmpresa(empresa);
        admin.setRol(rolAdministrador());
        admin = usuarios.save(admin);

        SolicitudPago solicitud = new SolicitudPago();
        solicitud.setEmpresa(empresa);
        solicitud.setPlan(request.plan().trim().toUpperCase());
        solicitud.setMetodoPago(request.metodoPago().trim().toUpperCase());
        solicitud.setReferencia(request.referencia().trim());
        solicitud.setNotas(request.notas());
        solicitud.setRutaComprobante(comprobanteGuardado);
        solicitud.setEstado("PENDIENTE");
        solicitudes.save(solicitud);
        return admin;
    }

    private Rol rolAdministrador() {
        return roles.findByNombreIgnoreCase("ADMINISTRADOR").orElseGet(() -> {
            Rol rol = new Rol();
            rol.setNombre("ADMINISTRADOR");
            rol.setDescripcion("Administrador de empresa");
            return roles.save(rol);
        });
    }
}
