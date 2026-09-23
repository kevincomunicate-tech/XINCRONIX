# Asistente virtual de Xincronix

La pantalla está disponible en `/asistente` y su backend Spring Boot usa los endpoints autenticados:

- `GET /api/assistant/config`: proveedores disponibles y datos del usuario.
- `POST /api/assistant/chat`: consulta al proveedor elegido y agrega al prompt el contexto de proyectos y tareas de la empresa del usuario.

## Configuración

Agrega las variables que necesites al archivo `.env`. Las claves nunca se envían al navegador ni deben subirse al repositorio.

```env
# local, grok, openai, gemini o anthropic
XNX_AI_PROVIDER=gemini
XNX_AI_MAX_HISTORY=12
XNX_AI_TEMPERATURE=0.35
XNX_AI_TIMEOUT=45

GEMINI_API_KEY=pega_aqui_tu_clave_de_google_ai_studio
GEMINI_MODEL=gemini-2.0-flash

# Opcionales: habilitan los otros proveedores en el selector.
GROK_API_KEY=
GROK_MODEL=grok-2-latest
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-5-haiku-latest
```

Reinicia la aplicación después de actualizar `.env`. Gemini queda disponible automáticamente en el selector cuando `GEMINI_API_KEY` tiene valor; si no hay claves, el modo local continúa funcionando para que la pantalla no quede inutilizable.

## Contrato del chat

```json
{
  "message": "Resume mis prioridades del día",
  "provider": "gemini",
  "history": [
    { "role": "user", "content": "Hola" },
    { "role": "assistant", "content": "Hola, soy Xincronix AI." }
  ]
}
```

La respuesta incluye `reply`, `provider`, `model` y `mode`. El servidor genera el contexto del usuario autenticado y no acepta contexto de negocio desde el navegador, evitando que un cliente consulte datos de otra empresa.


cmd
