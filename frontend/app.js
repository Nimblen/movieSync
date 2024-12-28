// ============ EDIT THIS URL AS NEEDED =============
const socketBaseUrl = "ws://localhost:8000/ws/app"; 
// ==================================================

// DOM Elements
const DOM = {
  loginContainer: document.getElementById("login-container"),
  loginForm: document.getElementById("login-form"),
  loginUsernameInput: document.getElementById("login-username"),
  loginPasswordInput: document.getElementById("login-password"),
  mainContainer: document.getElementById("main-container"),
  logoutButton: document.getElementById("logout-button"),
  roomListItems: document.getElementById("room-list-items"),
  videoPlayer: document.getElementById("video-player"),
  chatMessages: document.getElementById("chat-messages"),
  chatInput: document.getElementById("chat-input"),
  sendButton: document.getElementById("send-button"),
  userListItems: document.getElementById("user-list-items"),
  qualitySelector: document.getElementById("quality-selector"),
  createRoomForm: document.getElementById("create-room-form"),
  notificationContainer: document.getElementById("notification-container"), // Добавлено
};

// HLS & WebSocket references
let hls, socket;
let currentRoomId = null;
let lastSyncState = { current_time: 0, is_playing: false };
let isSyncing = false;

// ========== HELPER FUNCTIONS ==========
const showAlert = (message) => alert(message);
const toggleVisibility = (element, visible) => {
  element.style.display = visible ? "flex" : "none";
};

// ---------- LOGIN/LOGOUT LOGIC ----------
async function login(username, password) {
  if (username && password) {
    localStorage.setItem("loggedInUser", username);
    return true;
  }
  return false;
}

function handleLogout() {
  localStorage.removeItem("loggedInUser");
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.close();
  }
  toggleVisibility(DOM.mainContainer, false);
  toggleVisibility(DOM.loginContainer, true);
  createNotification("You have been logged out.", "info"); // Уведомление
}

DOM.loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const username = DOM.loginUsernameInput.value.trim();
  const password = DOM.loginPasswordInput.value.trim();

  if (await login(username, password)) {
    toggleVisibility(DOM.loginContainer, false);
    toggleVisibility(DOM.mainContainer, true);
    initializeApp();
    createNotification(`Welcome, ${username}!`, "success"); // Уведомление
  } else {
    showAlert("Login failed - please check username/password");
    createNotification("Login failed. Please try again.", "error"); // Уведомление
  }
});

DOM.logoutButton.addEventListener("click", handleLogout);

// =============== WEBSOCKET & SYNC LOGIC =================
function initializeWebSocket() {
  if (socket && socket.readyState === WebSocket.OPEN) {
    console.log("WebSocket already connected.");
    return;
  }

  socket = new WebSocket(socketBaseUrl);

  socket.onopen = () => {
    console.log("WebSocket: connection established.");
    sendWebSocketMessage("get_rooms", {});
  };

  socket.onerror = (error) => console.error("WebSocket error:", error);

  socket.onclose = () => console.warn("WebSocket: connection closed.");

  socket.onmessage = (event) => handleWebSocketMessage(JSON.parse(event.data));
}

function sendWebSocketMessage(method, params) {
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    console.error("WebSocket is not open. Can't send:", method);
    createNotification(`Cannot send ${method} - WebSocket is not connected.`, "error"); // Уведомление
    return;
  }
  socket.send(JSON.stringify({ jsonrpc: "2.0", method, params, id: Date.now() }));
}

function handleWebSocketMessage(data) {
  if (data.result) {
    const handlers = {
      get_rooms: () => renderRoomList(data.result.rooms),
      initial_state: () => {
        setPlayerState(data.result.state);
        updateChatMessages(data.result.messages);
        renderUserList(data.result.users);
      },
      set_sync_state: () => setPlayerState(data.result),
      send_chat_message: () => addChatMessage(data.result.username, data.result.message),
      update_users: () => renderUserList(data.result.users),
      create_room: () => sendWebSocketMessage("get_rooms", {}),
      get_movie: () => {
        if (data.result.hls_playlist) initializeVideoPlayer(data.result.hls_playlist);
      },
      user_joined: () => {
        addChatMessage("System", `${data.result.username} joined the room.`);
        renderUserList(data.result.users);
        createNotification(`User ${data.result.username} joined the room.`, "success");
      },
      user_left: () => {
        addChatMessage("System", `${data.result.username} left the room.`);
        renderUserList(data.result.users);
        createNotification(`User ${data.result.username} left the room.`, "warning");
      },
      notification: () => {
        // Предполагается, что сервер отправляет уведомления с полем 'message' и 'level'
        const { message, level } = data.result;
        createNotification(message, level.toLowerCase());
      },
    };
    (handlers[data.result.type] || (() => console.log("Unknown result type:", data.result.type)))();
  } else if (data.error) {
    console.error("RPC Error:", data.error);
    createNotification(`Error: ${data.error.message}`, "error");
  }
}

// Debounce for syncing
const debounce = (func, delay) => {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => func(...args), delay);
  };
};
const debouncedSyncPlayerState = debounce(syncPlayerState, 300);

function syncPlayerState(isPlaying) {
  if (isSyncing || !currentRoomId) return;
  const currentTime = DOM.videoPlayer.currentTime;
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

function setPlayerState(state) {
  if (!state) return;
  isSyncing = true;

  const serverTime = parseFloat(state.current_time || 0);
  const serverPlaying = state.is_playing;

  if (Math.abs(DOM.videoPlayer.currentTime - serverTime) > 1) {
    DOM.videoPlayer.currentTime = serverTime;
  }
  if (serverPlaying && DOM.videoPlayer.paused) {
    DOM.videoPlayer.play();
  } else if (!serverPlaying && !DOM.videoPlayer.paused) {
    DOM.videoPlayer.pause();
  }

  setTimeout(() => (isSyncing = false), 500);
}

// ============== VIDEO / CHAT / ROOMS =================
function initializeVideoPlayer(hlsUrl) {
  if (Hls.isSupported()) {
    if (hls) hls.destroy();
    hls = new Hls();
    hls.loadSource(hlsUrl);
    hls.attachMedia(DOM.videoPlayer);
    hls.on(Hls.Events.MANIFEST_PARSED, populateQualitySelector);
  } else if (DOM.videoPlayer.canPlayType("application/vnd.apple.mpegurl")) {
    DOM.videoPlayer.src = hlsUrl;
  } else {
    console.error("HLS is not supported in this browser.");
    createNotification("HLS is not supported in this browser.", "error");
  }
}

function populateQualitySelector() {
  DOM.qualitySelector.innerHTML = `<option value="auto">Auto</option>`;
  hls.levels.forEach((level, index) => {
    const option = document.createElement("option");
    option.value = index;
    option.textContent = `${level.height}p`;
    DOM.qualitySelector.appendChild(option);
  });
  DOM.qualitySelector.addEventListener("change", () => {
    hls.currentLevel = DOM.qualitySelector.value === "auto" ? -1 : parseInt(DOM.qualitySelector.value, 10);
    createNotification(`Video quality set to ${DOM.qualitySelector.options[DOM.qualitySelector.selectedIndex].text}`, "info");
  });
}

function joinRoom(roomId, movieId) {
  currentRoomId = roomId;
  console.log("Joining room:", roomId);

  sendWebSocketMessage("join_room", { room_id: roomId });
  sendWebSocketMessage("get_initial_state", { room_id: roomId });

  if (movieId) sendWebSocketMessage("get_movie", { movie_id: movieId });

  createNotification(`You have joined room ${roomId}.`, "success");
}

setInterval(() => {
  if (!currentRoomId) return;
  debouncedSyncPlayerState(!DOM.videoPlayer.paused);
}, 10000);

function updateChatMessages(messages) {
  DOM.chatMessages.innerHTML = "";
  messages.forEach((msg) => {
    const username = Object.keys(msg)[0];
    const message = msg[username];
    addChatMessage(username, message);
  });
}

function addChatMessage(username, message) {
  const messageElement = document.createElement("div");
  messageElement.textContent = `${username || "Anonymous"}: ${message || "No message"}`;
  DOM.chatMessages.appendChild(messageElement);
  DOM.chatMessages.scrollTop = DOM.chatMessages.scrollHeight;
}

function renderUserList(users) {
  DOM.userListItems.innerHTML = "";
  users.forEach((user) => {
    const li = document.createElement("li");
    li.textContent = user.username || "Anonymous";
    DOM.userListItems.appendChild(li);
  });
}

function renderRoomList(rooms) {
  DOM.roomListItems.innerHTML = "";
  rooms.forEach((room) => {
    const li = document.createElement("li");
    li.textContent = `Room: ${room.room_id} (Type: ${room.room_type}, Max: ${room.max_users})`;
    li.addEventListener("click", () => joinRoom(room.room_id, room.movie_id));
    DOM.roomListItems.appendChild(li);
  });
}

// =================== NOTIFICATIONS ===================

// Создание уведомления
function createNotification(message, type = "info") {
  const container = DOM.notificationContainer;

  const notification = document.createElement("div");
  notification.classList.add("notification", type);

  // Добавление кнопки закрытия
  const closeBtn = document.createElement("button");
  closeBtn.classList.add("close-btn");
  closeBtn.innerHTML = "&times;";
  closeBtn.onclick = () => {
    container.removeChild(notification);
  };

  // Добавление сообщения и кнопки в уведомление
  notification.innerHTML = message;
  notification.appendChild(closeBtn);

  container.appendChild(notification);

  // Автоматическое удаление уведомления через 5 секунд
  setTimeout(() => {
    if (container.contains(notification)) {
      container.removeChild(notification);
    }
  }, 5000);
}

// Пример отправки уведомления вручную (можно удалить или использовать по необходимости)
DOM.sendButton.addEventListener("click", () => {
  const message = DOM.chatInput.value.trim();
  if (message && currentRoomId) {
    sendWebSocketMessage("send_chat_message", {
      room_id: currentRoomId,
      message,
    });
    addChatMessage("You", message); // Отображение отправленного сообщения
    DOM.chatInput.value = "";
  }
});


DOM.videoPlayer.addEventListener("play", () => debouncedSyncPlayerState(true));
DOM.videoPlayer.addEventListener("pause", () => debouncedSyncPlayerState(false));
DOM.videoPlayer.addEventListener("seeked", () => debouncedSyncPlayerState(!DOM.videoPlayer.paused));

DOM.createRoomForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    console.error("WebSocket is not connected. Can't create room.");
    return;
  }
  const roomName = document.getElementById("room-name").value.trim();
  const movieId = document.getElementById("movie-id").value.trim();
  const roomType = document.getElementById("room-type").value;
  const maxUsers = document.getElementById("max-users").value;

  sendWebSocketMessage("create_room", {
    room_id: roomName,
    movie_id: movieId,
    room_type: roomType,
    room_owner: 1,
    max_users: parseInt(maxUsers, 10),
  });
  DOM.createRoomForm.reset();
});


// INIT APP
function initializeApp() {
  initializeWebSocket();
}
