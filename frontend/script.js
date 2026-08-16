'use strict';

/* ───────── CONFIG ───────── */
const API_URL = "http://localhost:8000/ask";
const API_BASE = "http://localhost:8000";

/* ───────── STORAGE KEY ───────── */
const STORAGE_KEY = "prepMind_chats";
const NOTES_KEY = "prepMind_notes";

/* ───────── STATE ───────── */
let currentChatId = null;
let isTyping = false;
let token = localStorage.getItem("token");
let selectedImage = null;
/* ───────── DOM ───────── */
const $ = id => document.getElementById(id);

const dom = {
  chatInput: $('chatInput'),
  sendBtn: $('sendBtn'),
  chatMessages: $('chatMessages'),
  hero: $('hero'),
  suggestions: $('suggestions'),
  chatHistoryList: $('chatHistoryList'),
  newChatBtn: $('newChatBtn'),
  notesGrid: $('notesGrid')
};
const imageInput = document.getElementById("imageUpload");

imageInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;

  selectedImage = file;

  showToast("📷 Image selected");
});
/* ───────── AUTH ───────── */
async function signup(email, password) {
  await fetch(`${API_BASE}/auth/signup`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({email, password})
  });
  alert("Signup successful ✅");
}

async function login(email, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({email, password})
  });

  const data = await res.json();

  if (data.access_token) {
    token = data.access_token;
    localStorage.setItem("token", token);
    alert("Login successful 🚀");
    location.reload();
  } else {
    alert("Login failed ❌");
  }
}

/* ───────── STORAGE ───────── */

function getChats() {
  return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
}

function saveChats(chats) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(chats));
}
async function fetchChats() {
  const res = await fetch(`${API_BASE}/chat/`, {
    headers: {
      "Authorization": "Bearer " + token
    }
  });

  return await res.json();
}

async function fetchMessages(chatId) {
  const res = await fetch(`${API_BASE}/chat/${chatId}`, {
    headers: {
      "Authorization": "Bearer " + token
    }
  });

  return await res.json();
}

/* ───────── NOTES ───────── */
/* ───────── NOTES (BACKEND) ───────── */

/* ───────── TEMP NOTES FIX (IMPORTANT) ───────── */
async function fetchNotes() {
  const res = await fetch(`${API_BASE}/notes/`, {
    headers: {
      "Authorization": "Bearer " + token
    }
  });

  return await res.json();
}

function saveNotes(notes) {
  localStorage.setItem(NOTES_KEY, JSON.stringify(notes));
}









async function addNote(text) {
  if (!text || text.trim() === "") return;

  const res = await fetch(`${API_BASE}/notes/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",   // ✅ IMPORTANT
      "Authorization": "Bearer " + token
    },
    body: JSON.stringify({
      text: text   // ✅ MATCH BACKEND EXPECTATION
    })
  });

  console.log("📡 NOTE STATUS:", res.status);

  if (!res.ok) {
    const err = await res.text();
    console.error("❌ NOTE ERROR:", err);
  }
}

async function removeNote(id) {
  await fetch(`${API_BASE}/notes/${id}`, {
    method: "DELETE",
    headers: {
      "Authorization": "Bearer " + token
    }
  });
}

async function isBookmarked(text) {
  const notes = await fetchNotes();
  return notes.some(n => n.text === text);
}
async function getNoteByText(text) {
  const notes = await fetchNotes();
  return notes.find(n => n.text === text);
}
/* ───────── NOTES UI ───────── */
async function renderNotes() {
  if (!token) return;

  const notes = await fetchNotes();

  const badge = document.getElementById("notesBadge");
  if (badge) badge.innerText = notes.length;

  if (!dom.notesGrid) return;

  dom.notesGrid.innerHTML = '';

  if (notes.length === 0) {
    dom.notesGrid.innerHTML = `<p style="text-align:center;">⭐ No notes yet</p>`;
    return;
  }

  notes.forEach(note => {
    const card = document.createElement('div');
    card.className = 'note-card';

    card.innerHTML = `
      <div class="note-card-text">${note.text}</div>
      <div class="note-card-date">${new Date().toLocaleString()}</div>
      <button class="note-delete-btn">❌ Remove</button>
    `;

    card.querySelector('.note-delete-btn').onclick = async () => {
      await fetch(`${API_BASE}/notes/${note.id}`, {
        method: "DELETE",
        headers: {
          "Authorization": "Bearer " + token
        }
      });

      renderNotes();
      refreshAllStars();
    };

    dom.notesGrid.appendChild(card);
  });
}

/* ───────── UTIL ───────── */
function genId() {
  return '_' + Math.random().toString(36).slice(2, 10);
}

function scrollToBottom() {
  dom.chatMessages.scrollTop = dom.chatMessages.scrollHeight;
}

function formatTime(ts) {
  return new Date(ts).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit'
  });
}
function showToast(message) {
  const toast = document.getElementById("toast");
  if (!toast) return;

  toast.innerText = message;
  toast.classList.add("show");

  setTimeout(() => {
    toast.classList.remove("show");
  }, 2000);
}
/* ───────── CHAT INIT ───────── */
function initChat() {
  currentChatId = null;

  // ✅ RESET IMAGE STATE
  selectedImage = null;

  const imageInput = document.getElementById("imageUpload");
  if (imageInput) imageInput.value = "";

  // 🔥 UI SWITCH
  document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));
  document.getElementById('section-chat').classList.add('active');

  document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
  document.querySelector('[data-section="chat"]').classList.add('active');

  dom.chatMessages.innerHTML = '';
  dom.hero.style.display = 'none';

  renderHistory();
}

/* ───────── SAVE MESSAGE ───────── */
function saveMessage(role, text) {
  const chats = getChats();
  const chat = chats[0]; // latest chat

  if (!chat) return;

  chat.messages.push({ role, text });

  if (chat.messages.length === 1) {
    chat.title = text.slice(0, 30);
  }

  saveChats(chats);
}

/* ───────── LOAD CHAT ───────── */
async function loadChat(chatId) {
  if (isTyping) return;

  currentChatId = chatId;

  dom.chatMessages.innerHTML = '';
  dom.hero.style.display = 'none';

  const messages = await fetchMessages(chatId);

  messages.forEach(msg => {
    appendMessage(msg.role, msg.text, false);
  });

  refreshAllStars();
}

/* ───────── HISTORY UI (FIXED DELETE BACK) ───────── */
async function renderHistory() {
  try {
    if (!token) {
      dom.chatHistoryList.innerHTML = '<p style="text-align:center;">Login required</p>';
      return;
    }

    const res = await fetch(`${API_BASE}/chat/`, {
      headers: {
        "Authorization": "Bearer " + token
      }
    });

    let chats = await res.json();

// 🔥 SORT BY LATEST UPDATED (DESC)


    dom.chatHistoryList.innerHTML = '';

    if (!chats.length) {
      dom.chatHistoryList.innerHTML = '<p style="text-align:center;">No chats yet</p>';
      return;
    }

    chats.forEach(chat => {
      const item = document.createElement('div');
      item.className = 'history-item';

      const title = document.createElement('span');
      title.className = 'history-title';
      title.textContent = chat.title || "New Chat";

      const delBtn = document.createElement('button');
      delBtn.className = 'history-delete';
      delBtn.textContent = '❌';

      // 👉 LOAD CHAT
      item.addEventListener('click', async () => {
        // 🔥 FORCE SWITCH TO CHAT SECTION
        document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));
        document.getElementById('section-chat').classList.add('active');
      
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        document.querySelector('[data-section="chat"]').classList.add('active');
      
        await loadChat(chat.id);
      });
      // 👉 DELETE CHAT (BACKEND)
      delBtn.addEventListener('click', async (e) => {
        e.stopPropagation();

        if (!confirm("Delete this chat?")) return;

        try {
          await fetch(`${API_BASE}/chat/${chat.id}`, {
            method: "DELETE",
            headers: {
              "Authorization": "Bearer " + token
            }
          });

          renderHistory();

          if (currentChatId === chat.id) {
            currentChatId = null;
            dom.chatMessages.innerHTML = '';
            dom.hero.style.display = 'block';
          }

        } catch (err) {
          console.error(err);
          alert("Delete failed ❌");
        }
      });

      item.appendChild(title);
      item.appendChild(delBtn);
      dom.chatHistoryList.appendChild(item);
    });

  } catch (err) {
    console.error(err);
    dom.chatHistoryList.innerHTML = '<p style="text-align:center;">Error loading chats</p>';
  }
}

/* ───────── SEND MESSAGE ───────── */
async function sendMessage() {
  const text = dom.chatInput.value.trim();
  if ((!text && !selectedImage) || isTyping) return;

  if (!token) {
    alert("Please login first");
    return;
  }

  dom.chatInput.value = "";

  appendMessage("user", text, true, selectedImage); // keep


  

  showTypingIndicator();
  await callBackend(text, selectedImage);
  selectedImage = null; // reset after sending
}

/* ───────── APPEND MESSAGE ───────── */
function appendMessage(role, text, save = true, imageFile = null){
  const ts = Date.now();

  const row = document.createElement('div');
  row.className = `msg-row ${role}`;

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = role === "user" ? "U" : "PM";

  const body = document.createElement('div');
  body.className = 'msg-body';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.innerHTML = (text || "").replace(/\n/g, "<br/>");
  // 🖼️ SHOW IMAGE (USER SIDE)
  if (role === "user" && imageFile) {
    const img = document.createElement("img");
    img.src = URL.createObjectURL(imageFile);
    img.className = "msg-img";
    bubble.prepend(img);
  }

  bubble.setAttribute("data-raw", text || "");

  const meta = document.createElement('div');
  meta.className = 'msg-meta';

  const time = document.createElement('span');
  time.className = 'msg-time';
  time.textContent = formatTime(ts);

  meta.appendChild(time);

  if (role === "ai") {
    const bookmark = document.createElement('button');
    bookmark.className = "bookmark-btn";
  
    bookmark.innerHTML = "☆";
  
    // 🔥 Sync star on load
    setTimeout(async () => {
      if (await isBookmarked(text)) {
        bookmark.innerHTML = "⭐";
      }
    }, 0);
  
    // 🔥 TOGGLE LOGIC
    bookmark.onclick = async () => {
      const raw = bubble.getAttribute("data-raw");
  
      const existingNote = await getNoteByText(raw);
  
      if (existingNote) {
        // ❌ REMOVE
        await removeNote(existingNote.id);
        bookmark.innerHTML = "☆";
      } else {
        // ✅ ADD
        await addNote(raw);
        bookmark.innerHTML = "⭐";
      }
  
      await renderNotes();
    };
  
    meta.appendChild(bookmark);
  }

  body.appendChild(bubble);
  body.appendChild(meta);

  row.appendChild(avatar);
  row.appendChild(body);

  dom.chatMessages.appendChild(row);
  dom.hero.classList.add("hidden");
  scrollToBottom();

  
}

/* ───────── STAR SYNC ───────── */
async function refreshAllStars() {
  const notes = await fetchNotes();

  document.querySelectorAll('.bookmark-btn').forEach(btn => {
    const bubble = btn.closest('.msg-body').querySelector('.msg-bubble');
    const raw = bubble.getAttribute("data-raw");

    const found = notes.find(n => n.text === raw);
    btn.innerHTML = found ? "⭐" : "☆";
  });
}

/* ───────── TYPING ───────── */
let typingEl = null;

function showTypingIndicator() {
  isTyping = true;

  const row = document.createElement('div');
  row.className = 'msg-row ai';

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = 'PM';

  const body = document.createElement('div');
  body.className = 'msg-body';

  const indicator = document.createElement('div');
  indicator.className = 'typing-indicator';
  indicator.innerHTML = "Thinking...";

  body.appendChild(indicator);
  row.appendChild(avatar);
  row.appendChild(body);

  dom.chatMessages.appendChild(row);
  typingEl = row;

  scrollToBottom();
}

function removeTypingIndicator() {
  if (typingEl) typingEl.remove();
  typingEl = null;
  isTyping = false;
}

/* ───────── BACKEND FIXED ───────── */
async function callBackend(question, imageFile = null) {
  try {
    let res;

    if (imageFile) {
      // 📷 IMAGE + TEXT
      const formData = new FormData();
      formData.append("question", question);
      formData.append("chat_id", currentChatId || "");
      formData.append("file", imageFile);

      res = await fetch(API_URL, {
        method: "POST",
        headers: {
          ...(token ? { "Authorization": "Bearer " + token } : {})
        },
        body: formData
      });

    } else {
      const formData = new FormData();
formData.append("question", question || "");
formData.append("chat_id", currentChatId || "");

if (imageFile) {
  formData.append("file", imageFile);
}

res = await fetch(API_URL, {
  method: "POST",
  headers: {
    ...(token ? { "Authorization": "Bearer " + token } : {})
  },
  body: formData
});
    }

    const data = await res.json();

    removeTypingIndicator();

    if (data.chat_id) currentChatId = data.chat_id;

    let finalAnswer = data.answer || "No response";

// 📘 Add source information
if (data.sources && data.sources.length > 0) {
  finalAnswer += "\n\n📘 Source:\n";

  data.sources.forEach(src => {
    finalAnswer += `• ${src.file} (Page: ${src.page})\n`;
  });
}

appendMessage("ai", finalAnswer);

    await renderHistory();

  } catch (err) {
    console.error(err);
    removeTypingIndicator();
    appendMessage("ai", "❌ Error processing request");
  }
}

/* ───────── NAVIGATION FIX (RESTORED) ───────── */
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', async (e) => {
    e.preventDefault(); // ✅ important

    const section = item.getAttribute('data-section');

    // 🔥 FORCE CLEAR UI FIRST
    dom.chatMessages.innerHTML = '';

    // UI switch
    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    item.classList.add('active');

    document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));

    const target = document.getElementById(`section-${section}`);
    if (target) target.classList.add('active');

    // 🔥 SECTION LOGIC
    if (section === "notes") {
      await renderNotes();
    }

    if (section === "history") {
      await renderHistory();
    }

    if (section === "chat") {
      if (currentChatId) {
        dom.hero.classList.add("hidden");   // ✅ hide hero
        await loadChat(currentChatId);
      } else {
        dom.hero.classList.remove("hidden"); // ✅ show hero
      }
    }
  });
});
/* ───────── EVENTS ───────── */
dom.sendBtn.addEventListener("click", sendMessage);

dom.chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

dom.newChatBtn.addEventListener("click", initChat);

/* ───────── INIT ───────── */
renderHistory();
renderNotes();
if (currentChatId) {
  dom.hero.classList.add("hidden");
}
console.log("🔥 FINAL STABLE VERSION 🚀");
