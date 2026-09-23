package com.Xincronix.controller;

import com.Xincronix.model.Usuario;
import com.Xincronix.repository.UsuarioRepository;
import com.Xincronix.service.AiAssistantService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.util.List;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/assistant")
public class AssistantController {
    private final AiAssistantService assistant;
    private final UsuarioRepository users;

    public AssistantController(AiAssistantService assistant, UsuarioRepository users) {
        this.assistant = assistant;
        this.users = users;
    }

    @GetMapping("/config")
    public Map<String, Object> config(@AuthenticationPrincipal UserDetails principal) {
        Map<String, Object> data = new java.util.LinkedHashMap<>(assistant.configuration());
        Usuario user = principal == null ? null : users.findByEmailIgnoreCase(principal.getUsername()).orElse(null);
        if (user != null) {
            String name = (user.getNombres() + " " + user.getApellidos()).trim();
            data.put("user", Map.of("name", name, "initials", name.isBlank() ? "US" : name.substring(0, 1).toUpperCase(),
                    "role", user.getCargo() == null || user.getCargo().isBlank()
                            ? (user.getRol() == null ? "Usuario" : user.getRol().getNombre())
                            : user.getCargo()));
        }
        return Map.of("success", true, "data", data);
    }

    @PostMapping("/chat")
    public ResponseEntity<Map<String, Object>> chat(@Valid @RequestBody AssistantRequest request,
                                                      @AuthenticationPrincipal UserDetails principal) {
        Usuario user = principal == null ? null : users.findByEmailIgnoreCase(principal.getUsername()).orElse(null);
        if (user == null) return ResponseEntity.status(401).body(Map.of("success", false, "message", "No autenticado"));
        try {
            var answer = assistant.ask(request.provider(), request.message(), request.history(), user);
            return ResponseEntity.ok(Map.of("success", true, "data", Map.of(
                    "reply", answer.reply(), "provider", answer.provider(), "model", answer.model(), "mode", answer.mode())));
        } catch (AiAssistantService.ProviderUnavailableException ex) {
            return ResponseEntity.status(422).body(Map.of("success", false, "message", ex.getMessage()));
        } catch (AiAssistantService.AssistantProviderException ex) {
            return ResponseEntity.badRequest().body(Map.of("success", false, "message", ex.getMessage()));
        }
    }

    public record AssistantRequest(@NotBlank @Size(max = 4000) String message,
                                   @Size(max = 20) String provider,
                                   @Size(max = 30) List<AiAssistantService.ChatMessage> history) {}
}
