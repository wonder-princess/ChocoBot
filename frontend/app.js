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
      history = data.history;
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

// ===== デュエット =====
const duetStartBtn = document.getElementById("duet-start-btn");
const duetTopicInput = document.getElementById("duet-topic-input");
const duetTopicEl = document.getElementById("duet-topic");
const duetOutputEl = document.getElementById("duet-output");

if (duetStartBtn) {
  duetStartBtn.addEventListener("click", async () => {
    duetStartBtn.disabled = true;
    duetTopicEl.textContent = "";
    duetOutputEl.textContent = "";
    duetOutputEl.innerHTML = "デュエット実行中...";

    const topicText = duetTopicInput.value.trim();
    const payload = {
      topic: topicText || null,
      // max_turns を画面から指定したくなったらここに追加
      // max_turns: 5,
    };

    try {
      const res = await fetch("/api/duet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        duetOutputEl.textContent = `エラーが発生しました: ${res.statusText}`;
        return;
      }

      const data = await res.json();

      duetTopicEl.textContent = `テーマ: ${data.topic}`;
      duetOutputEl.innerHTML = "";

      data.turns.forEach((t) => {
        const line = document.createElement("div");

        // Bot 名で CSS クラスを変える！
        line.className = `duet-line ${t.speaker}`;

        const speakerSpan = document.createElement("span");
        speakerSpan.className = "speaker";
        speakerSpan.textContent = `${t.speaker}:`;

        const contentSpan = document.createElement("span");
        contentSpan.textContent = ` ${t.content}`;

        line.appendChild(speakerSpan);
        line.appendChild(contentSpan);
        duetOutputEl.appendChild(line);
      });

    } catch (err) {
      console.error(err);
      duetOutputEl.textContent = "通信エラーが発生しました。";
    } finally {
      duetStartBtn.disabled = false;
    }
  });
}
