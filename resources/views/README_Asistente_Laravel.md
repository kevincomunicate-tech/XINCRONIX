# Asistente virtual Xincronix

Esta pantalla vive en `view/Asistente.html` y consume `../controller/assistant.php`.

## Variables de entorno

Configura una de estas opciones en `.env`:

```env
XNX_AI_PROVIDER=local
XNX_AI_MAX_HISTORY=12
XNX_AI_TEMPERATURE=0.35
XNX_AI_TIMEOUT=45

GROK_API_KEY=
GROK_MODEL=grok-2-latest

OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-flash

ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-5-haiku-latest
```

`XNX_AI_PROVIDER` acepta `local`, `grok`, `openai`, `gemini` o `anthropic`.

## Contrato HTTP

`POST ../controller/assistant.php`

```json
{
  "message": "Resume mis prioridades del dia",
  "provider": "auto",
  "history": [
    { "role": "user", "content": "Hola" },
    { "role": "assistant", "content": "Hola, soy Xincronix AI." }
  ],
  "context": {
    "page": "Asistente.html",
    "user": {}
  }
}
```

Respuesta:

```json
{
  "success": true,
  "data": {
    "reply": "Texto del asistente",
    "provider": "Modo demo",
    "model": "xincronix-local-demo",
    "mode": "demo"
  }
}
```

## Migracion sugerida a Laravel

1. Mover `config/assistant_config.php` a `config/xincronix_ai.php`.
2. Crear `app/Services/Ai/AssistantService.php` con la logica de `askAssistantProvider`.
3. Crear adaptadores: `OpenAiCompatibleProvider`, `GeminiProvider`, `AnthropicProvider` y `LocalProvider`.
4. Crear `app/Http/Controllers/Api/AssistantController.php` con metodos `config()` y `chat()`.
5. Registrar rutas:

```php
Route::middleware('auth:sanctum')->prefix('assistant')->group(function () {
    Route::get('/config', [AssistantController::class, 'config']);
    Route::post('/chat', [AssistantController::class, 'chat']);
});
```

6. Reemplazar en `Assets/js/asistente.js`:

```js
const ASSISTANT_ENDPOINT = '/api/assistant/chat';
```

Si se separa el frontend, usar `VITE_ASSISTANT_ENDPOINT` para no dejar rutas fijas.
