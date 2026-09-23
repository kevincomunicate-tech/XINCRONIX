package com.Xincronix.service;

import com.Xincronix.model.Proyecto;
import com.Xincronix.model.Tarea;
import com.Xincronix.model.Usuario;
import com.Xincronix.repository.ProyectoRepository;
import com.Xincronix.repository.TareaRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

/** Server-side gateway for the providers shown in the assistant UI. */
@Service
public class AiAssistantService {

    private static final Set<String> PROVIDERS = Set.of("grok", "openai", "gemini", "anthropic", "local");
    private final ObjectMapper json;
    private final ProyectoRepository proyectos;
    private final TareaRepository tareas;
    private final HttpClient httpClient;

    @Value("${xincronix.ai.provider:local}") private String configuredProvider;
    @Value("${xincronix.ai.temperature:0.35}") private double temperature;
    @Value("${xincronix.ai.max-history:12}") private int maxHistory;
    @Value("${xincronix.ai.timeout-seconds:45}") private int timeoutSeconds;
    @Value("${xincronix.ai.grok.api-key:}") private String grokApiKey;
    @Value("${xincronix.ai.grok.model:grok-2-latest}") private String grokModel;
    @Value("${xincronix.ai.openai.api-key:}") private String openAiApiKey;
    @Value("${xincronix.ai.openai.model:gpt-4o-mini}") private String openAiModel;
    @Value("${xincronix.ai.gemini.api-key:}") private String geminiApiKey;
    @Value("${xincronix.ai.gemini.model:gemini-2.0-flash}") private String geminiModel;
    @Value("${xincronix.ai.anthropic.api-key:}") private String anthropicApiKey;
    @Value("${xincronix.ai.anthropic.model:claude-3-5-haiku-latest}") private String anthropicModel;

    public AiAssistantService(ObjectMapper json, ProyectoRepository proyectos, TareaRepository tareas) {
        this.json = json;
        this.proyectos = proyectos;
        this.tareas = tareas;
        this.httpClient = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).build();
    }

    public Map<String, Object> configuration() {
        List<Map<String, Object>> options = new ArrayList<>();
        options.add(providerInfo("grok", "Grok / xAI", grokModel, hasKey(grokApiKey)));
        options.add(providerInfo("openai", "OpenAI", openAiModel, hasKey(openAiApiKey)));
        options.add(providerInfo("gemini", "Gemini", geminiModel, hasKey(geminiApiKey)));
        options.add(providerInfo("anthropic", "Anthropic", anthropicModel, hasKey(anthropicApiKey)));
        options.add(providerInfo("local", "Modo local", "xincronix-local", true));
        return Map.of("defaultProvider", normalized(configuredProvider), "providers", options);
    }

    public AssistantReply ask(String requestedProvider, String message, List<ChatMessage> history, Usuario user) {
        String provider = resolveProvider(requestedProvider);
        String systemPrompt = systemPrompt(user);
        List<ChatMessage> safeHistory = sanitizeHistory(history);

        if ("local".equals(provider)) {
            return new AssistantReply(localReply(message, user), "Modo local", "xincronix-local", "demo");
        }
        if (!isConfigured(provider)) {
            String messageForUser = "gemini".equals(provider)
                    ? "Gemini aún no está configurado. Agrega GEMINI_API_KEY al archivo .env y reinicia la aplicación."
                    : displayName(provider) + " estará disponible próximamente. Usa Gemini para continuar.";
            throw new ProviderUnavailableException(messageForUser);
        }

        try {
            return switch (provider) {
                case "grok" -> openAiCompatible("grok", "https://api.x.ai/v1/chat/completions", grokApiKey,
                        grokModel, systemPrompt, safeHistory, message);
                case "openai" -> openAiCompatible("openai", "https://api.openai.com/v1/chat/completions", openAiApiKey,
                        openAiModel, systemPrompt, safeHistory, message);
                case "gemini" -> gemini(systemPrompt, safeHistory, message);
                case "anthropic" -> anthropic(systemPrompt, safeHistory, message);
                default -> throw new ProviderUnavailableException("Proveedor de IA no soportado.");
            };
        } catch (IOException | InterruptedException ex) {
            if (ex instanceof InterruptedException) Thread.currentThread().interrupt();
            throw new AssistantProviderException("No fue posible conectar con " + displayName(provider)
                    + ". Revisa la clave, la red y vuelve a intentarlo.");
        }
    }

    private AssistantReply openAiCompatible(String provider, String endpoint, String apiKey, String model, String system, List<ChatMessage> history, String message)
            throws IOException, InterruptedException {
        List<Map<String, String>> messages = new ArrayList<>();
        messages.add(Map.of("role", "system", "content", system));
        for (ChatMessage item : history) messages.add(Map.of("role", item.role(), "content", item.content()));
        messages.add(Map.of("role", "user", "content", message));
        JsonNode body = post(endpoint, Map.of("model", model, "messages", messages, "temperature", temperature),
                Map.of("Authorization", "Bearer " + apiKey));
        String reply = body.at("/choices/0/message/content").asText("").trim();
        if (reply.isEmpty()) throw new AssistantProviderException("El proveedor no devolvió una respuesta utilizable.");
        return new AssistantReply(reply, displayName(provider), model, "api");
    }

    private AssistantReply gemini(String system, List<ChatMessage> history, String message)
            throws IOException, InterruptedException {
        List<Map<String, Object>> contents = new ArrayList<>();
        for (ChatMessage item : history) contents.add(geminiContent(item.role(), item.content()));
        contents.add(geminiContent("user", message));
        String endpoint = "https://generativelanguage.googleapis.com/v1beta/models/" + geminiModel
                + ":generateContent";
        JsonNode body = post(endpoint, Map.of(
                "systemInstruction", Map.of("parts", List.of(Map.of("text", system))),
                "contents", contents,
                "generationConfig", Map.of("temperature", temperature)),
                Map.of("x-goog-api-key", geminiApiKey));
        String reply = body.at("/candidates/0/content/parts/0/text").asText("").trim();
        if (reply.isEmpty()) throw new AssistantProviderException("Gemini no devolvió una respuesta utilizable.");
        return new AssistantReply(reply, "Gemini", geminiModel, "api");
    }

    private AssistantReply anthropic(String system, List<ChatMessage> history, String message)
            throws IOException, InterruptedException {
        List<Map<String, String>> messages = new ArrayList<>();
        for (ChatMessage item : history) messages.add(Map.of("role", item.role(), "content", item.content()));
        messages.add(Map.of("role", "user", "content", message));
        JsonNode body = post("https://api.anthropic.com/v1/messages", Map.of("model", anthropicModel,
                "max_tokens", 1024, "temperature", temperature, "system", system, "messages", messages),
                Map.of("x-api-key", anthropicApiKey, "anthropic-version", "2023-06-01"));
        String reply = body.at("/content/0/text").asText("").trim();
        if (reply.isEmpty()) throw new AssistantProviderException("Anthropic no devolvió una respuesta utilizable.");
        return new AssistantReply(reply, "Anthropic", anthropicModel, "api");
    }

    private JsonNode post(String endpoint, Object body, Map<String, String> headers)
            throws IOException, InterruptedException {
        HttpRequest.Builder request = HttpRequest.newBuilder(URI.create(endpoint))
                .timeout(Duration.ofSeconds(Math.max(10, timeoutSeconds)))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json.writeValueAsString(body)));
        headers.forEach(request::header);
        HttpResponse<String> response = httpClient.send(request.build(), HttpResponse.BodyHandlers.ofString());
        JsonNode payload = readJson(response.body());
        if (response.statusCode() >= 400) {
            String detail = payload.at("/error/message").asText(payload.path("message").asText("Error remoto"));
            throw new AssistantProviderException("El proveedor rechazó la solicitud (" + response.statusCode() + "): " + detail);
        }
        return payload;
    }

    private JsonNode readJson(String value) throws JsonProcessingException { return json.readTree(value); }
    private Map<String, Object> geminiContent(String role, String content) {
        return Map.of("role", "assistant".equals(role) ? "model" : "user", "parts", List.of(Map.of("text", content)));
    }

    private String systemPrompt(Usuario user) {
        String userName = clean(user.getNombres()) + " " + clean(user.getApellidos());
        String company = user.getEmpresa() == null ? "sin empresa asignada" : clean(user.getEmpresa().getNombre());
        List<Proyecto> projects = user.getIdEmpresa() == null ? List.of() : proyectos.findByEmpresaIdEmpresa(user.getIdEmpresa());
        List<Tarea> allTasks = projects.stream().flatMap(project -> tareas.findByProyectoIdProyecto(project.getIdProyecto()).stream())
                .sorted(Comparator.comparing(Tarea::getFechaVencimiento, Comparator.nullsLast(Comparator.naturalOrder()))).limit(30).toList();
        String projectContext = projects.stream().limit(20).map(project -> "- " + clean(project.getNombre()) + " (" + clean(project.getEstado()) + ")")
                .reduce("", (left, right) -> left + "\n" + right);
        String taskContext = allTasks.stream().map(task -> "- " + clean(task.getTitulo()) + " | " + clean(task.getEstado())
                + " | prioridad " + clean(task.getPrioridad()) + " | vence " + (task.getFechaVencimiento() == null ? "sin fecha" : task.getFechaVencimiento()))
                .reduce("", (left, right) -> left + "\n" + right);
        return "Eres Xincronix AI, un asistente de proyectos para " + userName + " de " + company + ". "
                + "Responde siempre en español, con claridad y sin inventar datos. Usa el contexto solo cuando ayude. "
                + "No afirmes que ejecutaste acciones en el sistema; ofrece pasos o borradores.\n\nProyectos:" + projectContext
                + "\n\nTareas:" + taskContext;
    }

    private String localReply(String message, Usuario user) {
        String normalized = message.toLowerCase(Locale.ROOT);
        int projectCount = user.getIdEmpresa() == null ? 0 : proyectos.findByEmpresaIdEmpresa(user.getIdEmpresa()).size();
        if (normalized.contains("prioridad") || normalized.contains("tarea")) {
            return "Estoy en modo local. Encontré " + projectCount + " proyecto(s) disponibles. Para priorizar, revisa primero las tareas vencidas, después las de prioridad alta y finalmente las que vencen esta semana.";
        }
        return "Estoy en modo local y recibí tu consulta: “" + message.trim()
                + "”. Configura Gemini, Grok, OpenAI o Anthropic en .env para obtener una respuesta generativa; mientras tanto puedo orientarte sobre la organización de proyectos y tareas.";
    }

    private List<ChatMessage> sanitizeHistory(List<ChatMessage> history) {
        if (history == null) return List.of();
        return history.stream().filter(item -> item != null && ("user".equals(item.role()) || "assistant".equals(item.role())))
                .filter(item -> item.content() != null && !item.content().isBlank()).map(item -> new ChatMessage(item.role(), item.content().trim()))
                .limit(Math.max(0, maxHistory)).toList();
    }
    private String resolveProvider(String requested) {
        String choice = normalized(requested);
        if (!"auto".equals(choice) && PROVIDERS.contains(choice)) return choice;
        String configured = normalized(configuredProvider);
        return PROVIDERS.contains(configured) && ("local".equals(configured) || isConfigured(configured)) ? configured : "local";
    }
    private boolean isConfigured(String provider) { return switch (provider) {
        case "grok" -> hasKey(grokApiKey); case "openai" -> hasKey(openAiApiKey); case "gemini" -> hasKey(geminiApiKey);
        case "anthropic" -> hasKey(anthropicApiKey); default -> true; }; }
    private Map<String, Object> providerInfo(String id, String name, String model, boolean available) {
        return Map.of("id", id, "name", name, "model", model, "available", available);
    }
    private static boolean hasKey(String value) { return value != null && !value.isBlank(); }
    private static String normalized(String value) { return value == null ? "auto" : value.trim().toLowerCase(Locale.ROOT); }
    private static String clean(String value) { return value == null || value.isBlank() ? "sin dato" : value.replaceAll("[\\r\\n]+", " ").trim(); }
    private static String displayName(String provider) { return switch (provider) {
        case "grok" -> "Grok / xAI"; case "openai" -> "OpenAI"; case "gemini" -> "Gemini"; case "anthropic" -> "Anthropic"; default -> "Modo local"; }; }

    public record ChatMessage(String role, String content) {}
    public record AssistantReply(String reply, String provider, String model, String mode) {}
    public static class ProviderUnavailableException extends RuntimeException { public ProviderUnavailableException(String message) { super(message); } }
    public static class AssistantProviderException extends RuntimeException { public AssistantProviderException(String message) { super(message); } }
}
