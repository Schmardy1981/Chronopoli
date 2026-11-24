/**
 * Chronopoli AI Tutor — Floating Sidebar Widget
 * Embeds in every LMS page via theme header.html
 * Communicates with /chronopoli/ai-tutor/chat/ via Server-Sent Events (SSE)
 */
(function() {
  'use strict';

  const CHAT_ENDPOINT = '/chronopoli/ai-tutor/chat/';
  const HISTORY_ENDPOINT = '/chronopoli/ai-tutor/history/';

  let sessionId = null;
  let isOpen = false;
  let isStreaming = false;

  // --- Create Widget DOM ---
  function createWidget() {
    const widget = document.createElement('div');
    widget.id = 'cp-tutor-widget';
    widget.innerHTML = `
      <button id="cp-tutor-toggle" title="AI Tutor">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
      </button>
      <div id="cp-tutor-panel" class="cp-tutor-hidden">
        <div id="cp-tutor-header">
          <span class="cp-tutor-title">Chronopoli AI Tutor</span>
          <button id="cp-tutor-close">&times;</button>
        </div>
        <div id="cp-tutor-messages"></div>
        <div id="cp-tutor-input-wrap">
          <input type="text" id="cp-tutor-input" placeholder="Ask anything about the course..." autocomplete="off" />
          <button id="cp-tutor-send" title="Send">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(widget);

    // Event listeners
    document.getElementById('cp-tutor-toggle').addEventListener('click', togglePanel);
    document.getElementById('cp-tutor-close').addEventListener('click', togglePanel);
    document.getElementById('cp-tutor-send').addEventListener('click', sendMessage);
    document.getElementById('cp-tutor-input').addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  function togglePanel() {
    const panel = document.getElementById('cp-tutor-panel');
    const toggle = document.getElementById('cp-tutor-toggle');
    isOpen = !isOpen;
    panel.classList.toggle('cp-tutor-hidden', !isOpen);
    toggle.classList.toggle('cp-tutor-active', isOpen);

    if (isOpen && !document.getElementById('cp-tutor-messages').hasChildNodes()) {
      addMessage('assistant', 'Welcome to the Chronopoli AI Tutor. I can answer questions about your courses, the platform, and the digital economy. How can I help?');
    }
  }

  function sendMessage() {
    if (isStreaming) return;
    const input = document.getElementById('cp-tutor-input');
    const question = input.value.trim();
    if (!question) return;

    input.value = '';
    addMessage('user', question);
    streamResponse(question);
  }

  function addMessage(role, content) {
    const container = document.getElementById('cp-tutor-messages');
    const msg = document.createElement('div');
    msg.className = `cp-tutor-msg cp-tutor-msg-${role}`;
    msg.textContent = content;
    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;
    return msg;
  }

  function streamResponse(question) {
    isStreaming = true;
    const msgEl = addMessage('assistant', '');
    msgEl.classList.add('cp-tutor-streaming');

    const csrfToken = getCsrfToken();
    const courseKey = getCourseKey();

    fetch(CHAT_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({
        question: question,
        session_id: sessionId,
        course_key: courseKey,
      }),
    }).then(function(response) {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      function read() {
        reader.read().then(function(result) {
          if (result.done) {
            isStreaming = false;
            msgEl.classList.remove('cp-tutor-streaming');
            return;
          }

          buffer += decoder.decode(result.value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (!line.startsWith('data: ')) continue;
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === 'session') {
                sessionId = data.session_id;
              } else if (data.type === 'chunk') {
                msgEl.textContent += data.text;
                document.getElementById('cp-tutor-messages').scrollTop =
                  document.getElementById('cp-tutor-messages').scrollHeight;
              } else if (data.type === 'done') {
                if (data.sources && data.sources.length > 0) {
                  const srcEl = document.createElement('div');
                  srcEl.className = 'cp-tutor-sources';
                  srcEl.textContent = 'Sources: ' + data.sources.map(function(s) {
                    return s.uri.split('/').pop();
                  }).join(', ');
                  msgEl.appendChild(srcEl);
                }
              }
            } catch (e) { /* ignore parse errors from partial chunks */ }
          }

          read();
        });
      }
      read();
    }).catch(function(err) {
      msgEl.textContent = 'Sorry, the AI Tutor is temporarily unavailable. Please try again.';
      isStreaming = false;
      msgEl.classList.remove('cp-tutor-streaming');
    });
  }

  function getCsrfToken() {
    const cookie = document.cookie.split(';').find(function(c) {
      return c.trim().startsWith('csrftoken=');
    });
    return cookie ? cookie.split('=')[1] : '';
  }

  function getCourseKey() {
    // Extract course key from URL if on a course page
    const match = window.location.pathname.match(/\/courses\/(course-v1:[^/]+)/);
    return match ? match[1] : '';
  }

  // --- Initialize ---
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createWidget);
  } else {
    createWidget();
  }
})();
