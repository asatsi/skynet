document.addEventListener("DOMContentLoaded", () => {
  const messagesContainer = document.getElementById("messages-container");
  const chatForm = document.getElementById("chat-form");
  const userInput = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");
  const clearChatBtn = document.getElementById("clear-chat-btn");
  const refreshStatusBtn = document.getElementById("refresh-status-btn");
  const clearReasoningBtn = document.getElementById("clear-reasoning-btn");

  const mcpStatusBadge = document.getElementById("mcp-status-badge");
  const mcpToolsCount = document.getElementById("mcp-tools-count");
  const ollamaStatusBadge = document.getElementById("ollama-status-badge");
  const activeModelName = document.getElementById("active-model-name");
  const toolsListContainer = document.getElementById("tools-list-container");
  const toolsBadgeNum = document.getElementById("tools-badge-num");

  const reasoningTimeline = document.getElementById("reasoning-timeline");
  const thinkingBanner = document.getElementById("thinking-banner");

  let conversationHistory = [];
  let isGenerating = false;

  // Configure marked parser
  marked.setOptions({
    gfm: true,
    breaks: true,
  });

  // Check system status
  async function checkSystemStatus() {
    try {
      const res = await fetch("/api/status");
      if (res.ok) {
        const data = await res.json();
        
        // MCP Status
        if (data.mcp_connected) {
          mcpStatusBadge.className = "badge online";
          mcpStatusBadge.innerHTML = `<i class="fa-solid fa-circle-check"></i> Connected`;
          mcpToolsCount.textContent = `${data.mcp_tools_count} Tools`;
          toolsBadgeNum.textContent = data.mcp_tools_count;
        } else {
          mcpStatusBadge.className = "badge offline";
          mcpStatusBadge.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> Offline`;
        }

        // Ollama Status
        if (data.ollama_connected) {
          ollamaStatusBadge.className = "badge online";
          ollamaStatusBadge.innerHTML = `<i class="fa-solid fa-circle-check"></i> Connected`;
        } else {
          ollamaStatusBadge.className = "badge offline";
          ollamaStatusBadge.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> Offline`;
        }

        activeModelName.textContent = data.active_model || "qwen3.5:9b";
      }
    } catch (e) {
      console.error("Failed to fetch system status:", e);
    }
  }

  // Load available MCP tools into sidebar explorer
  async function loadToolsExplorer() {
    try {
      const res = await fetch("/api/tools");
      if (res.ok) {
        const data = await res.json();
        const tools = data.tools || [];
        
        if (tools.length === 0) {
          toolsListContainer.innerHTML = `<div class="tools-placeholder">No tools found or MCP server offline.</div>`;
          return;
        }

        toolsListContainer.innerHTML = tools.map(t => `
          <div class="tool-item">
            <div class="tool-name"><i class="fa-solid fa-wrench"></i> ${escapeHtml(t.name)}</div>
            <div class="tool-desc" title="${escapeHtml(t.description)}">${escapeHtml(t.description)}</div>
          </div>
        `).join("");
      }
    } catch (e) {
      toolsListContainer.innerHTML = `<div class="tools-placeholder">Error loading tools list.</div>`;
    }
  }

  // HTML Escape helper
  function escapeHtml(text) {
    if (!text) return "";
    return text.toString()
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Auto-resize textarea
  userInput.addEventListener("input", () => {
    userInput.style.height = "auto";
    userInput.style.height = (userInput.scrollHeight) + "px";
  });

  // Handle Shift + Enter vs Enter
  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!isGenerating && userInput.value.trim()) {
        chatForm.dispatchEvent(new Event("submit"));
      }
    }
  });

  // Quick Prompt Chips handler
  document.querySelectorAll(".prompt-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const promptText = chip.getAttribute("data-prompt");
      if (promptText && !isGenerating) {
        userInput.value = promptText;
        userInput.dispatchEvent(new Event("input"));
        chatForm.dispatchEvent(new Event("submit"));
      }
    });
  });

  // Clear session chat
  clearChatBtn.addEventListener("click", () => {
    conversationHistory = [];
    messagesContainer.innerHTML = `
      <div class="welcome-card glass-panel">
        <div class="welcome-icon"><i class="fa-solid fa-head-side-virus"></i></div>
        <h2>Healthcare Operations Workspace Cleared</h2>
        <p>Session history has been reset. Type a message below to start a new chat session with live reasoning trace in the right-side pane.</p>
      </div>
    `;
  });

  // Clear right-side reasoning panel
  clearReasoningBtn.addEventListener("click", () => {
    clearReasoningTimeline();
  });

  function clearReasoningTimeline() {
    reasoningTimeline.innerHTML = `
      <div class="timeline-empty">
        <i class="fa-solid fa-lightbulb"></i>
        <p>Reasoning steps will appear live in this panel as the agent processes your queries.</p>
      </div>
    `;
  }

  refreshStatusBtn.addEventListener("click", () => {
    checkSystemStatus();
    loadToolsExplorer();
  });

  // Append reasoning card to the right-side reasoning panel
  function appendReasoningStep(stepData) {
    const emptyPlaceholder = reasoningTimeline.querySelector(".timeline-empty");
    if (emptyPlaceholder) emptyPlaceholder.remove();

    const card = document.createElement("div");
    card.className = "timeline-card";
    card.innerHTML = `
      <div class="timeline-card-header">
        <span class="step-badge">Step ${stepData.step || 1}</span>
        <span class="step-title">${escapeHtml(stepData.title)}</span>
      </div>
      <div class="timeline-card-body">${escapeHtml(stepData.thought)}</div>
    `;
    reasoningTimeline.appendChild(card);
    reasoningTimeline.scrollTop = reasoningTimeline.scrollHeight;
  }

  // Form Submit / Chat Send
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = userInput.value.trim();
    if (!query || isGenerating) return;

    // Remove welcome card if present
    const welcomeCard = messagesContainer.querySelector(".welcome-card");
    if (welcomeCard) welcomeCard.remove();

    // Render User Message in center workspace
    appendUserMessage(query);
    userInput.value = "";
    userInput.style.height = "auto";
    isGenerating = true;
    sendBtn.disabled = true;

    // Show thinking indicator banner in right reasoning pane
    thinkingBanner.style.display = "flex";

    // Create Assistant Group Container in center workspace
    const assistantGroup = createAssistantGroup();
    messagesContainer.appendChild(assistantGroup.wrapper);
    scrollToBottom();

    let responseCard = null;

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: query,
          history: conversationHistory
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop(); // keep trailing incomplete chunk

        for (const line of lines) {
          if (!line.trim()) continue;
          
          let eventType = "message";
          let dataStr = "";

          const lineParts = line.split("\n");
          for (const p of lineParts) {
            if (p.startsWith("event: ")) eventType = p.replace("event: ", "").trim();
            if (p.startsWith("data: ")) dataStr = p.replace("data: ", "").trim();
          }

          if (!dataStr) continue;
          const payload = JSON.parse(dataStr);

          // Handle SSE event types
          if (eventType === "reasoning") {
            // Append reasoning step into RIGHT SIDE REASONING PANE
            appendReasoningStep(payload);

          } else if (eventType === "tool_call") {
            const toolCallCard = document.createElement("div");
            toolCallCard.className = "tool-call-card";
            toolCallCard.innerHTML = `
              <div class="tool-header">
                <span class="tool-name-tag"><i class="fa-solid fa-gear fa-spin"></i> Invoking Tool: <code>${escapeHtml(payload.tool_name)}</code></span>
                <span class="latency-tag"><i class="fa-solid fa-clock"></i> ${payload.timestamp}</span>
              </div>
              <div class="tool-body">
                <div><strong>Input Arguments:</strong></div>
                <div class="json-block">${escapeHtml(JSON.stringify(payload.arguments, null, 2))}</div>
              </div>
            `;
            assistantGroup.group.appendChild(toolCallCard);
            scrollToBottom();

          } else if (eventType === "tool_result") {
            // Find recent tool call card and append result
            const lastToolCard = assistantGroup.group.querySelector(".tool-call-card:last-of-type");
            if (lastToolCard) {
              const headerIcon = lastToolCard.querySelector(".fa-gear");
              if (headerIcon) headerIcon.className = "fa-solid fa-check-double";

              const toolBody = lastToolCard.querySelector(".tool-body");
              const resDiv = document.createElement("div");
              resDiv.innerHTML = `
                <div style="margin-top:0.4rem;"><strong>Tool Execution Output (${payload.latency_ms}ms):</strong></div>
                <div class="json-block" style="color:#64748b;">${escapeHtml(payload.result)}</div>
              `;
              toolBody.appendChild(resDiv);
            }
            scrollToBottom();

          } else if (eventType === "final_response") {
            if (!responseCard) {
              responseCard = document.createElement("div");
              responseCard.className = "assistant-response-card";
              assistantGroup.group.appendChild(responseCard);
            }
            responseCard.innerHTML = marked.parse(payload.content);
            conversationHistory.push({ role: "user", content: query });
            conversationHistory.push({ role: "assistant", content: payload.content });
            scrollToBottom();

          } else if (eventType === "error") {
            const errCard = document.createElement("div");
            errCard.className = "assistant-response-card";
            errCard.style.borderColor = "var(--danger-accent)";
            errCard.innerHTML = `<span style="color:var(--danger-accent);"><i class="fa-solid fa-triangle-exclamation"></i> <strong>Error:</strong> ${escapeHtml(payload)}</span>`;
            assistantGroup.group.appendChild(errCard);
            scrollToBottom();
          }
        }
      }

    } catch (err) {
      const errCard = document.createElement("div");
      errCard.className = "assistant-response-card";
      errCard.style.borderColor = "var(--danger-accent)";
      errCard.innerHTML = `<span style="color:var(--danger-accent);"><i class="fa-solid fa-triangle-exclamation"></i> <strong>Connection Error:</strong> ${escapeHtml(err.message)}</span>`;
      assistantGroup.group.appendChild(errCard);
    } finally {
      isGenerating = false;
      sendBtn.disabled = false;
      thinkingBanner.style.display = "none";
    }
  });

  function appendUserMessage(text) {
    const wrapper = document.createElement("div");
    wrapper.className = "message-wrapper user";
    wrapper.innerHTML = `
      <div class="user-message-card">${escapeHtml(text)}</div>
    `;
    messagesContainer.appendChild(wrapper);
  }

  function createAssistantGroup() {
    const wrapper = document.createElement("div");
    wrapper.className = "message-wrapper assistant";
    const group = document.createElement("div");
    group.className = "assistant-group";
    wrapper.appendChild(group);
    return { wrapper, group };
  }

  function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // Initial loads
  checkSystemStatus();
  loadToolsExplorer();
});
