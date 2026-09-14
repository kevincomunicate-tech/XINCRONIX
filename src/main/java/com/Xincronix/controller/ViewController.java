package com.Xincronix.controller;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Map;

import org.springframework.core.io.ClassPathResource;
import org.springframework.http.CacheControl;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;

/**
 * Routes for the web UI.
 *
 * <p>The original files came from Laravel and are intentionally rendered as
 * static HTML here.  Keeping the translation in one place means a client can
 * never receive an unprocessed {@code asset()}, {@code route()} or Blade
 * expression while the remaining screens are progressively migrated.</p>
 */
@Controller
public class ViewController {

    private static final Map<String, String> VIEW_FILES = Map.ofEntries(
            Map.entry("home", "templates/index.html"),
            Map.entry("login", "templates/auth/Login.html"),
            Map.entry("registro", "templates/auth/registro.html"),
            Map.entry("panel", "templates/panel/Panel.blade.html"),
            Map.entry("panel-admin", "templates/panel/admin_panel.blade.html"),
            Map.entry("panel-supervisor", "templates/panel/supervisor_panel.blade.html"),
            Map.entry("proyectos", "templates/proyecto/Proyecto.blade.php"),
            Map.entry("tareas", "templates/tareas/Tareas.blade.html"),
            Map.entry("equipos", "templates/equipos/Equipos.html"),
            Map.entry("agentes", "templates/Agentes/Agentes.html"),
            Map.entry("asistente", "templates/Agentes/Asistente.html"),
            Map.entry("automatizaciones", "templates/automatizaciones/Automatizaciones.html"),
            Map.entry("analytics", "templates/Analytics/Analytics.html"),
            Map.entry("informacion-team", "templates/información/team.html"),
            Map.entry("informacion-blog", "templates/información/blog.html"),
            Map.entry("informacion-exito", "templates/información/exito.html"),
            Map.entry("informacion-prensa", "templates/información/prensa.html"),
            Map.entry("informacion-trabajo", "templates/información/trabaja_con_nosotros.html"),
            Map.entry("informacion-terminos", "templates/información/terminos.html"),
            Map.entry("informacion-privacidad", "templates/información/privacidad.html"),
            Map.entry("informacion-cookies", "templates/información/cookies.html"),
            Map.entry("informacion-datos", "templates/información/datos.html"),
            Map.entry("informacion-acuerdo", "templates/información/acuerdo.html"),
            Map.entry("informacion-soporte", "templates/información/soporte_tecnico.html"),
            Map.entry("informacion-ventas", "templates/información/ventas-empresariales.html"));

    @GetMapping({"/", "/inicio", "/index.html"})
    public ResponseEntity<String> home() throws IOException { return page("home"); }

    @GetMapping("/reset-password")
    public ResponseEntity<String> resetPassword() {
        return ResponseEntity.ok().contentType(MediaType.TEXT_HTML).body("""
            <!doctype html><html lang='es'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
            <title>Restablecer contraseña | Xincronix</title><body style='font-family:system-ui;max-width:420px;margin:10vh auto;padding:24px'>
            <h1>Restablecer contraseña</h1><p>Elige una contraseña nueva de al menos 8 caracteres.</p>
            <form id='form'><input id='password' type='password' minlength='8' required placeholder='Nueva contraseña' style='width:100%;padding:12px'><button style='margin-top:12px;padding:12px'>Actualizar contraseña</button></form><p id='message'></p>
            <script>document.getElementById('form').onsubmit=async e=>{e.preventDefault();let r=await fetch('/api/auth/password/reset',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:new URLSearchParams(location.search).get('token'),password:document.getElementById('password').value})});let d=await r.json();document.getElementById('message').textContent=d.message;if(r.ok)setTimeout(()=>location='/login',1200)}</script></body></html>
            """);
    }

    @GetMapping({"/login", "/Login", "/Login.html", "/auth/Login.html"})
    public ResponseEntity<String> login() throws IOException { return page("login"); }

    @GetMapping({"/registro", "/Registro", "/registro.html", "/auth/registro.html"})
    public ResponseEntity<String> registro() throws IOException { return page("registro"); }

    @PostMapping("/registro")
    public ResponseEntity<String> registroPendiente() {
        return ResponseEntity.status(501).contentType(MediaType.APPLICATION_JSON)
                .body("{\"success\":false,\"message\":\"El registro aún debe migrarse al servicio Spring Boot.\"}");
    }

        @GetMapping({"/panel", "/Panel", "/Panel.html"})
        public ResponseEntity<String> panel() throws IOException { return page("panel"); }

        @GetMapping({"/panel/admin", "/admin_panel", "/admin/dashboard"})
        public ResponseEntity<String> panelAdmin() throws IOException { return page("panel-admin"); }

        @GetMapping({"/panel/supervisor", "/supervisor_panel"})
        public ResponseEntity<String> panelSupervisor() throws IOException { return page("panel-supervisor"); }

    @GetMapping({"/proyectos", "/Proyecto", "/Proyecto.html"})
    public ResponseEntity<String> proyectos() throws IOException { return page("proyectos"); }

    @GetMapping({"/tareas", "/Tareas", "/Tareas.html"})
    public ResponseEntity<String> tareas() throws IOException { return page("tareas"); }

    @GetMapping({"/equipos", "/Equipos", "/Equipos.html"})
    public ResponseEntity<String> equipos() throws IOException { return page("equipos"); }

    @GetMapping({"/agentes", "/Agentes", "/Agentes.html"})
    public ResponseEntity<String> agentes() throws IOException { return page("agentes"); }

    @GetMapping({"/asistente", "/Asistente", "/Asistente.html"})
    public ResponseEntity<String> asistente() throws IOException { return page("asistente"); }

    @GetMapping({"/automatizaciones", "/Automatizaciones", "/Automatizaciones.html"})
    public ResponseEntity<String> automatizaciones() throws IOException { return page("automatizaciones"); }

    @GetMapping({"/analytics", "/Analytics", "/Analytics.html"})
    public ResponseEntity<String> analytics() throws IOException { return page("analytics"); }

    @GetMapping("/informacion/equipo") public ResponseEntity<String> team() throws IOException { return page("informacion-team"); }
    @GetMapping("/informacion/blog") public ResponseEntity<String> blog() throws IOException { return page("informacion-blog"); }
    @GetMapping("/informacion/casos-de-exito") public ResponseEntity<String> exito() throws IOException { return page("informacion-exito"); }
    @GetMapping("/informacion/prensa") public ResponseEntity<String> prensa() throws IOException { return page("informacion-prensa"); }
    @GetMapping("/informacion/trabaja-con-nosotros") public ResponseEntity<String> trabajo() throws IOException { return page("informacion-trabajo"); }
    @GetMapping("/informacion/terminos") public ResponseEntity<String> terminos() throws IOException { return page("informacion-terminos"); }
    @GetMapping("/informacion/privacidad") public ResponseEntity<String> privacidad() throws IOException { return page("informacion-privacidad"); }
    @GetMapping("/informacion/cookies") public ResponseEntity<String> cookies() throws IOException { return page("informacion-cookies"); }
    @GetMapping("/informacion/datos") public ResponseEntity<String> datos() throws IOException { return page("informacion-datos"); }
    @GetMapping("/informacion/acuerdo") public ResponseEntity<String> acuerdo() throws IOException { return page("informacion-acuerdo"); }
    @GetMapping("/informacion/soporte-tecnico") public ResponseEntity<String> soporte() throws IOException { return page("informacion-soporte"); }
    @GetMapping("/informacion/ventas-empresariales") public ResponseEntity<String> ventas() throws IOException { return page("informacion-ventas"); }

    private ResponseEntity<String> page(String name) throws IOException {
        ClassPathResource resource = new ClassPathResource(VIEW_FILES.get(name));
        try (InputStream input = resource.getInputStream()) {
            String html = new String(input.readAllBytes(), StandardCharsets.UTF_8);
            return ResponseEntity.ok()
                    .contentType(MediaType.TEXT_HTML)
                    .cacheControl(CacheControl.noCache())
                    .body(normalizeLegacyReferences(html));
        }
    }

    private String normalizeLegacyReferences(String html) {
        String normalized = html
                .replaceAll("\\{\\{\\s*asset\\('assets/([^']+)'\\)\\s*}}", "/$1")
                .replace("{{ url('/api/login') }}", "/api/login")
                .replace("{{ url('/Panel') }}", "/panel")
                .replace("{{ url('/registro') }}", "/registro")
                .replace("{{ url('/dashboard') }}", "/panel")
                .replace("{{ route('login') }}", "/login")
                .replace("{{ route('register') }}", "/registro")
                .replaceAll("\\{\\{\\s*csrf_token\\(\\)\\s*}}", "")
                .replaceAll("\\{\\{\\s*now\\(\\)->toDateString\\(\\)\\s*}}", "")
                .replaceAll("\\{\\{[^}]+}}", "")
                .replaceAll("\\{\\-\\-[\\s\\S]*?\\-\\-}}", "")
                .replaceAll("@(?:if|else|endif|vite)\\b[^\\n]*", "");

        for (Map.Entry<String, String> entry : Map.ofEntries(
                Map.entry("Panel", "/panel"), Map.entry("Proyecto", "/proyectos"),
                Map.entry("Tareas", "/tareas"), Map.entry("Equipos", "/equipos"),
                Map.entry("Agentes", "/agentes"), Map.entry("Asistente", "/asistente"),
                Map.entry("Automatizaciones", "/automatizaciones"), Map.entry("Analytics", "/analytics"),
                Map.entry("Login", "/login")).entrySet()) {
            String from = entry.getKey();
            String to = entry.getValue();
            normalized = normalized.replace("href=\"" + from + "\"", "href=\"" + to + "\"")
                    .replace("href=\"" + from + ".html\"", "href=\"" + to + "\"")
                    .replace("window.location.href='" + from + "'", "window.location.href='" + to + "'")
                    .replace("window.location.href = '" + from + ".html'", "window.location.href = '" + to + "'");
        }
        return normalized
                .replace("../controller/tareas.php", "/api/tareas")
                .replace("../controller/equipo.php", "/api/equipos")
                .replace("../controller/analytics.php", "/api/analytics")
                .replace("../controller/dashboard.php", "/api/dashboard")
                .replace("../controller/logout.php", "/api/auth/logout")
                .replace("../../view/login.html", "/login")
                .replace("../../index.html", "/")
                .replace("../index.html", "/")
                .replace("../../Agentes.html", "/agentes")
                .replace("../login.html", "/login")
                .replace("view/login.html", "/login")
                .replace("view/registro.html", "/registro")
                .replace("Assets/css/", "/css/")
                .replace("Assets/js/", "/js/")
                .replace("href=\"equipo.html\"", "href=\"/informacion/equipo\"")
                .replace("href=\"blog.html\"", "href=\"/informacion/blog\"")
                .replace("href=\"exito.html\"", "href=\"/informacion/casos-de-exito\"")
                .replace("href=\"prensa.html\"", "href=\"/informacion/prensa\"")
                .replace("href=\"trabaja_con_nosotros.html\"", "href=\"/informacion/trabaja-con-nosotros\"")
                .replace("href=\"terminos.html\"", "href=\"/informacion/terminos\"")
                .replace("href=\"privacidad.html\"", "href=\"/informacion/privacidad\"")
                .replace("href=\"cookies.html\"", "href=\"/informacion/cookies\"")
                .replace("href=\"datos.html\"", "href=\"/informacion/datos\"")
                .replace("href=\"acuerdo.html\"", "href=\"/informacion/acuerdo\"")
                .replace("href=\"soporte_tecnico.html\"", "href=\"/informacion/soporte-tecnico\"")
                .replace("href=\"ventas_empresariales.html\"", "href=\"/informacion/ventas-empresariales\"");
    }
}
