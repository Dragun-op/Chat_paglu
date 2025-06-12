const socket = io();

const sender = CHAT_DATA.sender;
const receiver = CHAT_DATA.receiver;
const senderId = CHAT_DATA.sender_id;
const receiverId = CHAT_DATA.receiver_id;

function formatTimestamp(ts) {
  const date = new Date(ts);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

socket.emit('join_private', { sender, receiver });

window.onload = function () {
  const chatBox = document.getElementById("chat-box");
  chatBox.scrollTop = chatBox.scrollHeight;

  socket.emit('mark_seen', {
    sender: senderId,
    receiver: receiverId
  });
};

socket.on('new_private_message', data => {
  const chatBox = document.getElementById("chat-box");
  const msgElement = document.createElement("div");

  const msgClass = data.sender === sender ? 'message sent' : 'message received';
  msgElement.className = msgClass;

  const time = formatTimestamp(data.timestamp || Date.now());

  msgElement.innerHTML = `
    <div>
      <b>${data.sender}</b>: ${data.message}
    </div>
    <div class="msg-time">${time}${data.seen ? ' <span class="seen-tick">✓</span>' : ''}</div>
  `;

  chatBox.appendChild(msgElement);
  chatBox.scrollTop = chatBox.scrollHeight;

  if (data.sender !== sender) {
    socket.emit('mark_seen', {
      sender: senderId,
      receiver: receiverId
    });
  }
});

socket.on('seen_ack', () => {
  const allSentMessages = document.querySelectorAll('.message.sent');

  allSentMessages.forEach(msg => {
    const tick = msg.querySelector('.seen-tick');
    if (!tick) {
      const timeEl = msg.querySelector('.msg-time');
      if (timeEl) {
        timeEl.innerHTML += ` <span class="seen-tick">✓</span>`;
      }
    }
  });
});

function sendMessage() {
  const input = document.getElementById("message");
  const message = input.value.trim();
  if (!message) return;

  socket.emit('private_message', {
    sender,
    receiver,
    sender_id: senderId,
    receiver_id: receiverId,
    message
  });

  input.value = '';
}