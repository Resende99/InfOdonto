/* ─── TABS ────────────────────────────────────────────────────────────────── */
const tabButtons = document.querySelectorAll("[data-tab]");
const tabPanels  = document.querySelectorAll("[data-tab-panel]");

tabButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    const tab = btn.dataset.tab;
    tabButtons.forEach((b) => {
      const active = b === btn;
      b.classList.toggle("is-active", active);
      b.setAttribute("aria-selected", String(active));
    });
    tabPanels.forEach((p) => {
      p.classList.toggle("is-active", p.dataset.tabPanel === tab);
    });
  });
});

/* ─── CHAT ────────────────────────────────────────────────────────────────── */
const chatOpenBtn  = document.querySelector("[data-chat-open]");
const chatDialog   = document.querySelector("[data-chat-dialog]");
const chatCloseBtn = document.querySelector("[data-chat-close]");
const chatMessages = document.querySelector("[data-chat-messages]");
const chatInput    = document.querySelector("[data-chat-input]");
const chatSendBtn  = document.querySelector("[data-chat-send]");
const procIdInput  = document.querySelector("[data-procedimento-id]");

chatOpenBtn?.addEventListener("click", () => {
  chatDialog?.showModal?.() ?? chatDialog?.setAttribute("open", "");
});

chatCloseBtn?.addEventListener("click", () => {
  chatDialog?.close?.() ?? chatDialog?.removeAttribute("open");
});

function appendMessage(text, type) {
  if (!chatMessages) return null;
  const div = document.createElement("div");
  div.className = `chat-message ${type}`;
  div.textContent = text;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return div;
}

async function sendMessage() {
  if (!chatInput || !chatSendBtn) return;
  const message = chatInput.value.trim();
  if (!message) return;
  const procedimentoId = procIdInput?.value ?? "";
  appendMessage(message, "user");
  chatInput.value = "";
  chatSendBtn.disabled = true;
  const loadingEl = appendMessage("Consultando o assistente...", "assistant is-loading");
  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, procedimento_id: procedimentoId }),
    });
    const data = await response.json();
    loadingEl.textContent = data.message || "Não consegui responder agora.";
  } catch {
    loadingEl.textContent = "Não consegui conectar ao assistente. Tente novamente.";
  } finally {
    loadingEl.classList.remove("is-loading");
    chatSendBtn.disabled = false;
    chatInput.focus();
  }
}

chatSendBtn?.addEventListener("click", sendMessage);
chatInput?.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

/* ─── NAVEGAÇÃO SPA (apenas index.html) ───────────────────────────────────── */
const indexPage      = document.querySelector("[data-index-page]");
const contentPanel   = document.querySelector("[data-content-panel]");
const specialtyLinks = document.querySelectorAll("[data-specialty-link]");

const esc = (v) =>
  String(v)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#039;");

function renderProcedures(specialty) {
  if (!contentPanel) return;
  const cards = specialty.procedimentos.map((proc, i) => `
    <a class="procedure-card" href="/procedimento/${esc(proc.id)}">
      <span class="card-label">Procedimento ${String(i + 1).padStart(2, "0")}</span>
      <h3>${esc(proc.nome)}</h3>
      <p>${esc(proc.resumo)}</p>
      <span class="card-action">Ver orientações</span>
    </a>
  `).join("");
  contentPanel.innerHTML = `
    <div class="section-heading">
      <div>
        <span class="eyebrow">Especialidade</span>
        <h2>${esc(specialty.nome)}</h2>
      </div>
      <p>${esc(specialty.descricao)}</p>
    </div>
    <div class="procedure-grid">${cards}</div>
  `;
}

let cachedData = null;

async function loadData() {
  if (cachedData) return cachedData;
  const res = await fetch("/api/procedimentos");
  cachedData = await res.json();
  return cachedData;
}

async function selectSpecialty(id, pushState = true) {
  if (!indexPage || !contentPanel) return;
  const scrollY   = window.scrollY;
  const data      = await loadData();
  const specialty = data.especialidades.find((e) => e.id === id);
  if (!specialty) return;
  specialtyLinks.forEach((l) => l.classList.toggle("is-active", l.dataset.specialtyLink === id));
  renderProcedures(specialty);
  if (pushState) history.pushState({ specialtyId: id }, "", `/especialidade/${id}`);
  window.scrollTo({ top: scrollY, behavior: "instant" });
}

specialtyLinks.forEach((link) => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    selectSpecialty(link.dataset.specialtyLink);
  });
});

window.addEventListener("popstate", () => {
  const match = window.location.pathname.match(/^\/especialidade\/([^/]+)$/);
  if (match) selectSpecialty(match[1], false);
  else window.location.href = "/";
});