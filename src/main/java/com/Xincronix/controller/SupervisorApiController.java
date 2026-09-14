package com.Xincronix.controller;

import com.Xincronix.model.Empresa;
import com.Xincronix.model.Equipo;
import com.Xincronix.model.Proyecto;
import com.Xincronix.model.Reunion;
import com.Xincronix.model.SolicitudPago;
import com.Xincronix.model.Tarea;
import com.Xincronix.model.TicketSoporte;
import com.Xincronix.model.Usuario;
import com.Xincronix.repository.EquipoRepository;
import com.Xincronix.repository.EmpresaRepository;
import com.Xincronix.repository.ProyectoRepository;
import com.Xincronix.repository.ReunionRepository;
import com.Xincronix.repository.SolicitudPagoRepository;
import com.Xincronix.repository.TareaRepository;
import com.Xincronix.repository.TicketSoporteRepository;
import com.Xincronix.repository.UsuarioRepository;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/supervisor")
@PreAuthorize("hasAnyRole('SUPERVISOR', 'MANAGER', 'ADMINISTRADOR')")
public class SupervisorApiController {
    private final UsuarioRepository usuarios;
    private final EmpresaRepository empresas;
    private final EquipoRepository equipos;
    private final ProyectoRepository proyectos;
    private final TareaRepository tareas;
    private final ReunionRepository reuniones;
    private final SolicitudPagoRepository pagos;
    private final TicketSoporteRepository tickets;

    public SupervisorApiController(UsuarioRepository usuarios, EmpresaRepository empresas,
                                   EquipoRepository equipos, ProyectoRepository proyectos,
                                   TareaRepository tareas, ReunionRepository reuniones,
                                   SolicitudPagoRepository pagos, TicketSoporteRepository tickets) {
        this.usuarios = usuarios;
        this.empresas = empresas;
        this.equipos = equipos;
        this.proyectos = proyectos;
        this.tareas = tareas;
        this.reuniones = reuniones;
        this.pagos = pagos;
        this.tickets = tickets;
    }

    @GetMapping("/dashboard")
    public Map<String, Object> dashboard(@AuthenticationPrincipal UserDetails principal) {
        Usuario actor = actor(principal);
        Integer empresaId = actor.getIdEmpresa();
        List<Usuario> empleados = usuarios.findByEmpresaIdEmpresaOrderByNombresAscApellidosAsc(empresaId);
        List<Proyecto> proyectosEmpresa = proyectos.findByEmpresaIdEmpresa(empresaId);
        List<Equipo> equiposEmpresa = equipos.findByEmpresaIdEmpresa(empresaId);
        return Map.of("status", "success", "data", Map.of(
                "empresa", empresaData(actor.getEmpresa()),
                "empleados", empleados.stream().map(this::usuarioData).toList(),
                "proyectos", proyectosEmpresa.stream().map(this::proyectoData).toList(),
                "equipos", equiposEmpresa.stream().map(this::equipoData).toList(),
                "estadisticas", Map.of("empleados", empleados.size(), "proyectos", proyectosEmpresa.size(), "equipos", equiposEmpresa.size())));
    }

    @GetMapping("/empresa")
    public Map<String, Object> empresa(@AuthenticationPrincipal UserDetails principal) {
        return Map.of("status", "success", "data", empresaData(actor(principal).getEmpresa()));
    }

    @GetMapping("/empleados")
    public Map<String, Object> empleados(@AuthenticationPrincipal UserDetails principal) {
        return Map.of("status", "success", "data", usuarios.findByEmpresaIdEmpresaOrderByNombresAscApellidosAsc(actor(principal).getIdEmpresa()).stream().map(this::usuarioData).toList());
    }

    @GetMapping("/equipos")
    public Map<String, Object> equipos(@AuthenticationPrincipal UserDetails principal, @RequestParam(defaultValue = "list") String action) {
        return Map.of("status", "success", "data", equipos.findByEmpresaIdEmpresa(actor(principal).getIdEmpresa()).stream().map(this::equipoData).toList());
    }

    @GetMapping("/proyectos")
    public Map<String, Object> proyectos(@AuthenticationPrincipal UserDetails principal) {
        return Map.of("status", "success", "data", proyectos.findByEmpresaIdEmpresa(actor(principal).getIdEmpresa()).stream().map(this::proyectoData).toList());
    }

    @GetMapping("/tareas")
    public Map<String, Object> tareas(@AuthenticationPrincipal UserDetails principal) {
        Integer empresaId = actor(principal).getIdEmpresa();
        List<Map<String, Object>> data = tareas.findAll().stream()
                .filter(tarea -> tarea.getProyecto() != null && tarea.getProyecto().getEmpresa() != null
                        && empresaId.equals(tarea.getProyecto().getEmpresa().getIdEmpresa()))
                .map(this::tareaData).toList();
        return Map.of("status", "success", "data", data);
    }

    @GetMapping("/reuniones")
    public Map<String, Object> reuniones(@AuthenticationPrincipal UserDetails principal) {
        return Map.of("status", "success", "data", reuniones.findByUsuarioIdUsuario(actor(principal).getIdUsuario()).stream().map(this::reunionData).toList());
    }

    @GetMapping("/pagos")
    public Map<String, Object> pagos(@AuthenticationPrincipal UserDetails principal) {
        return Map.of("status", "success", "data", pagos.findByEmpresaIdEmpresa(actor(principal).getIdEmpresa()).stream().map(this::pagoData).toList());
    }

    @GetMapping("/tickets")
    public Map<String, Object> tickets(@AuthenticationPrincipal UserDetails principal) {
        return Map.of("status", "success", "data", tickets.findByEmpresaIdEmpresa(actor(principal).getIdEmpresa()).stream().map(this::ticketData).toList());
    }

    private Usuario actor(UserDetails principal) { return usuarios.findByEmail(principal.getUsername()).orElseThrow(); }
    private Map<String, Object> empresaData(Empresa value) { return Map.of("id_empresa", value.getIdEmpresa(), "nombre", text(value.getNombre()), "nit", text(value.getNit()), "email", text(value.getEmail()), "plan", text(value.getPlanSuscripcion())); }
    private Map<String, Object> usuarioData(Usuario value) { return Map.of("id_usuario", value.getIdUsuario(), "nombre", text(value.getNombres() + " " + value.getApellidos()), "email", text(value.getEmail()), "cargo", text(value.getCargo()), "estado", Boolean.TRUE.equals(value.getEstado())); }
    private Map<String, Object> equipoData(Equipo value) { return Map.of("id_equipo", value.getIdEquipo(), "nombre", text(value.getNombre()), "descripcion", text(value.getDescripcion()), "miembros", value.getMiembros() == null ? 0 : value.getMiembros()); }
    private Map<String, Object> proyectoData(Proyecto value) { return Map.of("id_proyecto", value.getIdProyecto(), "nombre", text(value.getNombre()), "descripcion", text(value.getDescripcion()), "estado", text(value.getEstado())); }
    private Map<String, Object> tareaData(Tarea value) { return Map.of("id_tarea", value.getIdTarea(), "titulo", text(value.getTitulo()), "estado", text(value.getEstado()), "prioridad", text(value.getPrioridad())); }
    private Map<String, Object> reunionData(Reunion value) { return Map.of("id_reunion", value.getIdReunion(), "nombre", text(value.getNombre()), "fecha", text(value.getFecha() == null ? null : value.getFecha().toString()), "estado", text(value.getEstado())); }
    private Map<String, Object> pagoData(SolicitudPago value) { return Map.of("id_solicitud", value.getIdSolicitud(), "plan", text(value.getPlan()), "metodo_pago", text(value.getMetodoPago()), "estado", text(value.getEstado())); }
    private Map<String, Object> ticketData(TicketSoporte value) { return Map.of("id_ticket", value.getIdTicket(), "asunto", text(value.getAsunto()), "prioridad", text(value.getPrioridad()), "estado", text(value.getEstado())); }
    private String text(String value) { return value == null ? "" : value; }
}