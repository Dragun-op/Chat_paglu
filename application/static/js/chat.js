const socket = io();

const sender = CHAT_DATA.sender;
const receiver = CHAT_DATA.receiver;
const senderId = CHAT_DATA.sender_id;
const receiverId = CHAT_DATA.receiver_id;

socket.emit('join_private', { sender, receiver });

socket.on('new_private_message', data => {
  const chatBox = document.getElementById("chat-box");
  const msgElement = document.createElement("div");

  const msgClass = data.sender === sender ? 'message sent' : 'message received';
  msgElement.className = msgClass;

  msgElement.innerHTML = `<b>${data.sender}:</b> ${data.message}`;

  chatBox.appendChild(msgElement);
  chatBox.scrollTop = chatBox.scrollHeight;
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


window.onload = function () {
  const chatBox = document.getElementById("chat-box");
  chatBox.scrollTop = chatBox.scrollHeight;
};