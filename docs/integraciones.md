# Integraciones de Xincronix

Todas son **opcionales**. Sin configurarlas, Xincronix funciona igual; cada página explica qué falta.
Las claves van en el archivo **`.env`** (en la raíz, junto a `manage.py`), que **no se sube a GitHub**.
Después de cambiar el `.env`, reinicia el servidor (`Ctrl + C` y otra vez `python manage.py runserver`).

| Integración | Variables en `.env` | Dónde se usa |
|---|---|---|
| Inicio de sesión con Google | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | Botón «Continuar con Google» en login y registro |
| Asistente IA (Gemini) | `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_MODEL_RESPALDO`, `GEMINI_LIMITE_POR_HORA` | Proyecto → **Asistente IA** |
| GitHub | `GITHUB_TOKEN` (opcional, se usa para las consultas de administradores) | Proyecto → **Repositorio** |
| Correo real (invitaciones, recuperar contraseña) | `DJANGO_EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` | Invitaciones a proyectos y «¿Olvidaste tu contraseña?» |

> Nunca pegues una clave en un chat, en una captura ni en el código. Si se filtra, bórrala y crea otra.

---

## 1. Inicio de sesión con Google

Usa django-allauth con OAuth de Google. Solo se pide nombre, correo y foto (`openid`, `profile`, `email`); no se guardan tokens de Google.

1. Entra a **https://console.cloud.google.com/** con tu cuenta de Gmail y crea un proyecto (por ejemplo `Xincronix`).
2. Configura la **pantalla de consentimiento de OAuth** (en la consola nueva aparece como «Google Auth Platform»):
   - Tipo de usuario: **Externo**.
   - Nombre de la app y correo de contacto.
   - Mientras esté en modo **Prueba**, agrega tu Gmail (y el de quien vaya a probar) en **Usuarios de prueba**.
3. **Credenciales → Crear credenciales → ID de cliente de OAuth → Aplicación web.**
4. En **URI de redirección autorizados** agrega exactamente:
   ```
   http://127.0.0.1:8000/cuentas/social/google/login/callback/
   ```
   Si entras por `localhost`, agrega también `http://localhost:8000/cuentas/social/google/login/callback/`.
   En producción, la misma ruta con tu dominio y `https://`.
5. Copia el ID y el secreto al `.env`:
   ```
   GOOGLE_CLIENT_ID=xxxxxxxx.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=xxxxxxxx
   ```

Si Google muestra `redirect_uri_mismatch`, la URL del paso 4 no coincide carácter por carácter con la que usas en el navegador.

---

## 2. Asistente IA con Google Gemini

Cada proyecto tiene la sección **Asistente IA**: haces preguntas («resume el avance», «¿qué está atrasado?», «propón las próximas tareas») y responde con los datos de ese proyecto.

1. Entra a **https://aistudio.google.com/** con tu Gmail y crea una **API key**.
2. Pégala en el `.env`:
   ```
   GEMINI_API_KEY=tu-clave
   GEMINI_MODEL=gemini-3.8-flash
   GEMINI_MODEL_RESPALDO=gemini-3.6-flash,gemini-3.5-flash-lite
   GEMINI_LIMITE_POR_HORA=20
   ```
   - `GEMINI_MODEL`: si Google retira el modelo o quieres otro, cámbialo aquí; no hay que tocar el código.
   - `GEMINI_MODEL_RESPALDO`: si el modelo principal responde que está saturado («high demand», error 503), se intenta con estos, en orden (separados por coma).
   - `GEMINI_LIMITE_POR_HORA`: preguntas por persona y por hora, para cuidar la cuota gratuita.

Cómo funciona:
- La clave solo la usa el servidor (`dashboard/gemini.py`) y viaja en un encabezado HTTP; nunca llega al navegador.
- Se envían a Gemini: nombre, descripción, tareas (con responsables y fechas), eventos y correcciones del proyecto. **No** se envían correos, contraseñas ni archivos. La página lo avisa.
- Solo pueden usarlo las personas que ven el proyecto. La conversación se guarda en la sesión (las últimas 6 preguntas) y se borra con «Nueva conversación».
- La respuesta se muestra escapada (no se ejecuta HTML que venga de la IA).

---

## 3. GitHub

Cada proyecto tiene la sección **Repositorio**, que lee el campo «Repositorio o demo» del proyecto:
- `https://github.com/usuario/repo` → descripción, estrellas, forks, issues/PR abiertos, lenguajes y últimos commits.
- `https://github.com/usuario` (o una organización) → lista de sus repositorios públicos; al hacer clic en uno se ven sus datos.

Sin token funciona con **repositorios públicos** (GitHub permite 60 consultas por hora desde una misma IP).
Las respuestas se guardan 10 minutos para no gastar ese límite.

Solo los administradores usan el token del servidor. Para consultar repositorios privados desde una cuenta administradora, crea un token **fine-grained** de **solo lectura**:
1. GitHub → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
2. Elige los repositorios y, en permisos, **Contents: Read-only** y **Metadata: Read-only**.
3. En el `.env`: `GITHUB_TOKEN=github_pat_xxxxx`

---

## 4. Correo real (invitaciones y recuperar contraseña)

Por defecto los correos **se imprimen en la terminal** donde corre `runserver` (no llegan a nadie).
Las invitaciones también aparecen como **notificación** dentro de Xincronix (la campana de la barra superior y el Centro de proyectos), así que funcionan aunque el correo no esté configurado.

Para que lleguen de verdad con **Gmail**:
1. En tu cuenta de Google activa la **verificación en 2 pasos**.
2. Crea una **contraseña de aplicación** (Cuenta de Google → Seguridad → Contraseñas de aplicaciones). Son 16 letras.
3. En el `.env`:
   ```
   DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=tu-correo@gmail.com
   EMAIL_HOST_PASSWORD=la-contraseña-de-aplicación
   DEFAULT_FROM_EMAIL=Xincronix <tu-correo@gmail.com>
   ```

Una cuenta personal de Gmail permite unos 500 correos al día. Si el servidor de correo falla, la invitación igual queda creada como notificación y el líder ve un aviso.

---

## Invitaciones a proyectos

El líder invita desde el proyecto (tarjeta **Equipo**) eligiendo el permiso:
- **Colaborador**: edita tareas, calendario, canvas y documentos.
- **Solo lectura**: solo mira el proyecto.

La persona invitada recibe **las dos cosas**:
1. Un **correo** con el botón «Aceptar invitación».
2. Una **notificación** en Xincronix (campana con contador + tarjeta en el Centro de proyectos) con **Aceptar** y **Rechazar**.

La invitación vence en 7 días. El líder ve las pendientes en la tarjeta Equipo y puede cancelarlas.
