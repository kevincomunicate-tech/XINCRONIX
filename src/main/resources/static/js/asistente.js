(() => {
  const endpoint = '/api/assistant';
  const elements = {
    form: document.querySelector('#assistantForm'), input: document.querySelector('#assistantInput'),
    messages: document.querySelector('#assistantMessages'), send: document.querySelector('#assistantSendBtn'),
    provider: document.querySelector('#providerSelect'), clear: document.querySelector('#assistantClearBtn'),
    label: document.querySelector('#assistantProviderLabel'), mode: document.querySelector('#assistantModeTag'),
    dot: document.querySelector('#assistantStatusDot'), toast: document.querySelector('#assistantToast'),
    toastText: document.querySelector('#assistantToastMessage'), userName: document.querySelector('#assistantUserName'),
    userRole: document.querySelector('#assistantUserRole'), avatar: document.querySelector('#assistantUserAvatar')
  };
  let history = [];
  let providers = [];
  let busy = false;

  function showToast(message, variant = 'primary') {
    elements.toast.className = `toast align-items-center text-bg-${variant} border-0`;
    elements.toastText.textContent = message;
    if (window.bootstrap) bootstrap.Toast.getOrCreateInstance(elements.toast).show();
  }
  function scrollDown() { elements.messages.scrollTop = elements.messages.scrollHeight; }
  function updateComposer() { elements.input.style.height = 'auto'; elements.input.style.height = `${Math.min(elements.input.scrollHeight, 132)}px`; }
  function emptyState() {
    elements.messages.replaceChildren();
    const state = document.createElement('div'); state.className = 'assistant-empty';
    state.innerHTML = '<div class="assistant-empty-icon"><i class="bi bi-stars"></i></div><h2>¿En qué trabajamos hoy?</h2><p>Pregúntame por prioridades, proyectos, tareas o ideas para automatizar el trabajo de tu equipo.</p>';
    elements.messages.append(state);
  }
  function addMessage(role, content, meta = '') {
    const blank = elements.messages.querySelector('.assistant-empty'); if (blank) blank.remove();
    const row = document.createElement('article'); row.className = `assistant-message ${role}`;
    const icon = document.createElement('div'); icon.className = 'assistant-message-avatar';
    icon.innerHTML = role === 'assistant' ? '<i class="bi bi-stars"></i>' : (elements.avatar.textContent || 'TU');
    const body = document.createElement('div');
    const bubble = document.createElement('div'); bubble.className = 'assistant-bubble'; bubble.textContent = content;
    const small = document.createElement('div'); small.className = 'assistant-message-meta'; small.textContent = meta;
    body.append(bubble, small); row.append(icon, body); elements.messages.append(row); scrollDown();
  }
  function addTyping() {
    const row = document.createElement('article'); row.id = 'assistantTyping'; row.className = 'assistant-message assistant';
    row.innerHTML = '<div class="assistant-message-avatar"><i class="bi bi-stars"></i></div><div class="assistant-bubble assistant-typing"><span></span><span></span><span></span></div>';
    elements.messages.append(row); scrollDown();
  }
  function removeTyping() { document.querySelector('#assistantTyping')?.remove(); }
  function setBusy(value) {
    busy = value; elements.send.disabled = value; elements.input.disabled = value;
    elements.dot.classList.toggle('busy', value); elements.dot.classList.toggle('offline', false);
  }
  function currentProvider() { return elements.provider.value || 'gemini'; }
  function updateProviderStatus() {
    const choice = currentProvider(); const provider = providers.find(item => item.id === choice);
    if (provider?.available) {
      elements.label.textContent = `${provider.name} · ${provider.model}`;
      elements.mode.textContent = 'API';
      return;
    }
    elements.label.textContent = choice === 'gemini'
      ? 'Gemini pendiente de configurar'
      : `${provider?.name || choice} estará disponible próximamente`;
    elements.mode.textContent = choice === 'gemini' ? 'SIN CLAVE' : 'PRÓXIMAMENTE';
  }
  async function loadConfiguration() {
    try {
      const response = await fetch(`${endpoint}/config`, { headers: { Accept: 'application/json' } });
      const payload = await response.json(); if (!response.ok || !payload.success) throw new Error(payload.message || 'No se pudo cargar la configuración');
      providers = payload.data.providers || [];
      providers.forEach(item => {
        const option = elements.provider.querySelector(`option[value="${item.id}"]`);
        if (!option) return;
        option.disabled = !item.available;
        option.textContent = item.available ? `${item.name} · activo` : `${item.name} · próximamente`;
      });
      const defaultChoice = payload.data.defaultProvider;
      if (defaultChoice && providers.some(item => item.id === defaultChoice && item.available)) elements.provider.value = defaultChoice;
      const user = payload.data.user;
      if (user) { elements.userName.textContent = user.name; elements.userRole.textContent = user.role; elements.avatar.textContent = user.initials; }
      updateProviderStatus();
    } catch (error) { elements.dot.classList.add('offline'); elements.label.textContent = 'Sin conexión con el asistente'; elements.mode.textContent = 'OFFLINE'; }
  }
  async function send(text) {
    const message = text.trim(); if (!message || busy) return;
    addMessage('user', message, 'Tú · ahora'); history.push({ role: 'user', content: message });
    elements.input.value = ''; updateComposer(); setBusy(true); addTyping();
    try {
      const response = await fetch(`${endpoint}/chat`, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ message, provider: currentProvider(), history: history.slice(-12) }) });
      const payload = await response.json(); if (!response.ok || !payload.success) throw new Error(payload.message || 'No se pudo procesar la consulta.');
      const data = payload.data; removeTyping(); addMessage('assistant', data.reply, `${data.provider} · ${data.model}`); history.push({ role: 'assistant', content: data.reply });
      elements.label.textContent = `${data.provider} · ${data.model}`; elements.mode.textContent = data.mode === 'api' ? 'API' : 'LOCAL';
    } catch (error) { removeTyping(); addMessage('assistant', error.message, 'Error de conexión'); showToast(error.message, 'danger'); }
    finally { setBusy(false); elements.input.focus(); }
  }
  elements.form.addEventListener('submit', event => { event.preventDefault(); send(elements.input.value); });
  elements.input.addEventListener('input', updateComposer);
  elements.input.addEventListener('keydown', event => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); elements.form.requestSubmit(); } });
  elements.provider.addEventListener('change', updateProviderStatus);
  elements.clear.addEventListener('click', () => { history = []; emptyState(); showToast('Conversación limpiada.'); });
  document.querySelectorAll('.assistant-prompt').forEach(button => button.addEventListener('click', () => { elements.input.value = button.dataset.prompt || ''; updateComposer(); elements.input.focus(); }));
  window.cerrarSesionAsistente = () => { window.location.assign('/logout'); };
  emptyState(); updateComposer(); loadConfiguration();
})();
