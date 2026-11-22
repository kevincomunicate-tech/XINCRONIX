# Inicio de sesión con Google

El botón **Continuar con Google** del login y del registro usa
[django-allauth](https://docs.allauth.org/) con el protocolo OAuth 2.0 / OpenID Connect.
Sin credenciales el botón aparece **desactivado** y todo lo demás funciona igual.

## Qué pasa cuando alguien pulsa el botón

1. El navegador envía un formulario **POST**, protegido con CSRF, a `/cuentas/social/google/login/`.
2. allauth lo redirige a Google. Le pasa un `state` y un `code_challenge` (PKCE)
   para que nadie pueda inyectar una respuesta falsa.
3. La persona elige su cuenta de Google y acepta.
4. Google vuelve a `/cuentas/social/google/login/callback/` con un código.
   allauth lo cambia por la identidad verificada: correo, nombres y apellidos.
5. `cuentas/adaptadores.py` aplica nuestras reglas (`config/politica_accesos.json`):
   - **Si el correo ya existe**, entra a esa misma cuenta. El superadministrador
     también puede entrar así.
   - **Si es nuevo**, se crea la cuenta como **Usuario**, sin empresa y sin
     contraseña. Si quiere, después crea una en *Mi cuenta → Crear contraseña*.
6. Cada perfil llega a su inicio: el superadministrador a `/administracion/` y los
   demás a `/app/`.

No se guardan los tokens de Google (`SOCIALACCOUNT_STORE_TOKENS = False`): solo se usa
para iniciar sesión.

## Crear las credenciales (una vez)

Hazlo con tu cuenta de Google en el navegador.

1. Entra a **https://console.cloud.google.com/** y crea un proyecto, por ejemplo `Xincronix`.
2. Abre **Google Auth Platform** (o *APIs y servicios → Pantalla de consentimiento de OAuth*)
   y pulsa **Comenzar**:
   - Nombre de la app: `Xincronix`.
   - Correo de asistencia: el tuyo.
   - Público: **Externo**.
   - Datos de contacto: tu correo. Luego acepta y pulsa **Crear**.
3. En **Público** (*Audience*), mientras la app está "En prueba", agrega como
   **usuarios de prueba** los Gmail que van a entrar: el tuyo y los del equipo.
4. En **Clientes** (*Clients*), pulsa **Crear cliente**:
   - Tipo: **Aplicación web**.
   - **Orígenes autorizados de JavaScript**:
     - `http://127.0.0.1:8000`
     - `http://localhost:8000`
   - **URI de redireccionamiento autorizados** (con la barra final):
     - `http://127.0.0.1:8000/cuentas/social/google/login/callback/`
     - `http://localhost:8000/cuentas/social/google/login/callback/`
5. Pulsa **Crear**. Google muestra el **ID de cliente** y el **Secreto del cliente**.

## Ponerlas en el proyecto

En el archivo `.env`, que nunca se sube a GitHub:

```
GOOGLE_CLIENT_ID=el-id-que-termina-en.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=el-secreto
```

Reinicia `python manage.py runserver`. El botón queda activo.

> No pegues el secreto en el chat, en capturas ni en el código. Si se filtra, en
> Google Cloud entra al cliente, pulsa **Restablecer secreto** y cambia el `.env`.

## Problemas comunes

| Mensaje de Google | Causa | Solución |
|---|---|---|
| `redirect_uri_mismatch` | La URL del navegador no coincide con la registrada (127.0.0.1 ≠ localhost, puerto distinto o falta la `/` final) | Abre el sitio con la misma dirección que registraste, o agrégala en el cliente |
| `access_denied` / "app no verificada" | Tu Gmail no está en usuarios de prueba | Agrégalo en **Público → Usuarios de prueba** |
| "No se pudo iniciar sesión con Google" (página de Xincronix) | La solicitud caducó o el `state` no coincide (por ejemplo, volviste atrás) | Vuelve al login e inténtalo de nuevo |

Para producción agrega el dominio real (`https://tu-dominio/cuentas/social/google/login/callback/`)
y publica la app en **Público → Publicar app**.
