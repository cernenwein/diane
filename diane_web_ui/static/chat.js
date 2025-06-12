document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('chat-form');
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    const input = document.getElementById('message');
    const msg = input.value.trim();
    if (!msg) return;
    appendMessage('user', msg);
    input.value = '';
    try {
      const res = await fetch('/send_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
      const data = await res.json();
      if (data.response) {
        appendMessage('diane', data.response);
      } else {
        appendMessage('diane', 'Error: ' + (data.error || 'Unknown'));
      }
    } catch (err) {
      appendMessage('diane', 'Error: ' + err);
    }
  });
});

function appendMessage(who, text) {
  const chatbox = document.getElementById('chatbox');
  const div = document.createElement('div');
  div.className = 'message ' + who;
  div.textContent = text;
  chatbox.appendChild(div);
  chatbox.scrollTop = chatbox.scrollHeight;
}
