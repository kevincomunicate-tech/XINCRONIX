<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<meta name="csrf-token" content="{{ csrf_token() }}">
<title>Xincronix — Iniciar sesión</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap" rel="stylesheet"/>
<style>
:root {
  --ink:     #07101f;
  --navy:    #0d1f3c;
  --cobalt:  #1a3a7c;
  --electric:#2a5bff;
  --sky:     #5b8bff;
  --frost:   #adc6ff;
  --accent:  #ff6b35;
  --white:   #ffffff;
  --muted:   #6b7a9a;
  --success: #10b981;
  --warning: #f59e0b;
  --danger:  #ef4444;
  --border-light: rgba(255,255,255,0.09);
  --border-input: rgba(255,255,255,0.14);
}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;font-family:'DM Sans',sans-serif;background:var(--ink);color:var(--white);overflow:hidden;}
@media(max-width:768px){body{overflow:auto;}}

.login-page{display:grid;grid-template-columns:1fr 1fr;min-height:100vh;}

/* PANEL IZQUIERDO */
.login-left{
  background:linear-gradient(145deg,var(--navy) 0%,#050e1c 100%);
  padding:52px 56px;
  display:flex;flex-direction:column;justify-content:space-between;
  position:relative;overflow:hidden;
}
.left-grid{
  position:absolute;inset:0;
  background-image:
    linear-gradient(rgba(42,91,255,0.07) 1px,transparent 1px),
    linear-gradient(90deg,rgba(42,91,255,0.07) 1px,transparent 1px);
  background-size:52px 52px;
  mask-image:radial-gradient(ellipse 80% 80% at 30% 50%,black 30%,transparent 100%);
}
.left-glow{
  position:absolute;width:480px;height:480px;border-radius:50%;
  background:radial-gradient(circle,rgba(42,91,255,0.18) 0%,transparent 65%);
  top:-140px;left:-140px;pointer-events:none;
  animation:breathe 7s ease-in-out infinite;
}
.left-glow2{
  position:absolute;width:340px;height:340px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,107,53,0.1) 0%,transparent 65%);
  bottom:-80px;right:-60px;pointer-events:none;
  animation:breathe 9s ease-in-out infinite reverse;
}
@keyframes breathe{0%,100%{transform:scale(1);}50%{transform:scale(1.07);}}

.left-logo{
  position:relative;z-index:1;
  display:flex;align-items:center;gap:11px;
  animation:fade-up 0.6s ease both;
}
.left-logo-icon{
  width:40px;height:40px;border-radius:10px;
  background:rgba(42,91,255,0.2);border:1px solid rgba(42,91,255,0.35);
  display:flex;align-items:center;justify-content:center;
  font-family:'Syne',sans-serif;font-size:16px;font-weight:800;color:var(--sky);
}
.left-logo-text{font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:var(--white);letter-spacing:-0.5px;}
.left-logo-text span{color:var(--sky);}

.left-middle{position:relative;z-index:1;animation:fade-up 0.6s 0.1s ease both;}
.left-badge{
  display:inline-flex;align-items:center;gap:7px;
  background:rgba(42,91,255,0.15);border:1px solid rgba(42,91,255,0.3);
  padding:5px 13px;border-radius:100px;
  font-size:11.5px;font-weight:600;color:var(--frost);margin-bottom:20px;
}
.left-badge .dot{width:6px;height:6px;border-radius:50%;background:var(--electric);animation:blink 2s infinite;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:0.25;}}
.left-headline{
  font-family:'Syne',sans-serif;font-size:clamp(26px,3.2vw,38px);
  font-weight:800;line-height:1.1;color:var(--white);margin-bottom:18px;
}
.left-headline em{
  font-style:normal;
  background:linear-gradient(135deg,var(--electric),var(--sky));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.left-sub{font-size:14px;color:rgba(255,255,255,0.42);line-height:1.7;max-width:300px;}

.left-features{
  position:relative;z-index:1;
  display:flex;flex-direction:column;gap:11px;
  animation:fade-up 0.6s 0.2s ease both;
}
.left-feature{
  display:flex;align-items:center;gap:12px;
  padding:12px 16px;
  background:rgba(255,255,255,0.03);border:1px solid var(--border-light);
  border-radius:11px;font-size:13px;color:rgba(255,255,255,0.55);transition:all 0.2s;
}
.left-feature:hover{background:rgba(42,91,255,0.08);border-color:rgba(42,91,255,0.2);color:rgba(255,255,255,0.8);}
.left-feature-icon{
  width:30px;height:30px;border-radius:8px;
  background:rgba(42,91,255,0.15);
  display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;
}

.left-stats{position:relative;z-index:1;display:flex;gap:28px;animation:fade-up 0.6s 0.3s ease both;}
.left-stat .num{font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:var(--white);}
.left-stat .lbl{font-size:11px;color:rgba(255,255,255,0.35);margin-top:2px;}

/* PANEL DERECHO */
.login-right{
  background:var(--white);border-left:1px solid var(--ink);
  padding:52px 56px;
  display:flex;flex-direction:column;justify-content:center;
  position:relative;overflow:hidden;
}
.right-glow{
  position:absolute;width:400px;height:400px;border-radius:50%;
  background:radial-gradient(circle,rgba(42,91,255,0.08) 0%,transparent 65%);
  bottom:-120px;right:-120px;pointer-events:none;
}

.form-logo{display:flex;align-items:center;gap:10px;margin-bottom:36px;animation:fade-up 0.5s ease both;}
.form-logo-icon{
  width:36px;height:36px;border-radius:9px;
  background:rgba(42,91,255,0.12);border:1px solid rgba(42,91,255,0.2);
  display:flex;align-items:center;justify-content:center;
  font-family:'Syne',sans-serif;font-size:14px;font-weight:800;color:var(--electric);
}
.form-logo-text{font-family:'Syne',sans-serif;font-size:20px;font-weight:800;color:var(--cobalt);letter-spacing:-0.4px;}
.form-logo-text span{color:var(--ink);}

.form-title{font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:var(--navy);margin-bottom:6px;animation:fade-up 0.5s 0.05s ease both;}
.form-sub{font-size:13.5px;color:var(--navy);margin-bottom:32px;animation:fade-up 0.5s 0.1s ease both;}

/* CAMPOS */
.field{margin-bottom:18px;}
.field label{
  display:block;font-size:12px;font-weight:600;
  color:rgba(0,0,0,0.45);letter-spacing:0.5px;text-transform:uppercase;margin-bottom:7px;
}
.field-wrap{position:relative;display:flex;align-items:center;}
.field-wrap .field-icon{position:absolute;left:14px;font-size:15px;color:var(--ink);pointer-events:none;line-height:1;}
.field-wrap input{
  width:100%;padding:12px 14px 12px 42px;
  background:rgba(255,255,255,0.05);border:1px solid var(--sky);
  border-radius:10px;font-size:14px;font-family:'DM Sans',sans-serif;
  color:var(--navy);transition:all 0.2s;outline:none;
}
.field-wrap input::placeholder{color:rgba(10,10,10,0.35);}
.field-wrap input:focus{
  background:rgba(42,91,255,0.05);
  border-color:rgba(42,91,255,0.5);
  box-shadow:0 0 0 3px rgba(42,91,255,0.12);
}
.field-wrap input.error{border-color:rgba(239,68,68,0.6) !important;box-shadow:0 0 0 3px rgba(239,68,68,0.08);}
.field-error{font-size:11.5px;color:var(--danger);margin-top:5px;display:none;}
.field-error.show{display:block;}
.field-wrap .toggle-pwd{
  position:absolute;right:12px;background:none;border:none;cursor:pointer;
  color:var(--muted);font-size:15px;padding:4px;line-height:1;transition:color 0.2s;
}

.form-options{
  display:flex;align-items:center;justify-content:space-between;margin-bottom:22px;
}
.remember{display:flex;align-items:center;gap:8px;cursor:pointer;font-size:13px;color:var(--cobalt);}
.remember input[type=checkbox]{width:16px;height:16px;border-radius:4px;accent-color:var(--electric);cursor:pointer;}
.forgot{font-size:13px;font-weight:600;color:var(--sky);text-decoration:none;transition:color 0.2s;}
.forgot:hover{color:var(--electric);}

.btn-login{
  width:100%;padding:13px;border-radius:10px;
  font-size:15px;font-weight:700;font-family:'DM Sans',sans-serif;
  background:var(--electric);color:var(--white);border:none;cursor:pointer;
  box-shadow:0 0 32px rgba(42,91,255,0.45);transition:all 0.2s;
  display:flex;align-items:center;justify-content:center;gap:8px;
}
.btn-login:hover:not(:disabled){background:#3d6aff;transform:translateY(-1px);box-shadow:0 6px 40px rgba(42,91,255,0.6);}
.btn-login:disabled{opacity:0.7;cursor:not-allowed;transform:none;}
.spinner{
  width:16px;height:16px;border-radius:50%;
  border:2px solid rgba(255,255,255,0.3);border-top-color:white;
  animation:spin 0.7s linear infinite;display:none;
}
@keyframes spin{to{transform:rotate(360deg);}}
.btn-login.loading .spinner{display:block;}
.btn-login.loading .btn-label{display:none;}

.divider{
  display:flex;align-items:center;gap:12px;margin:20px 0;
  color:var(--electric);font-size:12px;
}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:rgba(42,91,255,0.2);}

.btn-google{
  width:100%;height:46px;
  background:rgba(255,255,255,0.04);border:1px solid rgba(42,91,255,0.25);
  border-radius:10px;font-size:13.5px;font-weight:500;font-family:'DM Sans',sans-serif;
  color:var(--cobalt);cursor:pointer;
  display:flex;align-items:center;justify-content:center;gap:10px;transition:all 0.2s;
}
.btn-google:hover{background:rgba(42,91,255,0.05);border-color:rgba(42,91,255,0.4);}

.form-footer{margin-top:24px;text-align:center;font-size:13px;color:var(--muted);}
.form-footer a{color:var(--sky);font-weight:600;text-decoration:none;}
.form-footer a:hover{color:var(--electric);}

/* TOAST */
.toast{
  position:fixed;top:24px;right:24px;
  border-radius:12px;padding:14px 18px;
  display:flex;align-items:center;gap:12px;
  font-size:13.5px;font-weight:500;
  backdrop-filter:blur(10px);
  transform:translateY(-80px);opacity:0;
  transition:all 0.35s cubic-bezier(0.34,1.56,0.64,1);
  z-index:999;max-width:360px;box-shadow:0 8px 32px rgba(0,0,0,0.3);
}
.toast.show{transform:translateY(0);opacity:1;}
.toast.toast-error{background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.35);color:#fca5a5;}
.toast.toast-success{background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.35);color:#6ee7b7;}
.toast.toast-info{background:rgba(42,91,255,0.12);border:1px solid rgba(42,91,255,0.35);color:var(--frost);}
.toast-icon{font-size:18px;flex-shrink:0;}

@keyframes fade-up{from{opacity:0;transform:translateY(16px);}to{opacity:1;transform:translateY(0);}}

@media(max-width:768px){
  .login-page{grid-template-columns:1fr;}
  .login-left{display:none;}
  .login-right{padding:40px 28px;min-height:100vh;}
  body{overflow:auto;}
}
</style>
</head>
<body>

<div class="login-page">

  {{-- PANEL IZQUIERDO --}}
  <div class="login-left">
    <div class="left-grid"></div>
    <div class="left-glow"></div>
    <div class="left-glow2"></div>

    <div class="left-logo">
      <div class="left-logo-icon">
        <img src="{{ asset('assets/img/logo xincronix.png') }}" alt="Xincronix" style="width:100%;height:100%;object-fit:contain;">
      </div>
      <div class="left-logo-text">Xin<span>cronix</span></div>
    </div>

    <div class="left-middle">
      <div class="left-badge"><span class="dot"></span> Plataforma empresarial · 2026</div>
      <h2 class="left-headline">El sistema nervioso<br>de tu <em>empresa</em></h2>
      <p class="left-sub">Organiza equipos, automatiza procesos y supervisa agentes de IA en un único espacio de trabajo inteligente.</p>
    </div>

    <div class="left-features">
      <div class="left-feature"><div class="left-feature-icon">🤖</div>Gestión multiagente con IA integrada</div>
      <div class="left-feature"><div class="left-feature-icon">📋</div>Control de proyectos en tiempo real</div>
      <div class="left-feature"><div class="left-feature-icon">⚙️</div>Automatización de flujos de trabajo</div>
      <div class="left-feature"><div class="left-feature-icon">📈</div>Analytics e informes inteligentes</div>
    </div>

    <div class="left-stats">
      <div class="left-stat"><div class="num">3×</div><div class="lbl">Productividad media</div></div>
      <div class="left-stat"><div class="num">100%</div><div class="lbl">Empresarial</div></div>
      <div class="left-stat"><div class="num">IA</div><div class="lbl">Agentes nativos</div></div>
    </div>
  </div>

  {{-- PANEL DERECHO --}}
  <div class="login-right">
    <div class="right-glow"></div>

    <div class="form-logo">
      <div class="form-logo-icon">
        <img src="{{ asset('assets/img/logo xincronix.png') }}" alt="Xincronix" style="width:100%;height:100%;object-fit:contain;">
      </div>
      <div class="form-logo-text">Xin<span>cronix</span></div>
    </div>

    <div class="form-title">Bienvenido de vuelta</div>
    <div class="form-sub">Accede a tu espacio de trabajo corporativo</div>

    {{-- Errores de sesión (opcionales, por si usas autenticación web tradicional) --}}
    @if (session('error'))
      <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);color:#fca5a5;padding:10px 14px;border-radius:8px;font-size:13px;margin-bottom:16px;">
        {{ session('error') }}
      </div>
    @endif

    <form id="loginForm" novalidate>
      @csrf

      <div class="field">
        <label for="loginEmail">Correo corporativo *</label>
        <div class="field-wrap">
          <span class="field-icon">✉</span>
          <input type="email" id="loginEmail" name="email"
                 placeholder="tu@empresa.com" autocomplete="email"
                 value="{{ old('email') }}" required/>
        </div>
        <div class="field-error" id="emailError">Ingresa un correo electrónico válido.</div>
      </div>

      <div class="field">
        <label for="loginPassword">Contraseña *</label>
        <div class="field-wrap">
          <span class="field-icon">🔒</span>
          <input type="password" id="loginPassword" name="password"
                 placeholder="••••••••••" autocomplete="current-password" required/>
          <button type="button" class="toggle-pwd" id="togglePwd" title="Ver contraseña">👁</button>
        </div>
        <div class="field-error" id="pwdError">La contraseña debe tener al menos 8 caracteres.</div>
      </div>

      <div class="form-options">
        <label class="remember">
          <input type="checkbox" id="rememberMe" name="remember"/> Recordar sesión
        </label>
        <a href="#" class="forgot" onclick="showToast('Recuperación de contraseña próximamente.','info');return false;">¿Olvidaste tu contraseña?</a>
      </div>

      <button type="submit" class="btn-login" id="btnLogin">
        <div class="spinner"></div>
        <span class="btn-label">Iniciar sesión →</span>
      </button>
    </form>

    <div class="divider">o continúa con</div>

    <button type="button" class="btn-google" id="btnGoogle">
      <svg width="18" height="18" viewBox="0 0 16 16">
        <path fill="#4285F4" d="M15.45 8.18c0-.57-.05-1.11-.14-1.64H8v3.1h4.18a3.57 3.57 0 0 1-1.55 2.34v1.95h2.51c1.47-1.36 2.31-3.35 2.31-5.75Z"/>
        <path fill="#34A853" d="M8 16c2.1 0 3.86-.7 5.15-1.88l-2.51-1.95c-.7.47-1.59.74-2.64.74-2.03 0-3.75-1.37-4.36-3.2H1.05v2.01A7.99 7.99 0 0 0 8 16Z"/>
        <path fill="#FBBC05" d="M3.64 9.71A4.8 4.8 0 0 1 3.39 8c0-.59.1-1.16.25-1.71V4.28H1.05A8 8 0 0 0 0 8c0 1.3.31 2.52.85 3.62l2.8-1.91Z"/>
        <path fill="#EA4335" d="M8 3.18c1.15 0 2.18.4 2.99 1.17l2.24-2.24C11.86.79 10.09 0 8 0A8 8 0 0 0 1.05 4.28l2.59 2.01C4.25 4.55 5.97 3.18 8 3.18Z"/>
      </svg>
      Continuar con Google
    </button>

    <div class="form-footer">
      ¿No tienes cuenta? <a href="{{ url('/registro') }}">Solicitar acceso empresarial →</a>
    </div>
  </div>
</div>

{{-- Toast de notificación --}}
<div class="toast" id="toast">
  <span class="toast-icon" id="toastIcon">⚠️</span>
  <span id="toastMsg">Correo o contraseña incorrectos.</span>
</div>

<script>
const LOGIN_ENDPOINT = '{{ url('/api/login') }}';
const CSRF_TOKEN     = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

/* ─── Toggle contraseña ─── */
document.getElementById('togglePwd').addEventListener('click', () => {
  const inp = document.getElementById('loginPassword');
  const btn = document.getElementById('togglePwd');
  inp.type  = inp.type === 'password' ? 'text' : 'password';
  btn.textContent = inp.type === 'password' ? '👁' : '🙈';
});

/* ─── Toast ─── */
function showToast(msg, type = 'error') {
  const icons = { error: '⚠️', success: '✅', info: 'ℹ️' };
  const t = document.getElementById('toast');
  t.className = `toast toast-${type}`;
  document.getElementById('toastMsg').textContent   = msg;
  document.getElementById('toastIcon').textContent  = icons[type] ?? '⚠️';
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 4000);
}

/* ─── Helpers de validación ─── */
function setError(inputId, errorId, show) {
  const inp = document.getElementById(inputId);
  const err = document.getElementById(errorId);
  if (show) {
    inp.classList.add('error');
    err.classList.add('show');
  } else {
    inp.classList.remove('error');
    err.classList.remove('show');
  }
}

function isValidEmail(val) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);
}

document.getElementById('loginEmail').addEventListener('input',    () => setError('loginEmail',    'emailError', false));
document.getElementById('loginPassword').addEventListener('input', () => setError('loginPassword', 'pwdError',   false));

function validateLogin() {
  const email = document.getElementById('loginEmail').value.trim();
  const pwd   = document.getElementById('loginPassword').value;
  let valid   = true;

  if (!email || !isValidEmail(email)) { setError('loginEmail',    'emailError', true); valid = false; }
  if (!pwd   || pwd.length < 8)       { setError('loginPassword', 'pwdError',   true); valid = false; }
  return valid;
}

/* ─── Submit ─── */
document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  if (!validateLogin()) {
    showToast('Completa los campos correctamente.', 'error');
    return;
  }

  const btn = document.getElementById('btnLogin');
  btn.classList.add('loading');
  btn.disabled = true;

  const formData = new FormData();
  formData.append('email',    document.getElementById('loginEmail').value.trim());
  formData.append('password', document.getElementById('loginPassword').value);
  formData.append('_token',   CSRF_TOKEN);
  if (document.getElementById('rememberMe').checked) {
    formData.append('remember', '1');
  }

  try {
    const res  = await fetch(LOGIN_ENDPOINT, {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRF-TOKEN': CSRF_TOKEN
      },
      credentials: 'include'
    });
    const text = await res.text();

    let data;
    try {
      data = JSON.parse(text);
    } catch {
      console.error('Respuesta no JSON:', text);
      throw new Error('Respuesta inesperada del servidor.');
    }

    if (data.success === true) {
      if (data.data?.token) {
        localStorage.setItem('xincronix_token', data.data.token);
      }
      if (data.data?.usuario) {
        localStorage.setItem('usuarioActual', JSON.stringify(data.data.usuario));
      }

      showToast(data.message || '¡Acceso concedido! Redirigiendo…', 'success');

      setTimeout(() => {
        window.location.href = data.data?.redirect || '{{ url('/Panel') }}';
      }, 1000);

    } else {
      showToast(data.message || 'Correo o contraseña incorrectos.', 'error');
      document.getElementById('loginEmail').classList.add('error');
      document.getElementById('loginPassword').classList.add('error');
    }

  } catch (err) {
    console.error('Error en login:', err);
    showToast(err.message || 'Error de conexión. Inténtalo de nuevo.', 'error');
  } finally {
    btn.classList.remove('loading');
    btn.disabled = false;
  }
});

/* ─── Google (próximamente) ─── */
document.getElementById('btnGoogle').addEventListener('click', () => {
  showToast('Inicio con Google próximamente disponible.', 'info');
});
</script>
</body>
</html>