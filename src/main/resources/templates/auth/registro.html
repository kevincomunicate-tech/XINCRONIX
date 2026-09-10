<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<meta name="csrf-token" content="{{ csrf_token() }}">
<title>Xincronix — Registro empresarial</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap" rel="stylesheet"/>
<style>
:root {
  --ink:      #07101f;
  --navy:     #0d1f3c;
  --cobalt:   #1a3a7c;
  --electric: #2a5bff;
  --sky:      #5b8bff;
  --frost:    #adc6ff;
  --accent:   #ff6b35;
  --gold:     #f0c040;
  --white:    #ffffff;
  --muted:    #6b7a9a;
  --success:  #10b981;
  --warning:  #f59e0b;
  --danger:   #ef4444;
  --border-light: rgba(255,255,255,0.09);
  --border-input: rgba(255,255,255,0.14);
}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
html,body{font-family:'DM Sans',sans-serif;background:var(--ink);color:var(--white);}

/* ── LAYOUT ── */
.reg-page{display:grid;grid-template-columns:380px 1fr;min-height:100vh;}

/* ── SIDEBAR ── */
.reg-sidebar{
  background:linear-gradient(160deg,var(--navy) 0%,#050e1c 100%);
  padding:44px 36px;display:flex;flex-direction:column;gap:32px;
  position:sticky;top:0;height:100vh;overflow-y:auto;
  border-right:1px solid var(--border-light);
}
.sidebar-grid{
  position:absolute;inset:0;
  background-image:
    linear-gradient(rgba(42,91,255,0.06) 1px,transparent 1px),
    linear-gradient(90deg,rgba(42,91,255,0.06) 1px,transparent 1px);
  background-size:44px 44px;
  mask-image:radial-gradient(ellipse 80% 80% at 50% 50%,black 30%,transparent 100%);
}
.sidebar-glow{
  position:absolute;width:400px;height:400px;border-radius:50%;
  background:radial-gradient(circle,rgba(42,91,255,0.15) 0%,transparent 65%);
  top:-100px;left:-100px;pointer-events:none;
  animation:breathe 7s ease-in-out infinite;
}
@keyframes breathe{0%,100%{transform:scale(1);}50%{transform:scale(1.08);}}

.s-logo{position:relative;z-index:1;display:flex;align-items:center;gap:10px;}
.s-logo-icon{
  width:38px;height:38px;border-radius:9px;
  background:rgba(42,91,255,0.2);border:1px solid rgba(42,91,255,0.3);
  display:flex;align-items:center;justify-content:center;
  font-family:'Syne',sans-serif;font-size:15px;font-weight:800;color:var(--sky);
}
.s-logo-text{font-family:'Syne',sans-serif;font-size:20px;font-weight:800;color:var(--white);letter-spacing:-0.4px;}
.s-logo-text span{color:var(--sky);}

/* ── STEPPER ── */
.stepper{position:relative;z-index:1;display:flex;flex-direction:column;}
.stepper-label{font-size:10.5px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:rgba(255,255,255,0.3);margin-bottom:16px;}
.step-item{display:flex;gap:14px;align-items:flex-start;padding-bottom:24px;position:relative;}
.step-item:not(:last-child)::after{content:'';position:absolute;left:15px;top:32px;bottom:0;width:1px;background:rgba(255,255,255,0.1);}
.step-item.active::after{background:rgba(42,91,255,0.4);}
.step-item.done::after{background:rgba(16,185,129,0.4);}
.step-num{
  width:32px;height:32px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:12px;font-weight:700;flex-shrink:0;
  background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);
  color:rgba(255,255,255,0.3);transition:all 0.3s;
}
.step-item.active .step-num{background:rgba(42,91,255,0.2);border-color:rgba(42,91,255,0.5);color:var(--sky);box-shadow:0 0 0 4px rgba(42,91,255,0.12);}
.step-item.done .step-num{background:rgba(16,185,129,0.15);border-color:rgba(16,185,129,0.4);color:var(--success);}
.step-name{font-size:13.5px;font-weight:700;color:rgba(255,255,255,0.35);transition:color 0.3s;margin-bottom:3px;}
.step-item.active .step-name{color:var(--white);}
.step-item.done .step-name{color:rgba(255,255,255,0.6);}
.step-desc{font-size:11.5px;color:rgba(255,255,255,0.22);line-height:1.5;}
.step-item.active .step-desc{color:rgba(255,255,255,0.4);}

/* PLAN CARD */
.plan-card{position:relative;z-index:1;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:20px;display:none;}
.plan-card.visible{display:block;}
.plan-card-label{font-size:10.5px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:rgba(255,255,255,0.3);margin-bottom:14px;}
.plan-selected{display:flex;align-items:center;gap:12px;}
.plan-icon{width:40px;height:40px;border-radius:10px;background:rgba(42,91,255,0.15);display:flex;align-items:center;justify-content:center;font-size:17px;flex-shrink:0;}
.plan-name{font-family:'Syne',sans-serif;font-size:15px;font-weight:800;color:var(--white);}
.plan-price{font-size:12.5px;color:var(--sky);margin-top:2px;}
.plan-workers-badge{margin-left:auto;background:rgba(42,91,255,0.15);border:1px solid rgba(42,91,255,0.25);border-radius:100px;padding:3px 10px;font-size:11px;font-weight:600;color:var(--frost);}

.sidebar-help{position:relative;z-index:1;background:rgba(42,91,255,0.06);border:1px solid rgba(42,91,255,0.15);border-radius:12px;padding:16px;font-size:12.5px;color:rgba(255,255,255,0.45);line-height:1.6;}
.sidebar-help strong{color:rgba(255,255,255,0.7);display:block;margin-bottom:4px;}
.sidebar-help a{color:var(--sky);text-decoration:none;font-weight:600;}

/* ── MAIN ── */
.reg-main{padding:52px 64px;background:var(--ink);overflow-y:auto;}

/* STEP PANELS */
.step-panel{display:none;animation:fade-up 0.45s ease both;}
.step-panel.active{display:block;}
@keyframes fade-up{from{opacity:0;transform:translateY(18px);}to{opacity:1;transform:translateY(0);}}

.panel-eyebrow{font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--electric);margin-bottom:10px;}
.panel-title{font-family:'Syne',sans-serif;font-size:clamp(22px,3vw,32px);font-weight:800;color:var(--white);margin-bottom:8px;line-height:1.1;}
.panel-sub{font-size:14px;color:var(--muted);margin-bottom:36px;line-height:1.6;max-width:520px;}

/* FORM */
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px;}
.form-row.single{grid-template-columns:1fr;}
.field{margin-bottom:0;}
.field label{display:block;font-size:11.5px;font-weight:600;color:rgba(255,255,255,0.4);letter-spacing:0.5px;text-transform:uppercase;margin-bottom:7px;}
.field-wrap{position:relative;display:flex;align-items:center;}
.field-wrap .fi{position:absolute;left:13px;font-size:14px;color:var(--muted);pointer-events:none;}
.field-wrap input,
.field-wrap select,
.field-wrap textarea{
  width:100%;padding:11px 14px 11px 40px;
  background:rgba(255,255,255,0.05);border:1px solid var(--border-input);
  border-radius:10px;font-size:13.5px;font-family:'DM Sans',sans-serif;
  color:var(--white);transition:all 0.2s;outline:none;
}
.field-wrap select{cursor:pointer;-webkit-appearance:none;}
.field-wrap select option{background:var(--navy);color:var(--white);}
.field-wrap textarea{resize:vertical;min-height:80px;padding-top:12px;}
.field-wrap input::placeholder,.field-wrap textarea::placeholder{color:rgba(255,255,255,0.18);}
.field-wrap input:focus,.field-wrap select:focus,.field-wrap textarea:focus{
  background:rgba(42,91,255,0.07);border-color:rgba(42,91,255,0.45);box-shadow:0 0 0 3px rgba(42,91,255,0.1);
}
/* Error state */
.field-wrap input.error,
.field-wrap select.error,
.field-wrap textarea.error{
  border-color:rgba(239,68,68,0.55) !important;box-shadow:0 0 0 3px rgba(239,68,68,0.08) !important;
}
.field-error{font-size:11.5px;color:var(--danger);margin-top:5px;display:none;}
.field-error.show{display:block;}

/* Indicador de fortaleza de contraseña */
.pwd-strength{margin-top:8px;display:none;}
.pwd-strength.show{display:block;}
.pwd-strength-bar{height:3px;border-radius:2px;background:rgba(255,255,255,0.08);overflow:hidden;margin-bottom:4px;}
.pwd-strength-fill{height:100%;border-radius:2px;transition:all 0.3s;}
.pwd-strength-text{font-size:11px;color:rgba(255,255,255,0.35);}

/* PLAN SELECTOR */
.plan-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:28px;}
.plan-opt{background:rgba(255,255,255,0.03);border:1.5px solid rgba(255,255,255,0.08);border-radius:14px;padding:20px 16px;cursor:pointer;transition:all 0.2s;position:relative;overflow:hidden;}
.plan-opt:hover{background:rgba(42,91,255,0.06);border-color:rgba(42,91,255,0.3);}
.plan-opt.selected{background:rgba(42,91,255,0.1);border-color:rgba(42,91,255,0.55);box-shadow:0 0 0 3px rgba(42,91,255,0.12);}
.plan-opt-popular{position:absolute;top:10px;right:10px;background:var(--electric);color:white;font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;padding:3px 8px;border-radius:100px;}
.plan-opt-name{font-family:'Syne',sans-serif;font-size:15px;font-weight:800;color:var(--white);margin-bottom:4px;}
.plan-opt-price{font-size:12px;color:var(--sky);margin-bottom:10px;}
.plan-opt-workers{font-size:11.5px;color:rgba(255,255,255,0.4);background:rgba(255,255,255,0.05);border-radius:6px;padding:4px 8px;display:inline-block;}
.plan-opt-check{position:absolute;top:12px;left:12px;width:18px;height:18px;border-radius:50%;background:var(--electric);display:none;align-items:center;justify-content:center;font-size:10px;color:white;}
.plan-opt.selected .plan-opt-check{display:flex;}

/* PAYMENT METHODS */
.payment-methods{display:flex;gap:12px;margin-bottom:28px;}
.pay-method{flex:1;padding:14px 16px;background:rgba(255,255,255,0.03);border:1.5px solid rgba(255,255,255,0.08);border-radius:12px;cursor:pointer;display:flex;align-items:center;gap:10px;font-size:13px;color:rgba(255,255,255,0.55);transition:all 0.2s;}
.pay-method:hover{background:rgba(42,91,255,0.06);border-color:rgba(42,91,255,0.25);}
.pay-method.selected{background:rgba(42,91,255,0.1);border-color:rgba(42,91,255,0.5);color:var(--white);}
.pay-method-icon{font-size:20px;}
.pay-method-name{font-weight:600;}
.pay-method-sub{font-size:11px;color:rgba(255,255,255,0.3);}

.payment-panel{display:none;}
.payment-panel.active{display:block;}

.transfer-info{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.09);border-radius:14px;padding:22px;margin-bottom:20px;}
.transfer-info-title{font-size:11px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:rgba(255,255,255,0.3);margin-bottom:16px;}
.transfer-row{display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid rgba(255,255,255,0.05);}
.transfer-row:last-child{border-bottom:none;}
.transfer-key{font-size:12.5px;color:rgba(255,255,255,0.4);}
.transfer-val{font-size:13px;font-weight:600;color:var(--white);display:flex;align-items:center;gap:8px;}
.copy-btn{background:rgba(42,91,255,0.15);border:1px solid rgba(42,91,255,0.25);border-radius:6px;padding:2px 8px;font-size:10.5px;color:var(--sky);cursor:pointer;font-family:'DM Sans',sans-serif;font-weight:600;transition:all 0.15s;}
.copy-btn:hover{background:rgba(42,91,255,0.25);}

.nequi-info{text-align:center;padding:28px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:14px;margin-bottom:20px;}
.nequi-qr{width:120px;height:120px;border-radius:12px;background:rgba(255,255,255,0.08);margin:0 auto 14px;display:flex;align-items:center;justify-content:center;font-size:48px;}
.nequi-num{font-size:20px;font-weight:800;color:var(--white);font-family:'Syne',sans-serif;}
.nequi-sub{font-size:12px;color:rgba(255,255,255,0.35);margin-top:4px;}

/* ORDER SUMMARY */
.order-summary{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:20px;margin-bottom:20px;}
.order-title{font-size:11px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:rgba(255,255,255,0.3);margin-bottom:14px;}
.order-row{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);font-size:13px;}
.order-row:last-child{border-bottom:none;padding-bottom:0;}
.order-label{color:rgba(255,255,255,0.5);}
.order-val{font-weight:600;color:var(--white);}
.order-total .order-label{color:var(--white);font-weight:700;font-family:'Syne',sans-serif;}
.order-total .order-val{color:var(--sky);font-size:16px;font-family:'Syne',sans-serif;}

/* VERIFY STATES */
.verify-states{display:flex;flex-direction:column;gap:14px;margin-bottom:28px;}
.verify-state{display:flex;gap:16px;align-items:flex-start;padding:18px 20px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:14px;transition:all 0.3s;}
.verify-state.current{background:rgba(245,158,11,0.06);border-color:rgba(245,158,11,0.25);}
.verify-state.done{background:rgba(16,185,129,0.06);border-color:rgba(16,185,129,0.2);}
.verify-state-icon{font-size:22px;flex-shrink:0;margin-top:2px;}
.verify-state-title{font-size:14px;font-weight:700;color:rgba(255,255,255,0.5);margin-bottom:3px;}
.verify-state.current .verify-state-title{color:var(--white);}
.verify-state-desc{font-size:12.5px;color:rgba(255,255,255,0.25);line-height:1.6;}
.verify-state.current .verify-state-desc{color:rgba(255,255,255,0.45);}
.verify-badge{margin-left:auto;flex-shrink:0;align-self:center;padding:4px 12px;border-radius:100px;font-size:11px;font-weight:700;}
.badge-pending{background:rgba(245,158,11,0.15);color:var(--warning);}
.badge-waiting{background:rgba(107,122,154,0.15);color:var(--muted);}
.badge-done-b{background:rgba(16,185,129,0.15);color:var(--success);}

/* FILE UPLOAD */
.upload-area{border:2px dashed rgba(255,255,255,0.12);border-radius:14px;padding:28px;text-align:center;cursor:pointer;transition:all 0.2s;margin-bottom:20px;background:rgba(255,255,255,0.02);}
.upload-area:hover{border-color:rgba(42,91,255,0.4);background:rgba(42,91,255,0.04);}
.upload-area.dragover{border-color:rgba(42,91,255,0.6);background:rgba(42,91,255,0.08);}
.upload-icon{font-size:36px;margin-bottom:10px;}
.upload-label{font-size:14px;font-weight:600;color:rgba(255,255,255,0.7);margin-bottom:4px;}
.upload-sub{font-size:12px;color:rgba(255,255,255,0.3);}
.upload-preview{display:none;align-items:center;gap:12px;background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.2);border-radius:10px;padding:12px 16px;margin-bottom:16px;}
.upload-preview.visible{display:flex;}
.upload-preview-icon{font-size:20px;}
.upload-preview-name{font-size:13px;font-weight:600;color:var(--white);}
.upload-preview-size{font-size:11px;color:rgba(255,255,255,0.35);}
.upload-remove{margin-left:auto;background:none;border:none;color:rgba(255,255,255,0.3);cursor:pointer;font-size:18px;}
input[type=file]{display:none;}

/* ALERTS */
.alert-info{background:rgba(42,91,255,0.07);border:1px solid rgba(42,91,255,0.2);border-radius:12px;padding:14px 16px;display:flex;align-items:flex-start;gap:12px;font-size:13px;color:rgba(255,255,255,0.6);line-height:1.6;margin-bottom:20px;}
.alert-warn{background:rgba(245,158,11,0.07);border:1px solid rgba(245,158,11,0.2);border-radius:12px;padding:14px 16px;display:flex;align-items:flex-start;gap:12px;font-size:13px;color:rgba(255,255,255,0.6);line-height:1.6;margin-bottom:20px;}
.alert-success{background:rgba(16,185,129,0.07);border:1px solid rgba(16,185,129,0.2);border-radius:12px;padding:14px 16px;display:flex;align-items:flex-start;gap:12px;font-size:13px;color:rgba(255,255,255,0.6);line-height:1.6;margin-bottom:20px;}

/* BUTTONS */
.btn-next{padding:13px 32px;border-radius:10px;font-size:14px;font-weight:700;font-family:'DM Sans',sans-serif;background:var(--electric);color:var(--white);border:none;cursor:pointer;box-shadow:0 0 28px rgba(42,91,255,0.4);transition:all 0.2s;display:inline-flex;align-items:center;gap:8px;}
.btn-next:hover:not(:disabled){background:#3d6aff;transform:translateY(-1px);box-shadow:0 6px 36px rgba(42,91,255,0.55);}
.btn-next:disabled{opacity:0.45;cursor:not-allowed;transform:none;box-shadow:none;}
.btn-next .btn-spinner{width:15px;height:15px;border-radius:50%;border:2px solid rgba(255,255,255,0.3);border-top-color:white;animation:spin 0.7s linear infinite;display:none;}
.btn-next.loading .btn-spinner{display:block;}
.btn-next.loading .btn-label-text{display:none;}
.btn-back{padding:13px 24px;border-radius:10px;font-size:14px;font-weight:600;font-family:'DM Sans',sans-serif;background:transparent;color:rgba(255,255,255,0.5);border:1px solid rgba(255,255,255,0.12);cursor:pointer;transition:all 0.2s;}
.btn-back:hover{background:rgba(255,255,255,0.05);color:var(--white);}
.btn-row{display:flex;gap:12px;margin-top:28px;align-items:center;}

/* SUCCESS */
.success-hero{text-align:center;padding:40px 0;}
.success-icon-wrap{width:96px;height:96px;border-radius:50%;background:rgba(16,185,129,0.1);border:2px solid rgba(16,185,129,0.3);display:flex;align-items:center;justify-content:center;font-size:44px;margin:0 auto 24px;animation:pop 0.5s cubic-bezier(0.34,1.56,0.64,1) both;}
@keyframes pop{from{transform:scale(0.5);opacity:0;}to{transform:scale(1);opacity:1;}}
.success-title{font-family:'Syne',sans-serif;font-size:clamp(24px,3vw,36px);font-weight:800;color:var(--white);margin-bottom:10px;}
.success-sub{font-size:15px;color:rgba(255,255,255,0.45);max-width:440px;margin:0 auto 32px;line-height:1.7;}
.success-steps-card{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:24px;max-width:480px;margin:0 auto 28px;text-align:left;}
.success-steps-title{font-size:11px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:rgba(255,255,255,0.3);margin-bottom:16px;}
.success-step-item{display:flex;align-items:flex-start;gap:12px;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.05);}
.success-step-item:last-child{border-bottom:none;}
.success-step-num{width:22px;height:22px;border-radius:50%;background:rgba(16,185,129,0.15);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:var(--success);flex-shrink:0;margin-top:1px;}
.success-step-text{font-size:13px;color:rgba(255,255,255,0.55);line-height:1.5;}
.success-step-text strong{color:rgba(255,255,255,0.8);}
.btn-portal{display:inline-flex;align-items:center;gap:8px;padding:14px 36px;border-radius:12px;font-size:15px;font-weight:700;font-family:'DM Sans',sans-serif;background:var(--electric);color:var(--white);border:none;cursor:pointer;box-shadow:0 0 36px rgba(42,91,255,0.45);transition:all 0.2s;text-decoration:none;}
.btn-portal:hover{background:#3d6aff;transform:translateY(-2px);box-shadow:0 8px 44px rgba(42,91,255,0.6);}

/* PROGRESS BAR */
.progress-bar-wrap{height:3px;background:rgba(255,255,255,0.06);border-radius:2px;margin-bottom:36px;overflow:hidden;}
.progress-bar-fill{height:100%;background:var(--electric);border-radius:2px;transition:width 0.5s cubic-bezier(0.4,0,0.2,1);}

/* TOAST */
.toast{position:fixed;bottom:28px;right:28px;border-radius:12px;padding:14px 18px;display:flex;align-items:center;gap:12px;font-size:13.5px;font-weight:500;backdrop-filter:blur(10px);transform:translateY(80px);opacity:0;transition:all 0.35s cubic-bezier(0.34,1.56,0.64,1);z-index:999;max-width:360px;box-shadow:0 8px 32px rgba(0,0,0,0.4);}
.toast.show{transform:translateY(0);opacity:1;}
.toast.toast-error{background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);color:#fca5a5;}
.toast.toast-success{background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);color:#6ee7b7;}
.toast.toast-warn{background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.3);color:#fcd34d;}
.toast.toast-info{background:rgba(42,91,255,0.12);border:1px solid rgba(42,91,255,0.3);color:var(--frost);}

@keyframes spin{to{transform:rotate(360deg);}}

@media(max-width:900px){
  .reg-page{grid-template-columns:1fr;}
  .reg-sidebar{display:none;}
  .reg-main{padding:36px 24px;}
  .form-row{grid-template-columns:1fr;}
  .plan-grid{grid-template-columns:1fr;}
  .payment-methods{flex-direction:column;}
}
</style>
</head>
<body>

<div class="reg-page">

  <!-- ══ SIDEBAR ══ -->
  <div class="reg-sidebar" style="position:relative">
    <div class="sidebar-grid"></div>
    <div class="sidebar-glow"></div>

    <div class="s-logo">
      <div class="s-logo-icon"><img src="{{ asset('assets/img/logo xincronix.png') }}" alt="Xincronix" style="width:100%;height:100%;object-fit:contain;"></div>
      <div class="s-logo-text">Xin<span>cronix</span></div>
    </div>

    <div class="stepper">
      <div class="stepper-label">Proceso de registro</div>
      <div class="step-item active" id="stp1">
        <div class="step-num">1</div>
        <div class="step-text"><div class="step-name">Tu empresa</div><div class="step-desc">Datos corporativos básicos</div></div>
      </div>
      <div class="step-item" id="stp2">
        <div class="step-num">2</div>
        <div class="step-text"><div class="step-name">Elige tu plan</div><div class="step-desc">Selecciona el plan adecuado</div></div>
      </div>
      <div class="step-item" id="stp3">
        <div class="step-num">3</div>
        <div class="step-text"><div class="step-name">Pago</div><div class="step-desc">Realiza tu pago seguro</div></div>
      </div>
      <div class="step-item" id="stp4">
        <div class="step-num">4</div>
        <div class="step-text"><div class="step-name">Verificación</div><div class="step-desc">Confirmamos tu pago</div></div>
      </div>
      <div class="step-item" id="stp5">
        <div class="step-num">✓</div>
        <div class="step-text"><div class="step-name">¡Listo!</div><div class="step-desc">Acceso habilitado</div></div>
      </div>
    </div>

    <div class="plan-card" id="planCard">
      <div class="plan-card-label">Plan seleccionado</div>
      <div class="plan-selected">
        <div class="plan-icon" id="pcIcon">🚀</div>
        <div>
          <div class="plan-name" id="pcName">Business</div>
          <div class="plan-price" id="pcPrice">COP 1'990.000/mes</div>
        </div>
        <div class="plan-workers-badge" id="pcWorkers">100 users</div>
      </div>
    </div>

    <div class="sidebar-help">
      <strong>¿Necesitas ayuda?</strong>
      Escríbenos a <a href="mailto:contacto@xincronix.com">contacto@xincronix.com</a> o visita nuestra <a href="#">documentación</a>.
    </div>
  </div>

  <!-- ══ MAIN ══ -->
  <div class="reg-main">

    <div class="progress-bar-wrap">
      <div class="progress-bar-fill" id="progressBar" style="width:20%"></div>
    </div>

    <!-- ─ PASO 1 ─ -->
    <div class="step-panel active" id="panel1">
      <div class="panel-eyebrow">Paso 1 de 4</div>
      <h2 class="panel-title">Cuéntanos sobre<br>tu empresa</h2>
      <p class="panel-sub">Esta información nos permite personalizar tu espacio de trabajo. Solo toma 2 minutos.</p>

      <div class="form-row">
        <div class="field">
          <label>Nombre de la empresa *</label>
          <div class="field-wrap">
            <span class="fi">🏢</span>
            <input type="text" id="companyName" placeholder="Acme S.A.S." maxlength="150"/>
          </div>
          <div class="field-error" id="err-companyName">El nombre de la empresa es obligatorio.</div>
        </div>
        <div class="field">
          <label>NIT / RUT *</label>
          <div class="field-wrap">
            <span class="fi">📋</span>
            <input type="text" id="nit" placeholder="900.123.456-7" maxlength="20"/>
          </div>
          <div class="field-error" id="err-nit">El NIT es obligatorio.</div>
        </div>
      </div>

      <div class="form-row">
        <div class="field">
          <label>Sector de la empresa *</label>
          <div class="field-wrap">
            <span class="fi">🏭</span>
            <select id="sector">
              <option value="" disabled selected>Selecciona un sector</option>
              <option>Tecnología</option><option>Consultoría</option><option>Manufactura</option>
              <option>Salud</option><option>Logística</option><option>Retail</option>
              <option>Educación</option><option>Finanzas</option><option>Otro</option>
            </select>
          </div>
          <div class="field-error" id="err-sector">Selecciona el sector de tu empresa.</div>
        </div>
        <div class="field">
          <label>Número de empleados *</label>
          <div class="field-wrap">
            <span class="fi">👥</span>
            <select id="employees">
              <option value="" disabled selected>Selecciona rango</option>
              <option>1 – 10</option><option>11 – 50</option><option>51 – 100</option>
              <option>101 – 500</option><option>500+</option>
            </select>
          </div>
          <div class="field-error" id="err-employees">Selecciona el rango de empleados.</div>
        </div>
      </div>

      <div class="form-row">
        <div class="field">
          <label>Nombre completo del administrador *</label>
          <div class="field-wrap">
            <span class="fi">👤</span>
            <input type="text" id="adminName" placeholder="María García López" maxlength="100"/>
          </div>
          <div class="field-error" id="err-adminName">El nombre es obligatorio.</div>
        </div>
        <div class="field">
          <label>Cargo *</label>
          <div class="field-wrap">
            <span class="fi">💼</span>
            <input type="text" id="adminRole" placeholder="CEO / Director de TI" maxlength="80"/>
          </div>
          <div class="field-error" id="err-adminRole">El cargo es obligatorio.</div>
        </div>
      </div>

      <div class="form-row">
        <div class="field">
          <label>Correo corporativo *</label>
          <div class="field-wrap">
            <span class="fi">✉</span>
            <input type="email" id="adminEmail" placeholder="admin@empresa.com" maxlength="150"/>
          </div>
          <div class="field-error" id="err-adminEmail">Ingresa un correo electrónico válido.</div>
        </div>
        <div class="field">
          <label>Teléfono *</label>
          <div class="field-wrap">
            <span class="fi">📞</span>
            <input type="tel" id="adminPhone" placeholder="+57 300 123 4567" maxlength="20"/>
          </div>
          <div class="field-error" id="err-adminPhone">El teléfono es obligatorio.</div>
        </div>
      </div>

      <div class="form-row single" style="margin-bottom:0">
        <div class="field">
          <label>Contraseña *</label>
          <div class="field-wrap">
            <span class="fi">🔒</span>
            <input type="password" id="regPwd" placeholder="Mínimo 8 caracteres" style="padding-right:44px"/>
            <button type="button" class="toggle-pwd" id="toggleRegPwd" style="position:absolute;right:12px;background:none;border:none;cursor:pointer;color:var(--muted);font-size:14px;">👁</button>
          </div>
          <div class="field-error" id="err-regPwd">La contraseña debe tener mínimo 8 caracteres.</div>
          <!-- Indicador de fortaleza -->
          <div class="pwd-strength" id="pwdStrength">
            <div class="pwd-strength-bar"><div class="pwd-strength-fill" id="pwdFill"></div></div>
            <div class="pwd-strength-text" id="pwdStrengthText">Escribe tu contraseña</div>
          </div>
        </div>
      </div>

      <div class="btn-row">
        <button class="btn-next" onclick="goStep(2)">
          <div class="btn-spinner"></div>
          <span class="btn-label-text">Continuar → Elegir plan</span>
        </button>
        <span style="font-size:12px;color:var(--muted);">
          ¿Ya tienes cuenta? <a href="{{ route('login') }}" style="color:var(--sky);font-weight:600;text-decoration:none;">Inicia sesión</a>
        </span>
      </div>
    </div>

    <!-- ─ PASO 2: PLAN ─ -->
    <div class="step-panel" id="panel2">
      <div class="panel-eyebrow">Paso 2 de 4</div>
      <h2 class="panel-title">Elige tu plan<br>empresarial</h2>
      <p class="panel-sub">Selecciona el plan que mejor se adapta al tamaño y necesidades de tu empresa. Puedes cambiar de plan en cualquier momento.</p>

      <div class="plan-grid">
        <div class="plan-opt" onclick="selectPlan(this,'starter')">
          <div class="plan-opt-check">✓</div>
          <div class="plan-opt-name">Starter</div>
          <div class="plan-opt-price">COP 599.000/mes</div>
          <div class="plan-opt-workers">👥 Hasta 10 trabajadores</div>
        </div>
        <div class="plan-opt selected" onclick="selectPlan(this,'business')">
          <div class="plan-opt-popular">Más popular</div>
          <div class="plan-opt-check">✓</div>
          <div class="plan-opt-name">Business</div>
          <div class="plan-opt-price">COP 1'990.000/mes</div>
          <div class="plan-opt-workers">👥 Hasta 100 trabajadores</div>
        </div>
        <div class="plan-opt" onclick="selectPlan(this,'enterprise')">
          <div class="plan-opt-check">✓</div>
          <div class="plan-opt-name">Enterprise</div>
          <div class="plan-opt-price">Cotizar</div>
          <div class="plan-opt-workers">👥 +100 sin tope</div>
        </div>
      </div>

      <div class="alert-info">
        <span style="font-size:18px;flex-shrink:0">ℹ️</span>
        <div>La facturación es <strong style="color:rgba(255,255,255,0.8)">anual</strong>. El pago inicial corresponde a 12 meses. Recibirás acceso completo inmediatamente después de confirmar el pago.</div>
      </div>

      <div class="order-summary">
        <div class="order-title">Resumen del pedido</div>
        <div class="order-row"><span class="order-label">Plan seleccionado</span><span class="order-val" id="sumPlan">Business</span></div>
        <div class="order-row"><span class="order-label">Facturación</span><span class="order-val">Anual (12 meses)</span></div>
        <div class="order-row"><span class="order-label">Subtotal</span><span class="order-val" id="sumSubtotal">COP 23'880.000</span></div>
        <div class="order-row"><span class="order-label">IVA (19%)</span><span class="order-val" id="sumTax">COP 4'537.200</span></div>
        <div class="order-row order-total"><span class="order-label">Total a pagar</span><span class="order-val" id="sumTotal">COP 28'417.200</span></div>
      </div>

      <div class="btn-row">
        <button class="btn-back" onclick="goStep(1)">← Volver</button>
        <button class="btn-next" onclick="goStep(3)">
          <div class="btn-spinner"></div>
          <span class="btn-label-text">Continuar → Pago</span>
        </button>
      </div>
    </div>

    <!-- ─ PASO 3: PAGO ─ -->
    <div class="step-panel" id="panel3">
      <div class="panel-eyebrow">Paso 3 de 4</div>
      <h2 class="panel-title">Realiza tu pago</h2>
      <p class="panel-sub">Elige tu método de pago preferido. Una vez realizado el pago, nuestro equipo verificará la transacción en máximo 24 horas hábiles.</p>

      <div class="payment-methods">
        <div class="pay-method selected" onclick="selectPayMethod(this,'transfer')">
          <span class="pay-method-icon">🏦</span>
          <div><div class="pay-method-name">Transferencia</div><div class="pay-method-sub">Bancaria / PSE</div></div>
        </div>
        <div class="pay-method" onclick="selectPayMethod(this,'nequi')">
          <span class="pay-method-icon">📱</span>
          <div><div class="pay-method-name">Nequi</div><div class="pay-method-sub">Pago rápido</div></div>
        </div>
        <div class="pay-method" onclick="selectPayMethod(this,'card')">
          <span class="pay-method-icon">💳</span>
          <div><div class="pay-method-name">Tarjeta</div><div class="pay-method-sub">Crédito / débito</div></div>
        </div>
      </div>

      <!-- Transferencia -->
      <div class="payment-panel active" id="pay-transfer">
        <div class="transfer-info">
          <div class="transfer-info-title">Datos bancarios para transferencia</div>
          <div class="transfer-row"><span class="transfer-key">Banco</span><span class="transfer-val">Bancolombia</span></div>
          <div class="transfer-row"><span class="transfer-key">Tipo de cuenta</span><span class="transfer-val">Cuenta Corriente</span></div>
          <div class="transfer-row">
            <span class="transfer-key">Número de cuenta</span>
            <span class="transfer-val">123-456789-00<button class="copy-btn" onclick="copyText('123-456789-00')">Copiar</button></span>
          </div>
          <div class="transfer-row">
            <span class="transfer-key">NIT titular</span>
            <span class="transfer-val">900.XXX.XXX-X<button class="copy-btn" onclick="copyText('900.XXX.XXX-X')">Copiar</button></span>
          </div>
          <div class="transfer-row"><span class="transfer-key">Titular</span><span class="transfer-val">Xincronix SAS</span></div>
          <div class="transfer-row">
            <span class="transfer-key">Concepto</span>
            <span class="transfer-val" id="payRef">XNX-XXXXX <button class="copy-btn" onclick="copyRef()">Copiar</button></span>
          </div>
          <div class="transfer-row">
            <span class="transfer-key">Monto a pagar</span>
            <span class="transfer-val" style="color:var(--sky)" id="payAmount">COP 28'417.200</span>
          </div>
        </div>
        <div class="alert-warn">
          <span style="font-size:18px;flex-shrink:0">⚠️</span>
          <div>Usa el <strong style="color:rgba(255,255,255,0.8)">concepto de pago exacto</strong> para que podamos identificar tu transacción automáticamente.</div>
        </div>
      </div>

      <!-- Nequi -->
      <div class="payment-panel" id="pay-nequi">
        <div class="nequi-info">
          <div class="nequi-qr">📱</div>
          <div class="nequi-num">+57 300 XXX XXXX</div>
          <div class="nequi-sub">Número Nequi de Xincronix SAS</div>
        </div>
        <div class="alert-info">
          <span style="font-size:18px;flex-shrink:0">ℹ️</span>
          <div>En el mensaje escribe tu <strong style="color:rgba(255,255,255,0.8)">referencia de pago</strong>: <span style="color:var(--sky);font-weight:700" id="nequiRef">XNX-XXXXX</span></div>
        </div>
      </div>

      <!-- Tarjeta -->
      <div class="payment-panel" id="pay-card">
        <div class="alert-info" style="margin-bottom:16px;">
          <span style="font-size:18px;flex-shrink:0">🔒</span>
          <div>Los pagos con tarjeta se procesan de forma segura vía <strong style="color:rgba(255,255,255,0.8)">PayU / Wompi</strong>.</div>
        </div>
        <div class="order-summary" style="margin-bottom:0">
          <div class="order-title">Resumen</div>
          <div class="order-row"><span class="order-label">Plan</span><span class="order-val" id="cardSumPlan">Business</span></div>
          <div class="order-row order-total"><span class="order-label">Total</span><span class="order-val" id="cardSumTotal">COP 28'417.200</span></div>
        </div>
      </div>

      <div class="btn-row">
        <button class="btn-back" onclick="goStep(2)">← Volver</button>
        <button class="btn-next" onclick="goStep(4)">
          <div class="btn-spinner"></div>
          <span class="btn-label-text">Ya pagué — Enviar comprobante →</span>
        </button>
      </div>
    </div>

    <!-- ─ PASO 4: VERIFICACIÓN ─ -->
    <div class="step-panel" id="panel4">
      <div class="panel-eyebrow">Paso 4 de 4</div>
      <h2 class="panel-title">Envía tu comprobante<br>de pago</h2>
      <p class="panel-sub">Para activar tu cuenta necesitamos verificar tu pago. Adjunta el comprobante y lo revisaremos en máximo <strong style="color:var(--white)">24 horas hábiles</strong>.</p>

      <div class="verify-states">
        <div class="verify-state current">
          <span class="verify-state-icon">📤</span>
          <div><div class="verify-state-title">Envío del comprobante</div><div class="verify-state-desc">Adjunta tu captura de pantalla, PDF o foto del recibo.</div></div>
          <div class="verify-badge badge-pending">En curso</div>
        </div>
        <div class="verify-state">
          <span class="verify-state-icon">🔍</span>
          <div><div class="verify-state-title">Revisión por nuestro equipo</div><div class="verify-state-desc">Verificamos monto, referencia y datos de tu empresa.</div></div>
          <div class="verify-badge badge-waiting">Pendiente</div>
        </div>
        <div class="verify-state">
          <span class="verify-state-icon">✅</span>
          <div><div class="verify-state-title">Activación de tu cuenta</div><div class="verify-state-desc">Recibirás un correo con tus credenciales de acceso.</div></div>
          <div class="verify-badge badge-waiting">Pendiente</div>
        </div>
      </div>

      <div class="upload-area" id="uploadArea"
           onclick="document.getElementById('fileInput').click()"
           ondragover="event.preventDefault();this.classList.add('dragover')"
           ondragleave="this.classList.remove('dragover')"
           ondrop="handleDrop(event)">
        <div class="upload-icon">📎</div>
        <div class="upload-label">Arrastra tu comprobante aquí</div>
        <div class="upload-sub">o haz clic para seleccionar · PDF, PNG, JPG — máx. 10 MB</div>
        <input type="file" id="fileInput" accept=".pdf,.png,.jpg,.jpeg" onchange="handleFile(this.files)"/>
      </div>

      <div class="upload-preview" id="uploadPreview">
        <span class="upload-preview-icon">📄</span>
        <div>
          <div class="upload-preview-name" id="uploadName">comprobante.pdf</div>
          <div class="upload-preview-size" id="uploadSize">1.2 MB</div>
        </div>
        <button class="upload-remove" onclick="removeFile()" title="Eliminar">×</button>
      </div>

      <div class="form-row single" style="margin-bottom:16px;">
        <div class="field">
          <label>Notas adicionales (opcional)</label>
          <div class="field-wrap">
            <span class="fi" style="top:14px">📝</span>
            <textarea id="payNotes" placeholder="Ej: Transferencia realizada el 9 de abril desde Bancolombia, referencia 98765…" style="padding-left:40px"></textarea>
          </div>
        </div>
      </div>

      <div class="alert-info">
        <span style="font-size:18px;flex-shrink:0">📧</span>
        <div>Te notificaremos a <strong style="color:rgba(255,255,255,0.8)" id="notifyEmail">tu correo corporativo</strong> cuando tu pago sea confirmado.</div>
      </div>

      <div class="btn-row">
        <button class="btn-back" onclick="goStep(3)">← Volver</button>
        <button class="btn-next" id="btnSend" onclick="submitRegistration()" disabled>
          <div class="btn-spinner"></div>
          <span class="btn-label-text">Enviar comprobante ✓</span>
        </button>
      </div>
    </div>

    <!-- ─ PASO 5: ÉXITO ─ -->
    <div class="step-panel" id="panel5">
      <div class="success-hero">
        <div class="success-icon-wrap">🎉</div>
        <h2 class="success-title">¡Solicitud enviada<br>con éxito!</h2>
        <p class="success-sub">Hemos recibido tu comprobante de pago. Nuestro equipo lo revisará y activará tu acceso en máximo 24 horas hábiles.</p>

        <div class="success-steps-card">
          <div class="success-steps-title">¿Qué sigue?</div>
          <div class="success-step-item">
            <div class="success-step-num">1</div>
            <div class="success-step-text">Recibirás un <strong>correo de confirmación</strong> en los próximos minutos con el número de tu solicitud.</div>
          </div>
          <div class="success-step-item">
            <div class="success-step-num">2</div>
            <div class="success-step-text">Nuestro equipo <strong>verificará tu pago</strong> en máximo 24 horas hábiles (lunes a viernes).</div>
          </div>
          <div class="success-step-item">
            <div class="success-step-num">3</div>
            <div class="success-step-text">Recibirás un correo con tus <strong>credenciales de acceso</strong> y el enlace a tu panel de control.</div>
          </div>
          <div class="success-step-item">
            <div class="success-step-num">4</div>
            <div class="success-step-text">Un <strong>consultor de onboarding</strong> se pondrá en contacto para guiarte en la configuración inicial.</div>
          </div>
        </div>

        <a href="{{ route('login') }}" class="btn-portal">Ir al inicio de sesión →</a>
        <div style="margin-top:20px;font-size:12.5px;color:var(--muted);">
          ¿Tienes dudas? <a href="mailto:contacto@xincronix.com" style="color:var(--sky);text-decoration:none;font-weight:600;">contacto@xincronix.com</a>
        </div>
      </div>
    </div>

  </div><!-- /reg-main -->
</div><!-- /reg-page -->

<!-- Toast -->
<div class="toast" id="toast">
  <span id="toastIcon">✅</span>
  <span id="toastMsg">¡Copiado!</span>
</div>

<script>
const REGISTER_ENDPOINT = '/registro';

/* ─── ESTADO ─── */
let currentStep = 1;
let selectedPlan = 'business';
let selectedPayMethod = 'transfer';
let uploadedFile = null;
let payRef = '';

const plans = {
  starter:    { name:'Starter',    price:"COP 599.000/mes",    workers:'10 users',  subtotal:7188000,  icon:'🌱' },
  business:   { name:'Business',   price:"COP 1'990.000/mes",  workers:'100 users', subtotal:23880000, icon:'🚀' },
  enterprise: { name:'Enterprise', price:'Cotizar',            workers:'+100',      subtotal:null,     icon:'🏢' },
};

function fmt(n){ return n ? 'COP ' + n.toLocaleString('es-CO') : 'Cotizar'; }

/* ════════════════════════════════════════════════
   VALIDACIÓN PASO 1
   ════════════════════════════════════════════════ */
const RULES = {
  companyName: { required: true, label: 'El nombre de la empresa es obligatorio.' },
  nit:         { required: true, label: 'El NIT es obligatorio.' },
  sector:      { required: true, label: 'Selecciona el sector de tu empresa.' },
  employees:   { required: true, label: 'Selecciona el rango de empleados.' },
  adminName:   { required: true, label: 'El nombre del administrador es obligatorio.' },
  adminRole:   { required: true, label: 'El cargo es obligatorio.' },
  adminEmail:  { required: true, email: true, label: 'Ingresa un correo electrónico válido.' },
  adminPhone:  { required: true, label: 'El teléfono es obligatorio.' },
  regPwd:      { required: true, minLen: 8, label: 'La contraseña debe tener mínimo 8 caracteres.' },
};

function isValidEmail(val){ return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val); }

function setFieldError(id, hasError) {
  const el = document.getElementById(id);
  const err = document.getElementById('err-' + id);
  if (!el || !err) return;
  if (hasError) {
    el.classList.add('error');
    err.classList.add('show');
  } else {
    el.classList.remove('error');
    err.classList.remove('show');
  }
}

/* Limpia errores al escribir */
Object.keys(RULES).forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener('input', () => setFieldError(id, false));
});

function validateStep1() {
  let ok = true;
  for (const [id, rule] of Object.entries(RULES)) {
    const el = document.getElementById(id);
    const val = el ? el.value.trim() : '';
    let hasError = false;

    if (rule.required && !val) hasError = true;
    if (!hasError && rule.email && !isValidEmail(val)) hasError = true;
    if (!hasError && rule.minLen && val.length < rule.minLen) hasError = true;

    setFieldError(id, hasError);
    if (hasError) ok = false;
  }
  return ok;
}

/* ════════════════════════════════════════════════
   NAVEGACIÓN ENTRE PASOS
   ════════════════════════════════════════════════ */
function goStep(n) {
  if (n === 2 && !validateStep1()) {
    showToast('Completa todos los campos obligatorios.', 'warn');
    /* Scroll al primer campo con error */
    const firstErr = document.querySelector('#panel1 .error');
    if (firstErr) firstErr.scrollIntoView({ behavior: 'smooth', block: 'center' });
    return;
  }

  document.getElementById('panel' + currentStep).classList.remove('active');
  const prevStp = document.getElementById('stp' + currentStep);
  if (prevStp) {
    prevStp.classList.remove('active');
    if (currentStep < n) prevStp.classList.add('done');
  }

  currentStep = n;

  const panel = document.getElementById('panel' + n);
  if (panel) panel.classList.add('active');
  const stp = document.getElementById('stp' + n);
  if (stp) stp.classList.add('active');

  const pct = {1:20,2:40,3:60,4:80,5:100};
  document.getElementById('progressBar').style.width = (pct[n] ?? 100) + '%';

  if (n >= 2) document.getElementById('planCard').classList.add('visible');
  updatePlanCard();
  updateSummary();
  if (n === 3) generateRef();

  const em = document.getElementById('adminEmail')?.value;
  if (em) document.getElementById('notifyEmail').textContent = em;

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function selectPlan(el, key) {
  document.querySelectorAll('.plan-opt').forEach(p => p.classList.remove('selected'));
  el.classList.add('selected');
  selectedPlan = key;
  updatePlanCard();
  updateSummary();
}

function updatePlanCard() {
  const p = plans[selectedPlan];
  document.getElementById('pcIcon').textContent    = p.icon;
  document.getElementById('pcName').textContent    = p.name;
  document.getElementById('pcPrice').textContent   = p.price;
  document.getElementById('pcWorkers').textContent = p.workers;
}

function updateSummary() {
  const p = plans[selectedPlan];
  document.getElementById('sumPlan').textContent     = p.name;
  document.getElementById('cardSumPlan').textContent = p.name;
  if (p.subtotal) {
    const tax   = Math.round(p.subtotal * 0.19);
    const total = p.subtotal + tax;
    document.getElementById('sumSubtotal').textContent  = fmt(p.subtotal);
    document.getElementById('sumTax').textContent       = fmt(tax);
    document.getElementById('sumTotal').textContent     = fmt(total);
    document.getElementById('cardSumTotal').textContent = fmt(total);
    document.getElementById('payAmount').textContent    = fmt(total);
  } else {
    ['sumSubtotal','sumTax','sumTotal','cardSumTotal','payAmount'].forEach(id => {
      document.getElementById(id).textContent = 'A cotizar';
    });
  }
}

function selectPayMethod(el, method) {
  document.querySelectorAll('.pay-method').forEach(m => m.classList.remove('selected'));
  el.classList.add('selected');
  selectedPayMethod = method;
  document.querySelectorAll('.payment-panel').forEach(p => p.classList.remove('active'));
  document.getElementById('pay-' + method).classList.add('active');
}

/* ════════════════════════════════════════════════
   REFERENCIA DE PAGO
   ════════════════════════════════════════════════ */
function generateRef() {
  payRef = 'XNX-' + Math.random().toString(36).substr(2, 6).toUpperCase();
  const refEl = document.getElementById('payRef');
  if (refEl) refEl.innerHTML = payRef + ' <button class="copy-btn" onclick="copyRef()">Copiar</button>';
  const nEl = document.getElementById('nequiRef');
  if (nEl) nEl.textContent = payRef;
}

/* ════════════════════════════════════════════════
   FILE UPLOAD
   ════════════════════════════════════════════════ */
function handleFile(files) {
  if (!files || !files[0]) return;
  const file = files[0];
  const allowed = ['application/pdf', 'image/png', 'image/jpeg'];
  if (!allowed.includes(file.type)) {
    showToast('Solo se permiten archivos PDF, PNG o JPG.', 'error'); return;
  }
  if (file.size > 10 * 1024 * 1024) {
    showToast('El archivo supera los 10 MB.', 'error'); return;
  }
  uploadedFile = file;
  document.getElementById('uploadName').textContent = file.name;
  document.getElementById('uploadSize').textContent = (file.size / 1024 / 1024).toFixed(2) + ' MB';
  document.getElementById('uploadPreview').classList.add('visible');
  document.getElementById('uploadArea').style.display = 'none';
  document.getElementById('btnSend').disabled = false;
  showToast('Comprobante cargado correctamente.', 'success');
}

function handleDrop(e) {
  e.preventDefault();
  document.getElementById('uploadArea').classList.remove('dragover');
  handleFile(e.dataTransfer.files);
}

function removeFile() {
  uploadedFile = null;
  document.getElementById('uploadPreview').classList.remove('visible');
  document.getElementById('uploadArea').style.display = '';
  document.getElementById('btnSend').disabled = true;
  document.getElementById('fileInput').value = '';
}

async function submitRegistration() {
  if (!uploadedFile) {
    showToast('Adjunta tu comprobante de pago.', 'warn'); return;
  }

  const btn = document.getElementById('btnSend');
  btn.classList.add('loading');
  btn.disabled = true;

  /* Construimos FormData con TODOS los campos del formulario */
  const fd = new FormData();
  fd.append('nombre', document.getElementById('companyName').value.trim());
  fd.append('nit',            document.getElementById('nit').value.trim());
  fd.append('sector',         document.getElementById('sector').value);
  fd.append('num_empleados',  document.getElementById('employees').value);
  fd.append('nombres',        document.getElementById('adminName').value.trim().split(' ').slice(0, -1).join(' ') || document.getElementById('adminName').value.trim());
  fd.append('apellidos',      document.getElementById('adminName').value.trim().split(' ').slice(-1)[0] || '');
  fd.append('cargo',          document.getElementById('adminRole').value.trim());
  fd.append('email',          document.getElementById('adminEmail').value.trim());
  fd.append('telefono',       document.getElementById('adminPhone').value.trim());
  fd.append('password',       document.getElementById('regPwd').value);
  fd.append('plan',           selectedPlan);
  fd.append('metodo_pago',    selectedPayMethod);
  fd.append('referencia',     payRef);
  fd.append('notas',          document.getElementById('payNotes').value.trim());
  fd.append('comprobante',    uploadedFile, uploadedFile.name);

  try {
    const response = await fetch('/registro', { 
        method: 'POST', 
        body: fd,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
        }
    });

    const data = await response.json(); 

    if (response.ok) {
        // Código de éxito original
        document.getElementById('stp4').classList.remove('active');
        document.getElementById('stp4').classList.add('done');
        document.getElementById('panel4').classList.remove('active');
        currentStep = 5;
        document.getElementById('panel5').classList.add('active');
        document.getElementById('progressBar').style.width = '100%';
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
        // Si hay error de validación (422)
        console.error("Detalles del error:", data.errors);
        showToast(data.message || 'Error en el formulario', 'error');
        btn.classList.remove('loading');
        btn.disabled = false;
    }
} catch (err) {
    console.error("Error en la petición:", err);
    showToast('Error de conexión. Inténtalo de nuevo.', 'error');
    btn.classList.remove('loading');
    btn.disabled = false;
}
}

/* ════════════════════════════════════════════════
  COPIAR AL PORTAPAPELES
   ════════════════════════════════════════════════ */
function copyText(t) {
  navigator.clipboard.writeText(t).catch(() => {
    const ta = document.createElement('textarea');
    ta.value = t; document.body.appendChild(ta);
    ta.select(); document.execCommand('copy');
    document.body.removeChild(ta);
  });
  showToast('¡Copiado al portapapeles!', 'success');
}
function copyRef() { copyText(payRef); }

/* ════════════════════════════════════════════════
   TOAST
   ════════════════════════════════════════════════ */
function showToast(msg, type = 'success') {
  const icons = { success:'✅', error:'❌', warn:'⚠️', info:'ℹ️' };
  const t = document.getElementById('toast');
  t.className = `toast toast-${type}`;
  document.getElementById('toastMsg').textContent = msg;
  document.getElementById('toastIcon').textContent = icons[type] ?? 'ℹ️';
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 4000);
}

/* ════════════════════════════════════════════════
  FORTALEZA DE CONTRASEÑA
   ════════════════════════════════════════════════ */
document.getElementById('regPwd').addEventListener('input', function () {
  const val = this.value;
  const strengthEl  = document.getElementById('pwdStrength');
  const fillEl      = document.getElementById('pwdFill');
  const textEl      = document.getElementById('pwdStrengthText');

  if (!val) { strengthEl.classList.remove('show'); return; }
  strengthEl.classList.add('show');

  let score = 0;
  if (val.length >= 8)  score++;
  if (val.length >= 12) score++;
  if (/[A-Z]/.test(val)) score++;
  if (/[0-9]/.test(val)) score++;
  if (/[^A-Za-z0-9]/.test(val)) score++;

  const levels = [
    { pct:'20%', color:'#ef4444', text:'Muy débil'   },
    { pct:'40%', color:'#f59e0b', text:'Débil'        },
    { pct:'60%', color:'#f59e0b', text:'Aceptable'    },
    { pct:'80%', color:'#10b981', text:'Fuerte'       },
    { pct:'100%',color:'#10b981', text:'Muy fuerte'   },
  ];
  const lvl = levels[Math.min(score - 1, 4)] ?? levels[0];
  fillEl.style.width      = lvl.pct;
  fillEl.style.background = lvl.color;
  textEl.textContent      = lvl.text;
  textEl.style.color      = lvl.color;
});

/* ─── Toggle contraseña ─── */
document.getElementById('toggleRegPwd').addEventListener('click', () => {
  const inp = document.getElementById('regPwd');
  const btn = document.getElementById('toggleRegPwd');
  inp.type = inp.type === 'password' ? 'text' : 'password';
  btn.textContent = inp.type === 'password' ? '👁' : '🙈';
});

/* ─── Init ─── */
updatePlanCard();
updateSummary();
generateRef();
</script>
</body>
</html>
