document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.getElementById('send-button');
    const userInput = document.getElementById('user-input');
    const chatWindow = document.getElementById('chat-window');
    const modeSelect = document.getElementById('mode-select');
    const voiceButton = document.getElementById('voice-button');

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    function appendMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        messageDiv.textContent = text;
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;
        appendMessage(message, 'user');
        userInput.value = '';
        const mode = modeSelect.value;

        fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message, mode: mode })
        })
        .then(response => response.json())
        .then(data => {
            appendMessage(data.response, 'ai');
            // Handle emotion visualization and audio playback if needed
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Voice input implementation
    voiceButton.addEventListener('click', function() {
        if ('webkitSpeechRecognition' in window) {
            const recognition = new webkitSpeechRecognition();
            recognition.lang = 'en-US';
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                userInput.value = transcript;
            };
            recognition.start();
        } else {
            alert('Speech recognition not supported in this browser.');
        }
    });
});
