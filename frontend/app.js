// ===== タブ切り替え =====
const tabChat = document.getElementById("tab-chat");
const tabDuet = document.getElementById("tab-duet");
const viewChat = document.getElementById("view-chat");
const viewDuet = document.getElementById("view-duet");

function activateTab(target) {
  const isChat = target === "chat";
  tabChat.classList.toggle("active", isChat);
  tabDuet.classList.toggle("active", !isChat);
  viewChat.classList.toggle("active", isChat);
  viewDuet.classList.toggle("active", !isChat);
}

if (tabChat && tabDuet) {
  tabChat.addEventListener("click", () => activateTab("chat"));
  tabDuet.addEventListener("click", () => activateTab("duet"));
}

// ===== 通常チャット =====
const chatWindow = document.getElementById("chat-window");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");

let history = [];

function appendMessage(role, content) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.textContent = content;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

if (chatForm) {
  chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;

    appendMessage("user", text);
    chatForm.querySelector("button").disabled = true;

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          history: history,
        }),
      });

      if (!response.ok) {
        appendMessage(
          "assistant",
          `エラーが発生しました: ${response.statusText}`
        );
        return;
      }

      const data = await response.json();
      history = data.history || [];
      appendMessage("assistant", data.reply);
    } catch (err) {
      console.error(err);
      appendMessage("assistant", "通信エラーが発生しました。");
    } finally {
      chatForm.querySelector("button").disabled = false;
      userInput.value = "";
      userInput.focus();
    }
  });
}

// ===== デュエット（WebSocket ストリーミング） =====
const duetStartBtn = document.getElementById("duet-start-btn");
const duetTopicInput = document.getElementById("duet-topic-input");
const duetTopicEl = document.getElementById("duet-topic");
const duetOutputEl = document.getElementById("duet-output");

if (duetStartBtn) {
  duetStartBtn.addEventListener("click", () => {
    duetStartBtn.disabled = true;
    duetTopicEl.textContent = "";
    duetOutputEl.innerHTML = "";
    duetOutputEl.textContent = "デュエット実行中...";

    const topicText = duetTopicInput.value.trim();
    const protocol = location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${protocol}://${location.host}/ws/duet`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      const payload = {
        topic: topicText || null
        // max_turns を画面から指定したくなったらここに追加:
        // max_turns: 3,
      };
      ws.send(JSON.stringify(payload));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "meta") {
        duetTopicEl.textContent = `テーマ: ${data.topic}`;
        duetOutputEl.innerHTML = "";
        return;
      }

      if (data.type === "turn") {
        const line = document.createElement("div");
        line.className = `duet-line ${data.speaker}`;

        const speakerSpan = document.createElement("span");
        speakerSpan.className = "speaker";
        speakerSpan.textContent = `${data.speaker}:`;

        const contentSpan = document.createElement("span");
        contentSpan.textContent = ` ${data.content}`;

        line.appendChild(speakerSpan);
        line.appendChild(contentSpan);
        duetOutputEl.appendChild(line);
        duetOutputEl.scrollTop = duetOutputEl.scrollHeight;
        return;
      }

      if (data.type === "end") {
        duetStartBtn.disabled = false;
        ws.close();
        return;
      }

      if (data.type === "error") {
        duetOutputEl.textContent = `エラー: ${data.message || "不明なエラー"}`;
        duetStartBtn.disabled = false;
        ws.close();
        return;
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
      duetOutputEl.textContent = "WebSocket エラーが発生しました。";
      duetStartBtn.disabled = false;
    };

    ws.onclose = () => {
      duetStartBtn.disabled = false;
    };
  });
}
