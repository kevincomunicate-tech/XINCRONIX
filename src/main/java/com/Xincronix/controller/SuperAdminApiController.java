package com.Xincronix.controller;

import com.Xincronix.dto.SuperAdminEmpresaRequest;
import com.Xincronix.dto.SuperAdminEmpresaResponse;
import com.Xincronix.model.Empresa;
import com.Xincronix.repository.EmpresaRepository;
import com.Xincronix.repository.EquipoRepository;
import com.Xincronix.repository.IaConversacionRepository;
import com.Xincronix.repository.ProyectoRepository;
import com.Xincronix.repository.SolicitudPagoRepository;
import com.Xincronix.repository.TicketSoporteRepository;
import com.Xincronix.repository.UsuarioRepository;
import jakarta.transaction.Transactional;
import jakarta.validation.Valid;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

/** Global company administration is intentionally isolated from tenant-scoped APIs. */
@RestController
@RequestMapping("/api/superadmin")
@PreAuthorize("hasRole('SUPERADMIN')")
public class SuperAdminApiController {
    private final EmpresaRepository empresas;
    private final UsuarioRepository usuarios;
    private final ProyectoRepository proyectos;
    private final EquipoRepository equipos;
    private final IaConversacionRepository conversacionesIa;
    private final SolicitudPagoRepository pagos;
    private final TicketSoporteRepository tickets;

    public SuperAdminApiController(EmpresaRepository empresas, UsuarioRepository usuarios, ProyectoRepository proyectos,
            EquipoRepository equipos, IaConversacionRepository conversacionesIa, SolicitudPagoRepository pagos,
            TicketSoporteRepository tickets) {
        this.empresas = empresas;
        this.usuarios = usuarios;
        this.proyectos = proyectos;
        this.equipos = equipos;
        this.conversacionesIa = conversacionesIa;
        this.pagos = pagos;
        this.tickets = tickets;
    }

    @GetMapping("/empresas")
    public ResponseEntity<Map<String, Object>> listarEmpresas() {
        return ResponseEntity.ok(Map.of("success", true, "data", empresas.findAll().stream()
                .map(SuperAdminEmpresaResponse::from).toList()));
    }

    @GetMapping("/empresas/{id}")
    public ResponseEntity<Map<String, Object>> obtenerEmpresa(@PathVariable Integer id) {
        return ResponseEntity.ok(Map.of("success", true, "data", SuperAdminEmpresaResponse.from(empresa(id))));
    }

    @PostMapping("/empresas")
    public ResponseEntity<Map<String, Object>> crearEmpresa(@Valid @RequestBody SuperAdminEmpresaRequest request) {
        Empresa empresa = new Empresa();
        apply(empresa, request);
        Empresa saved = empresas.save(empresa);
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of("success", true,
                "data", SuperAdminEmpresaResponse.from(saved)));
    }

    @PutMapping("/empresas/{id}")
    public ResponseEntity<Map<String, Object>> actualizarEmpresa(@PathVariable Integer id,
            @Valid @RequestBody SuperAdminEmpresaRequest request) {
        Empresa empresa = empresa(id);
        apply(empresa, request);
        return ResponseEntity.ok(Map.of("success", true, "data", SuperAdminEmpresaResponse.from(empresas.save(empresa))));
    }

    @DeleteMapping("/empresas/{id}")
    @Transactional
    public ResponseEntity<Map<String, Object>> eliminarEmpresa(@PathVariable Integer id) {
        Empresa empresa = empresa(id);
        if (tieneDependencias(id)) {
            throw new ResponseStatusException(HttpStatus.CONFLICT,
                    "No se puede eliminar la empresa porque tiene datos asociados");
        }
        empresas.delete(empresa);
        return ResponseEntity.ok(Map.of("success", true, "data", Map.of("idEmpresa", id)));
    }

    private Empresa empresa(Integer id) {
        return empresas.findById(id).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Empresa no encontrada"));
    }

    private void apply(Empresa empresa, SuperAdminEmpresaRequest request) {
        empresa.setNombre(request.nombre().trim());
        empresa.setNit(request.nit().trim());
        empresa.setEmail(request.email().trim().toLowerCase());
        empresa.setTelefono(request.telefono());
        empresa.setDireccion(request.direccion());
        empresa.setIndustria(request.industria());
        empresa.setPlanSuscripcion(request.planSuscripcion());
        empresa.setSector(request.sector());
        empresa.setAdministrador(request.administrador());
        empresa.setNumEmpleados(request.numEmpleados());
    }

    private boolean tieneDependencias(Integer idEmpresa) {
        return usuarios.existsByEmpresaIdEmpresa(idEmpresa) || proyectos.existsByEmpresaIdEmpresa(idEmpresa)
                || equipos.existsByEmpresaIdEmpresa(idEmpresa) || conversacionesIa.existsByEmpresaIdEmpresa(idEmpresa)
                || pagos.existsByEmpresaIdEmpresa(idEmpresa) || tickets.existsByEmpresaIdEmpresa(idEmpresa);
    }
}
