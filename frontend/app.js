// app.js

const apiBaseUrl = "http://localhost:8000/api"; // Backend API Base URL
const socketBaseUrl = "ws://localhost:8000/ws/app"; // WebSocket Base URL (без лишнего /)

// DOM Elements
const roomListItems = document.getElementById("room-list-items");
const videoPlayer = document.getElementById("video-player");
const chatContainer = document.getElementById("chat-container");
const chatInput = document.getElementById("chat-input");
const sendButton = document.getElementById("send-button");
const userListItems = document.getElementById("user-list-items");
const qualitySelector = document.getElementById("quality-selector");
const createRoomForm = document.getElementById("create-room-form");

let hls, socket;
let currentRoomId = null;
let lastSyncState = { current_time: 0, is_playing: false }; // Последнее отправленное состояние
let isSyncing = false; // Флаг, чтобы избежать зацикливания при синхронизации

// Получаем CSRF-токен (если используется Django без JWT/Token Auth)
function getCSRFToken() {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith("csrftoken=")) {
            return cookie.split("=")[1];
        }
    }
    return "";
}

const csrfToken = getCSRFToken();

// Дебаунс-функция (для задержки вызова syncPlayerState)
function debounce(func, delay) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => func.apply(this, args), delay);
    };
}

// --- Дебаунс-обёртка для syncPlayerState ---
const debouncedSyncPlayerState = debounce(syncPlayerState, 300);

// --- Инициализация WebSocket (вызывается один раз при старте приложения / логине) ---
function initializeWebSocket() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        console.log("WebSocket уже подключён.");
        return;
    }

    // Подключаемся без лишнего слэша в конце
    socket = new WebSocket(`${socketBaseUrl}`);

    socket.onopen = () => {
        console.log("WebSocket: соединение установлено.");
        // При необходимости можно запросить список комнат или что-то ещё через WS
        // sendWebSocketMessage("get_rooms", {});
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("Получено WebSocket-сообщение:", data);
        handleWebSocketMessage(data);
    };

    socket.onerror = (error) => {
        console.error("WebSocket ошибка:", error);
    };

    socket.onclose = () => {
        console.warn("WebSocket: соединение закрыто.");
    };
}

// --- Отправка сообщения по WebSocket ---
function sendWebSocketMessage(method, params) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.error("WebSocket не подключён. Невозможно отправить сообщение:", method);
        return;
    }

    socket.send(
        JSON.stringify({
            jsonrpc: "2.0",
            method: method,
            params: params,
            id: 1, // В реальном приложении можно генерировать уникальные id
        })
    );
}

// --- Обработка входящих сообщений WebSocket ---
function handleWebSocketMessage(data) {
    if (data.result) {
        switch (data.result.type) {
            case "initial_state":
                setPlayerState(data.result.state);
                updateChatMessages(data.result.messages);
                renderUserList(data.result.users);
                break;
            case "set_sync_state":
                setPlayerState(data.result.state);
                break;
            case "chat_message":
                addChatMessage(data.result.username || "User", data.result.message);
                break;
            case "update_users":
                renderUserList(data.result.users);
                break;
            case "create_room": 
                // Ответ на создание комнаты. Можно обновить список комнат или вывести уведомление.
                console.log("Комната успешно создана (WS).", data.result);
                fetchRooms(); 
                break;
            default:
                console.log("Неизвестный тип сообщения:", data.result.type);
        }
    } else if (data.error) {
        console.error("Ошибка RPC:", data.error);
    }
}

// --- Синхронизация состояния плеера ---
function syncPlayerState(isPlaying) {
    if (isSyncing || !currentRoomId) return;

    const currentTime = videoPlayer.currentTime;
    if (
        Math.abs(currentTime - lastSyncState.current_time) > 0.5 ||
        isPlaying !== lastSyncState.is_playing
    ) {
        sendWebSocketMessage("set_sync_state", {
            room_id: currentRoomId,
            current_time: currentTime,
            is_playing: isPlaying,
        });
        lastSyncState = { current_time, is_playing };
    }
}

// --- Установка состояния плеера, полученного с сервера ---
function setPlayerState(state) {
    if (state) {
        const currentTime = parseFloat(state.current_time || 0);
        const isPlaying = state.is_playing;

        isSyncing = true; // Чтобы не поймать зацикливание

        if (Math.abs(videoPlayer.currentTime - currentTime) > 1) {
            videoPlayer.currentTime = currentTime;
        }

        if (isPlaying && videoPlayer.paused) {
            videoPlayer.play();
        } else if (!isPlaying && !videoPlayer.paused) {
            videoPlayer.pause();
        }

        setTimeout(() => (isSyncing = false), 500);
    }
}

// --- Инициализация HLS-плеера (при выборе комнаты) ---
function initializeVideoPlayer(hlsUrl) {
    if (Hls.isSupported()) {
        hls = new Hls();
        hls.loadSource(hlsUrl);
        hls.attachMedia(videoPlayer);
        hls.on(Hls.Events.MANIFEST_PARSED, populateQualitySelector);
    } else if (videoPlayer.canPlayType("application/vnd.apple.mpegurl")) {
        // На Safari и iOS
        videoPlayer.src = hlsUrl;
    } else {
        console.error("HLS не поддерживается в этом браузере.");
    }
}

// --- Заполнение селектора качества ---
function populateQualitySelector() {
    qualitySelector.innerHTML = `<option value="auto">Auto</option>`;
    hls.levels.forEach((level, index) => {
        const option = document.createElement("option");
        option.value = index;
        option.textContent = `${level.height}p`;
        qualitySelector.appendChild(option);
    });

    qualitySelector.addEventListener("change", () => {
        hls.currentLevel = qualitySelector.value === "auto" ? -1 : parseInt(qualitySelector.value, 10);
    });
}

// --- Функция для входа в комнату (не переинициализируем сокет) ---
async function joinRoom(roomId, movieId) {
    currentRoomId = roomId;
    console.log("Входим в комнату:", roomId);

    // 1. Сообщаем серверу, что мы хотим присоединиться к комнате
    sendWebSocketMessage("join_room", { room_id: roomId });

    // 2. Запрашиваем первоначальное состояние комнаты
    sendWebSocketMessage("get_initial_state", { room_id: roomId });

    // 3. Загружаем детали фильма (по-прежнему через REST)
    if (movieId) {
        fetchMovieDetails(movieId);
    }
}

// --- Fetch деталей фильма по API (REST) ---
async function fetchMovieDetails(movieId) {
    try {
        const response = await fetch(`${apiBaseUrl}/movie/${movieId}/`);
        const movie = await response.json();
        if (movie.hls_playlist) {
            initializeVideoPlayer(movie.hls_playlist);
        }
    } catch (error) {
        console.error("Не удалось получить детали фильма:", error);
    }
}

// --- Обновление списка сообщений в чате ---
function updateChatMessages(messages) {
    chatContainer.innerHTML = "";
    messages.forEach((msg) => {
        const username = Object.keys(msg)[0];
        const message = msg[username];
        addChatMessage(username, message);
    });
}

// --- Добавить одно сообщение в чат ---
function addChatMessage(user, message) {
    const displayName = user || "Anonymous";
    const messageElement = document.createElement("div");
    messageElement.textContent = `${displayName}: ${message || "No message"}`;
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// --- Отобразить список пользователей ---
function renderUserList(users) {
    userListItems.innerHTML = "";
    users.forEach((user) => {
        const userElement = document.createElement("li");
        userElement.textContent = user.username || "Anonymous";
        userListItems.appendChild(userElement);
    });
}

// --- Получить список комнат с API (REST) ---
async function fetchRooms() {
    try {
        const response = await fetch(`${apiBaseUrl}/room/`);
        const result = await response.json();

        if (result.status === "success") {
            renderRoomList(result.data);
        } else {
            console.error("Ошибка при получении списка комнат:", result);
        }
    } catch (error) {
        console.error("Ошибка при запросе списка комнат:", error);
    }
}

// --- Отрисовать список комнат ---
function renderRoomList(rooms) {
    roomListItems.innerHTML = "";
    rooms.forEach((room) => {
        const roomElement = document.createElement("li");
        roomElement.textContent = `Room: ${room.room_id} (Type: ${room.room_type}, Max: ${room.max_users})`;
        roomElement.style.cursor = "pointer";
        roomElement.addEventListener("click", () => joinRoom(room.room_id, room.movie_id));
        roomListItems.appendChild(roomElement);
    });
}

// --- Отправка сообщения (чат) ---
sendButton.addEventListener("click", () => {
    const message = chatInput.value.trim();
    if (message && currentRoomId) {
        sendWebSocketMessage("send_chat_message", {
            room_id: currentRoomId,
            message: message,
        });
        chatInput.value = "";
    }
});

// --- События видеоплеера (для синхронизации) ---
videoPlayer.addEventListener("play", () => debouncedSyncPlayerState(true));
videoPlayer.addEventListener("pause", () => debouncedSyncPlayerState(false));
videoPlayer.addEventListener("seeked", () => debouncedSyncPlayerState(!videoPlayer.paused));

// --- Обработка сабмита формы создания комнаты (через WS) ---
createRoomForm.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.error("WebSocket не подключен. Невозможно создать комнату через WS.");
        return;
    }

    const roomName = document.getElementById("room-name").value.trim();
    const movieId = document.getElementById("movie-id").value.trim();
    const roomType = document.getElementById("room-type").value;
    const maxUsers = document.getElementById("max-users").value;

    // Отправляем запрос на создание комнаты по WS
    sendWebSocketMessage("create_room", {
        room_id: roomName,
        movie_id: movieId,
        room_type: roomType,
        room_owner: 1,
        max_users: parseInt(maxUsers, 10),
    });

    // Сбрасываем форму
    createRoomForm.reset();
});

// --- Инициализация приложения (вызываем при загрузке страницы или после логина) ---
function initializeApp() {
    // 1. Подключаемся к WebSocket
    initializeWebSocket();

    // 2. Запрашиваем список комнат по REST
    fetchRooms();
}

// Запускаем
initializeApp();
