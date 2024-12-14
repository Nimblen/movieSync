const hlsPlaylistUrl = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8";
const roomId = "123"; // Пример ID комнаты
const socketUrl = `ws://localhost:8000/ws/movie/${roomId}/`;

// DOM элементы
const videoPlayer = document.getElementById("video-player");
const qualitySelector = document.getElementById("quality-selector");
const chatContainer = document.getElementById("chat-container");
const chatInput = document.getElementById("chat-input");
const sendButton = document.getElementById("send-button");

let hls;
let socket;

// Инициализация HLS плеера
function initializeVideoPlayer() {
    if (Hls.isSupported()) {
        hls = new Hls();
        hls.loadSource(hlsPlaylistUrl);
        hls.attachMedia(videoPlayer);

        hls.on(Hls.Events.MANIFEST_PARSED, () => {
            console.log("HLS playlist loaded");
            populateQualitySelector();
        });
    } else if (videoPlayer.canPlayType("application/vnd.apple.mpegurl")) {
        videoPlayer.src = hlsPlaylistUrl;
    } else {
        console.error("HLS is not supported in this browser.");
    }
}

// Заполняем селектор качества
function populateQualitySelector() {
    const levels = hls.levels || []; // Проверяем, что уровни качества существуют
    levels.forEach((level, index) => {
        const option = document.createElement("option");
        option.value = index;
        option.textContent = `${level.height}p`;
        qualitySelector.appendChild(option);
    });

    // Событие изменения качества
    qualitySelector.addEventListener("change", () => {
        const selectedValue = qualitySelector.value;
        if (selectedValue === "auto") {
            hls.currentLevel = -1; // Автоматический выбор качества
        } else {
            hls.currentLevel = parseInt(selectedValue, 10); // Устанавливаем выбранный уровень
        }
    });
}

// Добавление сообщения в чат
function addChatMessage(user, message) {
    const messageElement = document.createElement("div");
    messageElement.textContent = `${user}: ${message}`;
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight; // Прокрутка вниз
}

// Установка состояния плеера
function setPlayerState(state) {
    if (state) {
        videoPlayer.currentTime = parseFloat(state.current_time || 0);
        if (state.is_playing) {
            videoPlayer.play();
        } else {
            videoPlayer.pause();
        }
    }
}

// Инициализация WebSocket
function initializeWebSocket() {
    socket = new WebSocket(socketUrl);

    socket.onopen = () => {
        console.log("WebSocket connection opened");
        // Запрос начального состояния комнаты
        socket.send(
            JSON.stringify({
                jsonrpc: "2.0",
                method: "get_initial_state",
                params: { room_id: roomId },
                id: 1,
            })
        );
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("Message from server:", data);

        if (data.result) {
            if (data.result.type === "initial_state") {
                const { state, messages } = data.result;

                // Устанавливаем состояние плеера
                setPlayerState(state);

                // Загружаем историю чата
                messages.forEach((msg) => {
                    const [user, ...messageParts] = msg.split(": ");
                    addChatMessage(user, messageParts.join(": "));
                });
            } else if (data.result.type === "chat_message") {
                addChatMessage(data.result.username || "User", data.result.message);
            } else if (data.result.type === "set_sync_state") {
                setPlayerState(data.result.state);
            }
        } else if (data.error) {
            console.error("Error from server:", data.error);
        }
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
    };

    socket.onclose = () => {
        console.warn("WebSocket connection closed. Reconnecting...");
        setTimeout(() => initializeWebSocket(), 3000); // Переподключение через 3 секунды
    };
}

// Отправка сообщения в чат
sendButton.addEventListener("click", () => {
    const message = chatInput.value;
    if (message) {
        socket.send(
            JSON.stringify({
                jsonrpc: "2.0",
                method: "send_chat_message",
                params: { room_id: roomId, message: message },
                id: 2,
            })
        );
        chatInput.value = "";
    }
});

// Синхронизация состояния при воспроизведении
videoPlayer.addEventListener("play", () => {
    socket.send(
        JSON.stringify({
            jsonrpc: "2.0",
            method: "set_sync_state",
            params: {
                room_id: roomId,
                current_time: videoPlayer.currentTime,
                is_playing: true,
            },
            id: 3,
        })
    );
});

// Синхронизация состояния при паузе
videoPlayer.addEventListener("pause", () => {
    socket.send(
        JSON.stringify({
            jsonrpc: "2.0",
            method: "set_sync_state",
            params: {
                room_id: roomId,
                current_time: videoPlayer.currentTime,
                is_playing: false,
            },
            id: 4,
        })
    );
});

// Запуск приложения
initializeVideoPlayer();
initializeWebSocket();
