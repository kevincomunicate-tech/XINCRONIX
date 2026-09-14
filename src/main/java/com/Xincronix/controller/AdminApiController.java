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
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import java.nio.charset.StandardCharsets;

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

    /** Server-side CSV export. Filters are evaluated on the same data the administrator can see. */
    @GetMapping(value = "/reportes/{tipo}.csv", produces = "text/csv")
    public ResponseEntity<byte[]> reporte(@org.springframework.web.bind.annotation.PathVariable String tipo,
                                          @RequestParam(required = false) String q,
                                          @RequestParam(required = false) String sector,
                                          @RequestParam(required = false) String plan,
                                          @RequestParam(required = false) String estado,
                                          @RequestParam(required = false) String prioridad) {
        String csv;
        switch (tipo.toLowerCase()) {
            case "empresas" -> csv = empresas.findAll().stream()
                    .filter(e -> matches(q, e.getNombre(), e.getEmail(), e.getNit()))
                    .filter(e -> matchesExact(sector, e.getSector())).filter(e -> matchesExact(plan, e.getPlanSuscripcion()))
                    .map(this::empresaData).collect(java.util.stream.Collectors.collectingAndThen(java.util.stream.Collectors.toList(), this::csv));
            case "pagos" -> csv = pagos.findAll().stream()
                    .filter(p -> matches(q, p.getReferencia(), p.getPlan(), p.getEmpresa() == null ? null : p.getEmpresa().getNombre()))
                    .filter(p -> matchesExact(estado, p.getEstado())).filter(p -> matchesExact(plan, p.getPlan()))
                    .map(this::pagoData).collect(java.util.stream.Collectors.collectingAndThen(java.util.stream.Collectors.toList(), this::csv));
            case "tickets" -> csv = tickets.findAll().stream()
                    .filter(t -> matches(q, t.getAsunto(), t.getDescripcion())).filter(t -> matchesExact(estado, t.getEstado())).filter(t -> matchesExact(prioridad, t.getPrioridad()))
                    .map(this::ticketData).collect(java.util.stream.Collectors.collectingAndThen(java.util.stream.Collectors.toList(), this::csv));
            default -> throw new IllegalArgumentException("Tipo de reporte no soportado");
        }
        return ResponseEntity.ok().header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=xincronix_" + tipo + ".csv")
                .contentType(new MediaType("text", "csv", StandardCharsets.UTF_8)).body(("\uFEFF" + csv).getBytes(StandardCharsets.UTF_8));
    }

    private boolean matches(String q, String... values) { if (q == null || q.isBlank()) return true; String needle = q.toLowerCase(); return java.util.Arrays.stream(values).filter(java.util.Objects::nonNull).anyMatch(v -> v.toLowerCase().contains(needle)); }
    private boolean matchesExact(String filter, String value) { return filter == null || filter.isBlank() || (value != null && value.equalsIgnoreCase(filter)); }
    private String csv(List<Map<String, Object>> rows) { if (rows.isEmpty()) return ""; List<String> headers = new java.util.ArrayList<>(rows.getFirst().keySet()); StringBuilder out = new StringBuilder(String.join(",", headers)); for (Map<String, Object> row : rows) { out.append('\n'); for (int i = 0; i < headers.size(); i++) { if (i > 0) out.append(','); out.append('"').append(String.valueOf(row.get(headers.get(i))).replace("\"", "\"\"")).append('"'); } } return out.toString(); }

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
