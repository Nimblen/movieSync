// Установите WebSocket соединение
const roomId = "123"; // Пример ID комнаты
let socket = new WebSocket(`ws://localhost:8000/ws/movie/${roomId}/`);

// Элементы DOM
const videoPlayer = document.getElementById("video-player");
const chatContainer = document.getElementById("chat-container");
const chatInput = document.getElementById("chat-input");
const sendButton = document.getElementById("send-button");

// Добавление сообщения в чат
function addChatMessage(user, message) {
    const messageElement = document.createElement("div");
    messageElement.textContent = `${user}: ${message}`;
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight; // Прокручиваем вниз
}

// Обработка соединения WebSocket
socket.onopen = () => {
    console.log("WebSocket connection opened");

    socket.send(JSON.stringify({
        jsonrpc: "2.0",
        method: "get_initial_state",
        params: { room_id: roomId },
        id: 1
    }));

    socket.send(JSON.stringify({
        jsonrpc: "2.0",
        method: "get_sync_state",
        params: { room_id: roomId },
        id: 2
    }));
};

// Обработка входящих сообщений
socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Message from server:", data);

    // Проверка формата JSON-RPC 2.0
    if (data.jsonrpc === "2.0") {
        if (data.result) {
            const result = data.result;

            if (result.type === "initial_state") {
                // Установка начального состояния комнаты
                const { state, messages } = result;
                if (state) {
                    videoPlayer.currentTime = parseFloat(state.current_time || 0);
                    if (state.is_playing) {
                        videoPlayer.play();
                    } else {
                        videoPlayer.pause();
                    }
                }

                // Загрузка истории чата
                messages.forEach((message) => {
                    const [user, ...messageParts] = message.split(": ");
                    const messageContent = messageParts.join(": ");
                    addChatMessage(user, messageContent);
                });
            } else if (result.type === "set_sync_state") {
                // Синхронизация состояния видеоплеера
                const state = result.state;
                if (state) {
                    videoPlayer.currentTime = parseFloat(state.current_time);
                    if (state.is_playing) {
                        videoPlayer.play();
                    } else {
                        videoPlayer.pause();
                    }
                }
            } else if (result.type === "chat_message") {
                // Добавление сообщения в чат
                addChatMessage(result.username || "User", result.message);
            }
        } else if (data.error) {
            console.error("Error from server:", data.error);
        }
    } else {
        console.error("Invalid JSON-RPC response format:", data);
    }
};

// Обработка ошибок
socket.onerror = (error) => {
    console.error("WebSocket error:", error);
};

// Обработка закрытия соединения с повторным подключением
socket.onclose = () => {
    console.log("WebSocket connection closed. Reconnecting...");
    setTimeout(() => {
        socket = new WebSocket(`ws://localhost:8000/ws/movie/${roomId}/`);
    }, 3000); // Переподключение через 3 секунды
};

// Отправка сообщения в чат
sendButton.addEventListener("click", () => {
    const message = chatInput.value;
    if (message) {
        socket.send(JSON.stringify({
            jsonrpc: "2.0",
            method: "send_chat_message",
            params: { message: message, room_id: roomId },
            id: 3
        }));
        chatInput.value = "";
    }
});

// Синхронизация состояния при воспроизведении или паузе
videoPlayer.addEventListener("play", () => {
    socket.send(JSON.stringify({
        jsonrpc: "2.0",
        method: "set_sync_state",
        params: {
            room_id: roomId,
            current_time: videoPlayer.currentTime,
            is_playing: true
        },
        id: 4
    }));
});

videoPlayer.addEventListener("pause", () => {
    socket.send(JSON.stringify({
        jsonrpc: "2.0",
        method: "set_sync_state",
        params: {
            room_id: roomId,
            current_time: videoPlayer.currentTime,
            is_playing: false
        },
        id: 5
    }));
});


let seekTimeout;
videoPlayer.addEventListener("seeked", () => {
    clearTimeout(seekTimeout);
    seekTimeout = setTimeout(() => {
        socket.send(JSON.stringify({
            jsonrpc: "2.0",
            method: "set_sync_state",
            params: {
                room_id: roomId,
                current_time: videoPlayer.currentTime,
                is_playing: !videoPlayer.paused
            },
            id: 6
        }));
    }, 5000); 
});
