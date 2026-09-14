package com.Xincronix.controller;

import com.Xincronix.model.Empresa;
import com.Xincronix.model.SolicitudPago;
import com.Xincronix.model.TicketSoporte;
import com.Xincronix.repository.EmpresaRepository;
import com.Xincronix.repository.SolicitudPagoRepository;
import com.Xincronix.repository.TicketSoporteRepository;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
@PreAuthorize("hasRole('ADMINISTRADOR')")
public class AdminApiController {
    private final EmpresaRepository empresas;
    private final SolicitudPagoRepository pagos;
    private final TicketSoporteRepository tickets;

    public AdminApiController(EmpresaRepository empresas, SolicitudPagoRepository pagos,
                              TicketSoporteRepository tickets) {
        this.empresas = empresas;
        this.pagos = pagos;
        this.tickets = tickets;
    }

    @GetMapping("/empresas")
    public Map<String, Object> empresas(@RequestParam(defaultValue = "list") String action) {
        List<Map<String, Object>> data = empresas.findAll().stream().map(this::empresaData).toList();
        return Map.of("success", true, "data", data);
    }

    @GetMapping("/pagos")
    public Map<String, Object> pagos(@RequestParam(defaultValue = "list") String action) {
        List<Map<String, Object>> data = pagos.findAll().stream().map(this::pagoData).toList();
        return Map.of("success", true, "data", data);
    }

    @GetMapping("/tickets")
    public Map<String, Object> tickets(@RequestParam(defaultValue = "list") String action) {
        List<Map<String, Object>> data = tickets.findAll().stream().map(this::ticketData).toList();
        return Map.of("success", true, "data", data);
    }

    @PostMapping("/empresas")
    public Map<String, Object> modificarEmpresa(@RequestParam Map<String, String> form) {
        String action = form.getOrDefault("action", "create");
        if ("delete".equals(action)) {
            empresas.deleteById(requiredId(form, "id_empresa"));
            return Map.of("status", "success", "message", "Empresa eliminada");
        }
        Empresa empresa = "update".equals(action)
                ? empresas.findById(requiredId(form, "id_empresa")).orElseThrow()
                : new Empresa();
        empresa.setNombre(required(form, "nombre"));
        empresa.setNit(required(form, "nit"));
        empresa.setEmail(required(form, "email"));
        empresa.setTelefono(form.get("telefono"));
        empresa.setSector(form.get("sector"));
        empresa.setPlanSuscripcion(form.get("plan"));
        empresa.setAdministrador(form.get("administrador"));
        empresa.setNumEmpleados(form.get("num_empleados"));
        empresa.setDireccion(form.get("direccion"));
        empresas.save(empresa);
        return Map.of("status", "success", "message", "Empresa guardada", "data", empresaData(empresa));
    }

    @PostMapping("/tickets")
    public Map<String, Object> modificarTicket(@RequestParam Map<String, String> form) {
        String action = form.getOrDefault("action", "create");
        Integer id = form.get("id_ticket") == null || form.get("id_ticket").isBlank()
                ? null : Integer.valueOf(form.get("id_ticket"));
        if ("delete".equals(action)) {
            tickets.deleteById(id);
            return Map.of("status", "success", "message", "Ticket eliminado");
        }
        TicketSoporte ticket = "update".equals(action) ? tickets.findById(id).orElseThrow() : new TicketSoporte();
        ticket.setAsunto(required(form, "asunto"));
        ticket.setDescripcion(required(form, "descripcion"));
        ticket.setPrioridad(form.getOrDefault("prioridad", "media"));
        ticket.setEstado(form.getOrDefault("estado", "abierto"));
        tickets.save(ticket);
        return Map.of("status", "success", "message", "Ticket guardado", "data", ticketData(ticket));
    }

    private String required(Map<String, String> form, String name) {
        String value = form.get(name);
        if (value == null || value.isBlank()) throw new IllegalArgumentException(name + " es obligatorio");
        return value.trim();
    }

    private Integer requiredId(Map<String, String> form, String name) {
        return Integer.valueOf(required(form, name));
    }

    private Map<String, Object> empresaData(Empresa empresa) {
        return Map.ofEntries(
                Map.entry("id_empresa", empresa.getIdEmpresa()),
                Map.entry("nombre", value(empresa.getNombre())),
                Map.entry("nit", value(empresa.getNit())),
                Map.entry("email", value(empresa.getEmail())),
                Map.entry("sector", value(empresa.getSector())),
                Map.entry("plan", value(empresa.getPlanSuscripcion())),
                Map.entry("administrador", value(empresa.getAdministrador())));
    }

    private Map<String, Object> pagoData(SolicitudPago pago) {
        return Map.ofEntries(
                Map.entry("id_solicitud", pago.getIdSolicitud()),
                Map.entry("empresa", value(pago.getEmpresa() == null ? null : pago.getEmpresa().getNombre())),
                Map.entry("plan", value(pago.getPlan())),
                Map.entry("metodo_pago", value(pago.getMetodoPago())),
                Map.entry("referencia", value(pago.getReferencia())),
                Map.entry("estado", value(pago.getEstado())));
    }

    private Map<String, Object> ticketData(TicketSoporte ticket) {
        return Map.ofEntries(
                Map.entry("id_ticket", ticket.getIdTicket()),
                Map.entry("asunto", value(ticket.getAsunto())),
                Map.entry("descripcion", value(ticket.getDescripcion())),
                Map.entry("prioridad", value(ticket.getPrioridad())),
                Map.entry("estado", value(ticket.getEstado())));
    }

    private String value(String value) { return value == null ? "" : value; }
}