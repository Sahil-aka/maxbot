/* ═══════════════════════════════════════════
   MAX BOT — main.js
   Handles: chat, mike (PTT), wake word SSE,
            quick actions, email modal, modals
═══════════════════════════════════════════ */

// ── State ──────────────────────────────────────────────────────────────────
const CLIENT_ID = 'max_' + Math.random().toString(36).slice(2, 9);
let isListening = false;
let wakeEnabled   = false;
let wakeSource    = null;   // EventSource

// ── DOM refs ──────────────────────────────────────────────────────────────
const chatArea    = document.getElementById('chatArea');
const textInput   = document.getElementById('textInput');
const sendBtn     = document.getElementById('sendBtn');
const micBtn      = document.getElementById('micBtn');
const clearBtn    = document.getElementById('clearBtn');
const wakeToggle  = document.getElementById('wakeToggle');
const statusDot   = document.getElementById('statusDot');
const statusLabel = document.getElementById('statusLabel');

// Modals
const emailBackdrop = document.getElementById('emailBackdrop');
const emailClose    = document.getElementById('emailClose');
const emailCancel   = document.getElementById('emailCancel');
const emailSend     = document.getElementById('emailSend');
const miniBackdrop  = document.getElementById('miniBackdrop');
const miniTitle     = document.getElementById('miniTitle');
const miniInput     = document.getElementById('miniInput');
const miniClose     = document.getElementById('miniClose');
const miniCancel    = document.getElementById('miniCancel');
const miniSubmit    = document.getElementById('miniSubmit');

// ── Status helpers ─────────────────────────────────────────────────────────
function setStatus(state, label) {
  const dot = statusDot;
  dot.className = 'status-dot ' + (state || '');
  statusLabel.textContent = label || 'Ready';
}

function showToast(msg, duration = 3500) {
  let el = document.querySelector('.toast');
  if (!el) {
    el = document.createElement('div');
    el.className = 'toast';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), duration);
}

// ── Chat rendering ─────────────────────────────────────────────────────────
function hideWelcome() {
  const w = document.getElementById('welcomeScreen');
  if (w) w.remove();
}

function scrollToBottom() {
  chatArea.scrollTop = chatArea.scrollHeight;
}

function now() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/** Render a user message bubble */
function addUserMessage(text) {
  hideWelcome();
  const row = document.createElement('div');
  row.className = 'msg-row user';
  row.innerHTML = `
    <div>
      <div class="msg-bubble">${escHtml(text)}</div>
      <div class="msg-time">${now()}</div>
    </div>
    <div class="msg-avatar">🧑</div>`;
  chatArea.appendChild(row);
  scrollToBottom();
}

/** Render a thinking indicator and return its row element */
function addThinkingBubble() {
  hideWelcome();
  const row = document.createElement('div');
  row.className = 'msg-row bot thinking-bubble';
  row.innerHTML = `
    <div class="msg-avatar">⚡</div>
    <div class="msg-bubble">
      <div class="dot-wave">
        <span></span><span></span><span></span>
      </div>
    </div>`;
  chatArea.appendChild(row);
  scrollToBottom();
  return row;
}

/** Render a bot message, replacing the thinking bubble if provided */
function addBotMessage(text, thinkingRow) {
  if (thinkingRow) thinkingRow.remove();
  hideWelcome();

  const row = document.createElement('div');
  row.className = 'msg-row bot';

  const content = renderBotContent(text);
  row.innerHTML = `
    <div class="msg-avatar">⚡</div>
    <div>
      <div class="msg-bubble">${content}</div>
      <div class="msg-time">${now()}</div>
    </div>`;
  chatArea.appendChild(row);
  scrollToBottom();
}

/** Parse special response formats and return HTML */
function renderBotContent(text) {
  // YouTube result
  if (text.startsWith('YOUTUBE_GALLERY|')) {
    try {
      const jsonStr = text.substring('YOUTUBE_GALLERY|'.length);
      const videos = JSON.parse(jsonStr);
      
      let html = `<div style="margin-bottom:4px; font-weight:600; color:var(--cyan-light)">Found on YouTube:</div>`;
      html += `<div class="youtube-carousel">`;
      videos.forEach(v => {
        html += `
          <div class="yt-card-mini" onclick="openYtModal('${v.id}')">
            <img class="yt-thumb" src="${escHtml(v.thumbnail)}" alt="thumb" loading="lazy" />
            <div class="yt-info">
              <div class="yt-title">${escHtml(v.title)}</div>
              <div class="yt-channel">${escHtml(v.channel)}</div>
            </div>
          </div>
        `;
      });
      html += `</div>`;
      return html;
    } catch (e) {
      console.error(e);
      return `⚠️ Error rendering YouTube gallery.`;
    }
  }

  // Legacy single YOUTUBE_RESULT fallback
  if (text.startsWith('YOUTUBE_RESULT|')) {
    const parts = text.split('|');
    const title    = escHtml(parts[1] || 'Video');
    const channel  = escHtml(parts[2] || '');
    const meta     = escHtml(parts[3] || '');
    const url      = parts[4] || '#';
    const thumb    = parts[5] || '';
    const thumbHtml = thumb
      ? `<img class="yt-thumb" src="${escHtml(thumb)}" alt="thumbnail" loading="lazy" />`
      : `<div class="yt-thumb" style="background:#1a1a2e;display:flex;align-items:center;justify-content:center;font-size:1.8rem;">▶️</div>`;
    return `
      <div>Found on YouTube:</div>
      <a class="yt-card" href="${escHtml(url)}" target="_blank" rel="noopener noreferrer">
        ${thumbHtml}
        <div class="yt-info">
          <div class="yt-title">${title}</div>
          <div class="yt-meta">${channel} · ${meta}</div>
          <div class="yt-play-badge">▶ Watch on YouTube</div>
        </div>
      </a>`;
  }

  // Search results (multiple blocks separated by \n\n)
  if (text.startsWith('🔍 **Search results')) {
    return renderSearchResults(text);
  }

  // Markdown-lite: bold (**text**) and links
  return markdownLite(text);
}

function renderSearchResults(text) {
  const blocks = text.split('\n\n');
  let html = '';
  for (const block of blocks) {
    if (block.startsWith('🔍')) {
      html += `<div style="margin-bottom:10px;font-weight:600;color:var(--cyan-light)">${escHtml(block)}</div>`;
    } else if (block.trim()) {
      const lines = block.split('\n');
      const title = markdownLite(lines[0] || '');
      const body  = escHtml((lines[1] || '').replace(/^\.\.\.$/, '').trim());
      const link  = (lines[2] || '').replace('🔗 ', '').trim();
      html += `
        <div class="search-result">
          <div class="search-result-title">${title}</div>
          ${body ? `<div class="search-result-body">${body}</div>` : ''}
          ${link ? `<a class="search-result-url" href="${escHtml(link)}" target="_blank" rel="noopener">${escHtml(link)}</a>` : ''}
        </div>`;
    }
  }
  return html || escHtml(text);
}

function markdownLite(text) {
  return escHtml(text)
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\[(.+?)\]\((https?:\/\/.+?)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>')
    .replace(/\n/g, '<br>');
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ── Send query ─────────────────────────────────────────────────────────────
async function sendQuery(query) {
  if (!query.trim()) return;

  addUserMessage(query);
  const thinking = addThinkingBubble();
  setStatus('thinking', 'Thinking…');

  try {
    const res = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    const data = await res.json();

    if (data.response === 'EMAIL_MODAL') {
      thinking.remove();
      setStatus('', 'Ready');
      openEmailModal();
      return;
    }

    addBotMessage(data.response || data.error || '⚠️ No response.', thinking);

    // Server-side TTS
    if (data.response) speakText(data.response);
  } catch (err) {
    addBotMessage('⚠️ Network error. Is the server running?', thinking);
  } finally {
    setStatus('', 'Ready');
  }
}

// ── TTS (Browser Only - Natural Voices) ───────────────────────────────────
let availableVoices = [];
if ('speechSynthesis' in window) {
  const loadVoices = () => { availableVoices = window.speechSynthesis.getVoices(); };
  loadVoices();
  if (window.speechSynthesis.onvoiceschanged !== undefined) {
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }
}

async function speakText(text) {
  setStatus('speaking', 'Speaking…');

  if ('speechSynthesis' in window) {
    let clean = text
      .replace(/YOUTUBE_RESULT\|.*/g, 'Here is the top video from YouTube.')
      .replace(/YOUTUBE_GALLERY\|.*/g, 'Here are some videos from YouTube.')
      .replace(/[\u{1F300}-\u{1F9A0}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F600}-\u{1F64F}\u{1F680}-\u{1F6FF}]/gu, '')
      .replace(/\bUSD\b/g, 'dollars')
      .replace(/▲/g, 'up')
      .replace(/▼/g, 'down')
      .replace(/\*\*/g, '')
      .replace(/[*_`#]/g, '')
      .replace(/https?:\/\/\S+/g, '')
      .slice(0, 300);

    const utt = new SpeechSynthesisUtterance(clean);
    
    // Pick the most natural voice (Edge Natural or Google US English)
    let bestVoice = availableVoices.find(v => 
      (v.name.includes('Natural') || v.name.includes('Online') || v.name.includes('Google US English')) && v.lang.startsWith('en')
    );
    
    if (bestVoice) {
      utt.voice = bestVoice;
    } else {
      // Fallback to female Zira
      let zira = availableVoices.find(v => v.name.includes('Zira'));
      if(zira) utt.voice = zira;
    }

    utt.onend = () => setStatus('', 'Ready');
    window.speechSynthesis.speak(utt);
    return;
  }
  setStatus('', 'Ready');
}

// ── Mic / Push-to-talk (Browser Web Speech API) ──────────────────────────────
micBtn.addEventListener('click', () => {
  if (isListening) return;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    showToast('Voice input is not supported in this browser. Try Chrome or Edge.');
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    isListening = true;
    micBtn.classList.add('listening');
    setStatus('listening', 'Listening…');
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    textInput.value = '';
    sendQuery(transcript);
  };

  recognition.onerror = (event) => {
    showToast('Microphone error: ' + event.error);
    isListening = false;
    micBtn.classList.remove('listening');
    setStatus('', 'Ready');
  };

  recognition.onend = () => {
    isListening = false;
    micBtn.classList.remove('listening');
    if (document.getElementById('statusLabel').textContent === 'Listening…') {
      setStatus('', 'Ready');
    }
  };

  recognition.start();
});

// ── Text input ─────────────────────────────────────────────────────────────
sendBtn.addEventListener('click', () => {
  const q = textInput.value.trim();
  if (!q) return;
  textInput.value = '';
  sendQuery(q);
});

textInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendBtn.click();
  }
});

// ── Clear chat ─────────────────────────────────────────────────────────────
clearBtn.addEventListener('click', async () => {
  chatArea.innerHTML = `
    <div class="chat-welcome" id="welcomeScreen">
      <div class="welcome-glyph">⚡</div>
      <h2>Hi, I'm <span class="gradient-text">MAX</span></h2>
      <p>Your AI-powered voice assistant. Ask me anything using the mic or type below.</p>
      <div class="welcome-chips">
        <button class="chip" data-query="What's the weather in Mumbai?">🌤 Mumbai weather</button>
        <button class="chip" data-query="Get the stock price of Tesla">📈 Tesla stock</button>
        <button class="chip" data-query="Play Shape of You on YouTube">▶️ Shape of You</button>
        <button class="chip" data-query="Tell me a fun fact about space">🚀 Space fact</button>
      </div>
    </div>`;
  attachChipListeners();
  await fetch('/clear', { method: 'POST' });
});

// ── Quick actions ──────────────────────────────────────────────────────────
document.querySelectorAll('.qa-card').forEach(btn => {
  btn.addEventListener('click', () => {
    const type = btn.dataset.type;
    handleQuickAction(type);
  });
});

function handleQuickAction(type) {
  switch (type) {
    case 'weather':
      openMiniModal('🌤 Which city?', 'e.g. Mumbai, London, Tokyo', (val) => {
        sendQuery(`What's the weather in ${val}?`);
      });
      break;
    case 'stocks':
      openMiniModal('📈 Enter stock name or ticker', 'e.g. Tesla, AAPL, NVDA', (val) => {
        sendQuery(`Get the stock price of ${val}`);
      });
      break;
    case 'youtube':
      openMiniModal('▶️ What do you want to watch?', 'e.g. Blinding Lights, lo-fi music', (val) => {
        sendQuery(`Play ${val} on YouTube`);
      });
      break;
    case 'email':
      openEmailModal();
      break;
    case 'search':
      openMiniModal('🔍 Search the web', 'Enter your search query', (val) => {
        sendQuery(`Search for ${val}`);
      });
      break;
  }
}

// ── Mini modal ─────────────────────────────────────────────────────────────
let _miniCallback = null;

function openMiniModal(title, placeholder, callback) {
  miniTitle.textContent = title;
  miniInput.placeholder = placeholder;
  miniInput.value = '';
  _miniCallback = callback;
  miniBackdrop.hidden = false;
  setTimeout(() => miniInput.focus(), 50);
}

function closeMiniModal() { miniBackdrop.hidden = true; _miniCallback = null; }

miniClose.addEventListener('click', closeMiniModal);
miniCancel.addEventListener('click', closeMiniModal);
miniSubmit.addEventListener('click', () => {
  const val = miniInput.value.trim();
  if (!val) return;
  closeMiniModal();
  if (_miniCallback) _miniCallback(val);
});
miniInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') miniSubmit.click();
  if (e.key === 'Escape') closeMiniModal();
});

// ── Email modal ────────────────────────────────────────────────────────────
function openEmailModal() {
  emailBackdrop.hidden = false;
  document.getElementById('emailTo').focus();
}
function closeEmailModal() { emailBackdrop.hidden = true; }

emailClose.addEventListener('click', closeEmailModal);
emailCancel.addEventListener('click', closeEmailModal);

emailSend.addEventListener('click', async () => {
  const senderEmail = document.getElementById('senderEmail').value.trim();
  const senderPassword = document.getElementById('senderPassword').value.trim();
  const to      = document.getElementById('emailTo').value.trim();
  const subject = document.getElementById('emailSubject').value.trim();
  const body    = document.getElementById('emailBody').value.trim();

  if (!to || !subject || !body) {
    showToast('Please fill in the To, Subject, and Message fields.');
    return;
  }

  emailSend.textContent = 'Sending…';
  emailSend.disabled = true;

  try {
    const res = await fetch('/send-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ to, subject, body, sender_email: senderEmail, sender_password: senderPassword }),
    });
    const data = await res.json();
    closeEmailModal();
    addBotMessage(data.response || data.error || '⚠️ Unknown error.', null);
    if (data.success) speakText('Email sent successfully!');
  } catch (err) {
    showToast('Failed to send email. Check your connection.');
  } finally {
    emailSend.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg> Send Email`;
    emailSend.disabled = false;
  }
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') { closeEmailModal(); closeMiniModal(); }
});

// ── Wake Word SSE ──────────────────────────────────────────────────────────
wakeToggle.addEventListener('change', async () => {
  wakeEnabled = wakeToggle.checked;

  await fetch('/toggle-wake-word', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ enabled: wakeEnabled, client_id: CLIENT_ID }),
  });

  if (wakeEnabled) {
    connectWakeSSE();
    showToast('👂 Hey Max is listening in the background…');
    setStatus('', 'Wake: ON');
    statusLabel.textContent = 'Wake word: ON';
  } else {
    if (wakeSource) { wakeSource.close(); wakeSource = null; }
    setStatus('', 'Ready');
    showToast('Wake word detection stopped.');
  }
});

let wakeRecognition = null;

function connectWakeSSE() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    showToast('Browser does not support background wake word.');
    wakeToggle.checked = false;
    return;
  }
  
  if (wakeRecognition) {
    wakeRecognition.stop();
  }

  wakeRecognition = new SpeechRecognition();
  wakeRecognition.continuous = true;
  wakeRecognition.interimResults = true;
  wakeRecognition.lang = 'en-US';

  wakeRecognition.onresult = (event) => {
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        const transcript = event.results[i][0].transcript.toLowerCase();
        if (transcript.includes('hey max') || transcript.includes('okay max')) {
          showToast('⚡ Wake word detected! Speak your command...', 2500);
          setStatus('listening', '🎙 Hey Max detected!');
          
          let parts = transcript.split(/hey max|okay max/);
          let cmd = parts[parts.length - 1].trim();
          if (cmd && cmd.length > 2) {
            sendQuery(cmd);
          } else {
             setTimeout(() => {
               if(!isListening) micBtn.click();
             }, 800);
          }
        }
      }
    }
  };

  wakeRecognition.onend = () => {
    if (wakeEnabled) {
      wakeRecognition.start(); // auto-restart
    }
  };

  wakeRecognition.start();
}

// ── Suggestion chips ───────────────────────────────────────────────────────
function attachChipListeners() {
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => sendQuery(chip.dataset.query));
  });
}
attachChipListeners();

// ── YouTube Modal ─────────────────────────────────────────────────────────
const ytBackdrop = document.getElementById('ytBackdrop');
const ytClose    = document.getElementById('ytClose');
const ytIframe   = document.getElementById('ytIframe');

window.openYtModal = function(videoId) {
  // Use youtube embed URL
  ytIframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
  ytBackdrop.hidden = false;
};

function closeYtModal() {
  ytBackdrop.hidden = true;
  ytIframe.src = ""; // Stop playing
}

if (ytClose) {
  ytClose.addEventListener('click', closeYtModal);
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeEmailModal();
    closeMiniModal();
    if (ytBackdrop && !ytBackdrop.hidden) closeYtModal();
  }
});
