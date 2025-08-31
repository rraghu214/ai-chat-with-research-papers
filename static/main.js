async function postJSON(url, data) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return res.json();
}

function appendMsg(role, text) {
  const log = document.getElementById('chat-log');
  const div = document.createElement('div');
  div.className = 'chat-msg';
  const roleSpan = document.createElement('span');
  roleSpan.className = 'role';
  roleSpan.textContent = role === 'user' ? 'You:' : 'Assistant:';
  const textSpan = document.createElement('span');
  textSpan.innerHTML = text;
  div.appendChild(roleSpan);
  div.appendChild(textSpan);
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

function setStatus(msg) {
  const s = document.getElementById('chat-status');
  s.textContent = msg || '';
}

window.addEventListener('DOMContentLoaded', () => {
  const sendBtn = document.getElementById('chat-send');
  const input = document.getElementById('chat-input');
  const urlField = document.getElementById('paper_url');

  if (!sendBtn || !input) return; // no chat section yet

  async function send() {
    const message = input.value.trim();
    if (!message) return;
    appendMsg('user', message);
    input.value = '';
    setStatus('Thinking...');

    try {
      const payload = { paper_url: urlField.value, message };
      const res = await postJSON('/chat', payload);
      if (res.ok) {
        appendMsg('model', res.answer);
        setStatus('');
      } else {
        setStatus(res.error || 'Error');
      }
    } catch (e) {
      setStatus(e.message || 'Network error');
    }
  }

  sendBtn.addEventListener('click', send);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') send();
  });
});