const socket = io();

socket.on('connect', function () {
  socket.send('User has connected!');
});

socket.on('message', function (data) {
  const chat = document.getElementById("chat");
  chat.innerHTML += `<p>${data}</p>`;
  chat.scrollTop = chat.scrollHeight;
});

const msgInput = document.getElementById("msg");
msgInput.addEventListener('input', () => {
  msgInput.style.height = 'auto';
  msgInput.style.height = msg.scrollHeight + 'px';
});

function sendMessage() {
  const msg = msgInput.value;
  if (msg.trim()) {
    socket.send(msg);
  }
    msgInput.value = "";
    msgInput.style.height = 'auto';
}