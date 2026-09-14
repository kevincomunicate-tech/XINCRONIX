package com.Xincronix.controller;

import com.Xincronix.model.Usuario;
import com.Xincronix.repository.EquipoRepository;
import com.Xincronix.repository.ProyectoRepository;
import com.Xincronix.repository.TareaRepository;
import com.Xincronix.repository.UsuarioRepository;
import com.Xincronix.service.UsuarioService;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/supervisor")
@PreAuthorize("hasAnyRole('SUPERVISOR', 'MANAGER', 'ADMINISTRADOR')")
public class SupervisorDashboardController {

    private final UsuarioRepository usuarioRepository;
    private final ProyectoRepository proyectoRepository;
    private final TareaRepository tareaRepository;
    private final EquipoRepository equipoRepository;
    private final UsuarioService usuarioService;

    public SupervisorDashboardController(UsuarioRepository usuarioRepository,
                                         ProyectoRepository proyectoRepository,
                                         TareaRepository tareaRepository,
                                         EquipoRepository equipoRepository,
                                         UsuarioService usuarioService) {
        this.usuarioRepository = usuarioRepository;
        this.proyectoRepository = proyectoRepository;
        this.tareaRepository = tareaRepository;
        this.equipoRepository = equipoRepository;
        this.usuarioService = usuarioService;
    }

    @GetMapping({"", "/", "/dashboard"})
    public String dashboard(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Usuario actor = usuarioRepository.findByEmail(userDetails.getUsername()).orElseThrow();

        Integer empresaId = actor.getEmpresa() != null ? actor.getEmpresa().getIdEmpresa() : null;

        long totalEmpleados = 0;
        if (empresaId != null) {
            totalEmpleados = usuarioRepository
                    .findByEmpresaIdEmpresaOrderByNombresAscApellidosAsc(empresaId)
                    .size();
        }

        long totalProyectos = 0;
        long totalTareas = 0;
        long totalEquipos = 0;

        if (empresaId != null) {
            var proyectosEmpresa = proyectoRepository.findByEmpresaIdEmpresa(empresaId);
            totalProyectos = proyectosEmpresa.size();
            totalTareas = proyectosEmpresa.stream()
                    .mapToLong(proyecto -> tareaRepository.findByProyectoIdProyecto(proyecto.getIdProyecto()).size())
                    .sum();
            totalEquipos = equipoRepository.findByEmpresaIdEmpresa(empresaId).size();
        }

        model.addAttribute("usuario", actor);
        model.addAttribute("nombreCompleto", actor.getNombres() + " " + actor.getApellidos());
        model.addAttribute("empresaNombre",
                actor.getEmpresa() != null ? actor.getEmpresa().getNombre() : "Sin empresa");
        model.addAttribute("rol",
                actor.getRol() != null ? actor.getRol().getNombre() : "Supervisor");

        model.addAttribute("totalEmpleados", totalEmpleados);
        model.addAttribute("totalProyectos", totalProyectos);
        model.addAttribute("totalTareas", totalTareas);
        model.addAttribute("totalEquipos", totalEquipos);

        model.addAttribute("empleados",
                empresaId != null
                        ? usuarioRepository.findByEmpresaIdEmpresaOrderByNombresAscApellidosAsc(empresaId)
                        : java.util.List.of());

        return "supervisor/dashboard";
    }

    @GetMapping("/empleados")
    public String empleados(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Usuario actor = usuarioRepository.findByEmail(userDetails.getUsername()).orElseThrow();
        model.addAttribute("usuario", actor);
        model.addAttribute("nombreCompleto", actor.getNombres() + " " + actor.getApellidos());
        model.addAttribute("empleados", usuarioService.listar(actor));
        return "supervisor/empleados";
    }

    @GetMapping("/proyectos")
    public String proyectos(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Usuario actor = usuarioRepository.findByEmail(userDetails.getUsername()).orElseThrow();
        model.addAttribute("usuario", actor);
        model.addAttribute("nombreCompleto", actor.getNombres() + " " + actor.getApellidos());
        model.addAttribute("proyectos", actor.getIdEmpresa() == null
            ? java.util.List.of() : proyectoRepository.findByEmpresaIdEmpresa(actor.getIdEmpresa()));
        return "supervisor/proyectos";
    }

    @GetMapping("/equipos")
    public String equipos(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Usuario actor = usuarioRepository.findByEmail(userDetails.getUsername()).orElseThrow();
        model.addAttribute("usuario", actor);
        model.addAttribute("nombreCompleto", actor.getNombres() + " " + actor.getApellidos());
        model.addAttribute("equipos", actor.getIdEmpresa() == null
            ? java.util.List.of() : equipoRepository.findByEmpresaIdEmpresa(actor.getIdEmpresa()));
        return "supervisor/equipos";
    }
}