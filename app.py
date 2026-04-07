from flask import Flask, request, jsonify
from agent import get_response

app = Flask(__name__)

@app.route("/")
def home():
    return '''
<html lang="en"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sports Agent</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&amp;family=Syne:wght@400;600;700;800&amp;family=DM+Sans:wght@400;500&amp;display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #0c0c0e;
    --surface: #131316;
    --surface2: #1a1a1f;
    --border: rgba(255,255,255,0.07);
    --border-accent: rgba(255,255,255,0.14);
    --accent: #e8ff47;
    --accent-dim: rgba(232,255,71,0.12);
    --accent-glow: rgba(232,255,71,0.25);
    --text: #f0f0ee;
    --muted: #6b6b72;
    --user-bg: #1e1e24;
    --agent-bg: #131316;
    --mono: 'DM Mono', monospace;
    --sans: 'DM Sans', sans-serif;
    --display: 'Syne', sans-serif;
  }

  html, body {
    height: 100%;
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    font-size: 15px;
    -webkit-font-smoothing: antialiased;
  }

  /* Subtle grid texture */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }

  #app {
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-width: 780px;
    margin: 0 auto;
  }

  /* Header */
  #header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 28px 18px;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }

  .header-left { display: flex; align-items: center; gap: 14px; }

  .logo-mark {
    width: 36px; height: 36px;
    background: var(--accent);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }
  .logo-mark svg { width: 20px; height: 20px; }

  .header-title {
    font-family: var(--display);
    font-size: 18px;
    font-weight: 800;
    letter-spacing: -0.3px;
    color: var(--text);
  }
  .header-sub {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--muted);
    margin-top: 1px;
    letter-spacing: 0.5px;
  }

  .status-pill {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--accent-dim);
    border: 1px solid var(--accent-glow);
    border-radius: 20px;
    padding: 5px 12px;
    font-family: var(--mono);
    font-size: 11px;
    color: var(--accent);
    letter-spacing: 0.3px;
  }
  .status-dot {
    width: 6px; height: 6px;
    background: var(--accent);
    border-radius: 50%;
    animation: blink 2s infinite;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

  /* Messages */
  #chat {
    flex: 1;
    overflow-y: auto;
    padding: 28px 28px 12px;
    display: flex;
    flex-direction: column;
    gap: 0;
    scroll-behavior: smooth;
  }
  #chat::-webkit-scrollbar { width: 3px; }
  #chat::-webkit-scrollbar-thumb { background: var(--border-accent); border-radius: 2px; }

  /* Empty state */
  #empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 24px;
    padding: 40px 20px;
    text-align: center;
  }
  .empty-icon {
    width: 64px; height: 64px;
    background: var(--surface2);
    border: 1px solid var(--border-accent);
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
  }
  .empty-icon svg { width: 30px; height: 30px; opacity: 0.5; }
  .empty-title {
    font-family: var(--display);
    font-size: 22px;
    font-weight: 700;
    color: var(--text);
  }
  .empty-sub {
    font-size: 14px;
    color: var(--muted);
    line-height: 1.6;
    max-width: 320px;
  }
  .suggestion-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    width: 100%;
    max-width: 460px;
  }
  .suggestion {
    background: var(--surface);
    border: 1px solid var(--border-accent);
    border-radius: 10px;
    padding: 12px 14px;
    font-size: 13px;
    color: var(--text);
    cursor: pointer;
    text-align: left;
    font-family: var(--sans);
    line-height: 1.4;
    transition: all 0.15s;
  }
  .suggestion:hover {
    border-color: var(--accent);
    background: var(--accent-dim);
    color: var(--accent);
  }
  .suggestion-label {
    font-family: var(--mono);
    font-size: 10px;
    color: var(--muted);
    margin-bottom: 4px;
    letter-spacing: 0.5px;
  }

  /* Message rows */
  .msg-row {
    display: flex;
    gap: 12px;
    padding: 14px 0;
    border-bottom: 1px solid var(--border);
    animation: fadeUp 0.2s ease;
  }
  .msg-row:last-child { border-bottom: none; }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .msg-row.user { flex-direction: row-reverse; }

  .msg-avatar {
    width: 30px; height: 30px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 500;
    margin-top: 2px;
  }
  .msg-row.user .msg-avatar {
    background: var(--surface2);
    border: 1px solid var(--border-accent);
    color: var(--muted);
  }
  .msg-row.agent .msg-avatar {
    background: var(--accent);
    color: #000;
  }
  .msg-avatar svg { width: 15px; height: 15px; }

  .msg-content { flex: 1; min-width: 0; }
  .msg-label {
    font-family: var(--mono);
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 0.5px;
    margin-bottom: 6px;
  }
  .msg-row.user .msg-label { text-align: right; }

  .msg-bubble {
    display: inline-block;
    max-width: 85%;
    line-height: 1.65;
    font-size: 14.5px;
  }
  .msg-row.user .msg-bubble {
    background: var(--user-bg);
    border: 1px solid var(--border-accent);
    border-radius: 14px 14px 4px 14px;
    padding: 10px 15px;
    float: right;
    color: var(--text);
  }
  .msg-row.agent .msg-bubble {
    color: var(--text);
  }

  /* Markdown inside agent bubbles */
  .msg-bubble p { margin-bottom: 10px; }
  .msg-bubble p:last-child { margin-bottom: 0; }
  .msg-bubble strong { color: var(--accent); font-weight: 500; }
  .msg-bubble code {
    font-family: var(--mono);
    font-size: 12px;
    background: var(--surface2);
    border: 1px solid var(--border-accent);
    padding: 1px 6px;
    border-radius: 4px;
    color: var(--accent);
  }
  .msg-bubble pre {
    background: var(--surface2);
    border: 1px solid var(--border-accent);
    border-radius: 8px;
    padding: 12px;
    overflow-x: auto;
    margin: 10px 0;
  }
  .msg-bubble pre code { background: none; border: none; padding: 0; }
  .msg-bubble ul, .msg-bubble ol { padding-left: 18px; margin-bottom: 10px; }
  .msg-bubble li { margin-bottom: 4px; }
  .msg-bubble h3 {
    font-family: var(--display);
    font-size: 15px;
    font-weight: 700;
    color: var(--accent);
    margin: 12px 0 6px;
  }
  .msg-bubble a { color: var(--accent); text-decoration: underline; text-underline-offset: 3px; }

  .clearfix::after { content: ''; display: table; clear: both; }

  /* Typing */
  .typing-row {
    display: flex;
    gap: 12px;
    padding: 14px 0;
    align-items: flex-start;
  }
  .typing-dots {
    display: flex; gap: 5px; align-items: center;
    padding: 4px 0;
  }
  .typing-dots span {
    width: 6px; height: 6px;
    background: var(--muted);
    border-radius: 50%;
    animation: bounce 1.3s infinite;
  }
  .typing-dots span:nth-child(2) { animation-delay: 0.15s; }
  .typing-dots span:nth-child(3) { animation-delay: 0.3s; }
  @keyframes bounce { 0%,60%,100%{transform:translateY(0);opacity:0.5} 30%{transform:translateY(-5px);opacity:1} }

  /* Input area */
  #input-area {
    padding: 16px 28px 24px;
    flex-shrink: 0;
    border-top: 1px solid var(--border);
  }

  #input-wrap {
    display: flex;
    align-items: flex-end;
    gap: 10px;
    background: var(--surface);
    border: 1px solid var(--border-accent);
    border-radius: 14px;
    padding: 10px 12px 10px 16px;
    transition: border-color 0.15s;
  }
  #input-wrap:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-dim);
  }

  #input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: var(--text);
    font-family: var(--sans);
    font-size: 14px;
    resize: none;
    max-height: 120px;
    overflow-y: auto;
    line-height: 1.5;
    padding: 2px 0;
  }
  #input::placeholder { color: var(--muted); }
  #input::-webkit-scrollbar { width: 2px; }

  #send-btn {
    width: 34px; height: 34px;
    background: var(--accent);
    border: none;
    border-radius: 9px;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    transition: all 0.15s;
  }
  #send-btn:hover { background: #d4e83d; transform: scale(1.05); }
  #send-btn:active { transform: scale(0.95); }
  #send-btn:disabled { background: var(--surface2); cursor: not-allowed; transform: none; }
  #send-btn svg { width: 15px; height: 15px; fill: #000; }

  #footer-hint {
    font-family: var(--mono);
    font-size: 10px;
    color: var(--muted);
    text-align: center;
    margin-top: 10px;
    letter-spacing: 0.3px;
  }
</style>
</head>
<body>
<div id="app">

  <div id="header">
    <div class="header-left">
      <div class="logo-mark">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="10" stroke="#000" stroke-width="2"></circle>
          <path d="M12 2a10 10 0 0 1 0 20" stroke="#000" stroke-width="2"></path>
          <path d="M2 12h20M12 2c-2.5 3-4 6.5-4 10s1.5 7 4 10M12 2c2.5 3 4 6.5 4 10s-1.5 7-4 10" stroke="#000" stroke-width="1.5"></path>
        </svg>
      </div>
      <div>
        <div class="header-title">Sports Agent</div>
        <div class="header-sub">Powered by OpenAI · Web Search</div>
      </div>
    </div>
    <div class="status-pill">
      <span class="status-dot"></span>
      LIVE
    </div>
  </div>

  <div id="chat">
    <div id="empty-state">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"></circle>
          <path d="M12 2a10 10 0 0 1 0 20M2 12h20M12 2c-2.5 3-4 6.5-4 10s1.5 7 4 10"></path>
        </svg>
      </div>
      <div>
        <div class="empty-title">Ask me anything sports</div>
        <div class="empty-sub">Live scores, stats, history, transfers — I've got real-time web access.</div>
      </div>
      <div class="suggestion-grid">
        <button class="suggestion" onclick="suggest(this)">
          <div class="suggestion-label">CRICKET</div>
          Who's leading the IPL 2025 points table?
        </button>
        <button class="suggestion" onclick="suggest(this)">
          <div class="suggestion-label">FOOTBALL</div>
          Latest Champions League results
        </button>
        <button class="suggestion" onclick="suggest(this)">
          <div class="suggestion-label">FORMULA 1</div>
          Current F1 driver standings 2025
        </button>
        <button class="suggestion" onclick="suggest(this)">
          <div class="suggestion-label">DEBATE</div>
          Messi vs Ronaldo — who's the GOAT?
        </button>
      </div>
    </div>
  </div>

  <div id="input-area">
    <div id="input-wrap">
      <textarea id="input" rows="1" placeholder="Ask about scores, stats, players, history..."></textarea>
      <button id="send-btn" onclick="send()" title="Send">
        <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>
      </button>
    </div>
    <div id="footer-hint">Enter to send · Shift+Enter for new line</div>
  </div>

</div>

<script>
  const chatEl = document.getElementById('chat');
  const inputEl = document.getElementById('input');
  const sendBtn = document.getElementById('send-btn');
  const emptyState = document.getElementById('empty-state');
  let isThinking = false;

  function suggest(btn) {
    inputEl.value = btn.textContent.trim().replace(/^[A-Z]+\s*/, '').trim();
    // get just the question (after the label div)
    const label = btn.querySelector('.suggestion-label');
    const fullText = btn.textContent.trim();
    const labelText = label ? label.textContent.trim() : '';
    inputEl.value = fullText.replace(labelText, '').trim();
    send();
  }

  function hideEmpty() {
    if (emptyState && emptyState.parentNode) {
      emptyState.remove();
    }
  }

  function addMsg(role, html) {
    hideEmpty();
    const isUser = role === 'user';
    const row = document.createElement('div');
    row.className = `msg-row ${role}`;

    const avatarHTML = isUser
      ? `<div class="msg-avatar">YOU</div>`
      : `<div class="msg-avatar"><svg viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a10 10 0 0 1 0 20M2 12h20" stroke-width="1.5"/></svg></div>`;

    const label = isUser ? 'YOU' : 'AGENT';
    const bubbleClass = isUser ? 'clearfix' : '';

    row.innerHTML = `
      ${avatarHTML}
      <div class="msg-content">
        <div class="msg-label">${label}</div>
        <div class="${bubbleClass}">
          <div class="msg-bubble">${html}</div>
        </div>
      </div>
    `;
    chatEl.appendChild(row);
    chatEl.scrollTop = chatEl.scrollHeight;
    return row;
  }

  function showTyping() {
    const row = document.createElement('div');
    row.className = 'typing-row';
    row.id = 'typing';
    row.innerHTML = `
      <div class="msg-avatar" style="background:var(--accent);border-radius:8px;width:30px;height:30px;display:flex;align-items:center;justify-content:center;">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a10 10 0 0 1 0 20M2 12h20" stroke-width="1.5"/></svg>
      </div>
      <div class="typing-dots"><span></span><span></span><span></span></div>
    `;
    chatEl.appendChild(row);
    chatEl.scrollTop = chatEl.scrollHeight;
  }

  function removeTyping() {
    const t = document.getElementById('typing');
    if (t) t.remove();
  }

  function escapeHTML(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  async function send() {
    const msg = inputEl.value.trim();
    if (!msg || isThinking) return;

    inputEl.value = '';
    inputEl.style.height = 'auto';
    isThinking = true;
    sendBtn.disabled = true;

    addMsg('user', escapeHTML(msg));
    showTyping();

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
      const data = await res.json();
      removeTyping();
      addMsg('agent', marked.parse(data.reply || "Sorry, I couldn't get a response."));
    } catch(e) {
      removeTyping();
      addMsg('agent', 'Network error — please try again.');
    }

    isThinking = false;
    sendBtn.disabled = false;
    inputEl.focus();
  }

  inputEl.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  });

  inputEl.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
  });
</script>


</body></html>
'''

previous_response_id = None


@app.route("/chat", methods=["POST"])
def chat():
    global previous_response_id
    data = request.json
    user_message = data["message"]
    reply, previous_response_id = get_response(user_message, previous_response_id)
    return jsonify({"reply": reply})


app.run(host="0.0.0.0", port=5000)
