document.addEventListener('DOMContentLoaded', async () => {
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const chatMessages = document.getElementById('chat-messages');

  // ✅ Retrieve the stored token
  const token = localStorage.getItem('token');
  if (!token) {
    window.location.href = 'login.html';
    return;
  }

  let sessionId = localStorage.getItem('session_id') || crypto.randomUUID();
  localStorage.setItem('session_id', sessionId); // persist session

  chatForm.addEventListener('submit', async e => {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;

    // Show user message
    const userMessageEl = document.createElement('div');
    userMessageEl.className = 'chat-message-user mb-2';
    userMessageEl.textContent = message;
    chatMessages.appendChild(userMessageEl);
    chatInput.value = '';

    try {
      const response = await fetch('http://127.0.0.1:8000/chatbot/ask', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message, session_id: sessionId })
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(errText || 'Chatbot error');
      }

      const data = await response.json();
      const botMessageEl = document.createElement('div');
      botMessageEl.className = 'chat-message-bot mb-2';
      botMessageEl.textContent = data.reply;
      chatMessages.appendChild(botMessageEl);

      chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (err) {
      console.error('Chatbot fetch error:', err);
      alert('Failed to get response from chatbot. Please try again.');
    }
  });
});
