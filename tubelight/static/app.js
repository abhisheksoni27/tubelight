let queryInput = null;
let startDateInput = null;
let endDateInput = null;
let levelSelect = null;
let limitSelect = null;
let refreshButton = null;
let updatedAt = null;
let recordCount = null;
let logTableBody = null;
let liveToggle = null;
let autoScrollToggle = null;
let refreshTimer = null;

function initDom() {
  queryInput = document.getElementById("queryInput");
  startDateInput = document.getElementById("startDateInput");
  endDateInput = document.getElementById("endDateInput");
  levelSelect = document.getElementById("levelSelect");
  limitSelect = document.getElementById("limitSelect");
  refreshButton = document.getElementById("refreshButton");
  updatedAt = document.getElementById("updatedAt");
  recordCount = document.getElementById("recordCount");
  logTableBody = document.getElementById("logTableBody");
  liveToggle = document.getElementById("liveToggle");
  autoScrollToggle = document.getElementById("autoScrollToggle");

  const missing = [];
  if (!queryInput) missing.push("queryInput");
  if (!levelSelect) missing.push("levelSelect");
  if (!limitSelect) missing.push("limitSelect");
  if (!refreshButton) missing.push("refreshButton");
  if (!logTableBody) missing.push("logTableBody");

  if (missing.length > 0) {
    console.error(
      "Missing required DOM elements for the log viewer:",
      missing.join(", "),
    );
    return false;
  }

  if (queryInput) {
    queryInput.addEventListener("input", () => fetchLogs());
  }
  if (startDateInput) {
    startDateInput.addEventListener("change", () => fetchLogs());
  }
  if (endDateInput) {
    endDateInput.addEventListener("change", () => fetchLogs());
  }
  if (levelSelect) {
    levelSelect.addEventListener("change", () => fetchLogs());
  }
  if (limitSelect) {
    limitSelect.addEventListener("change", () => fetchLogs());
  }
  if (refreshButton) {
    refreshButton.addEventListener("click", () => fetchLogs());
  }
  if (liveToggle) {
    liveToggle.addEventListener("change", updatePolling);
  }
  if (autoScrollToggle) {
    autoScrollToggle.addEventListener("change", () => {
      if (autoScrollToggle.checked) {
        scrollToBottom();
      }
    });
  }

  return true;
}

function formatSource(file, line) {
  if (!file) {
    return "—";
  }
  return `${file}${line ? `:${line}` : ""}`;
}

function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function buildRow(record) {
  const row = document.createElement("tr");
  row.className = "log-row";

  row.innerHTML = `
    <td><time>${record.time || "—"}</time></td>
    <td><span class="level-chip ${record.levelClass}">${record.icon || ""}${record.level}</span></td>
    <td>${record.message || "—"}</td>
    <td class="source"><strong>${record.module || ""}</strong><br />${formatSource(record.file, record.line)}</td>
    <td class="context">PID ${record.process || "—"} • ${record.thread || "—"}</td>
  `;

  row.addEventListener("click", () => toggleDetailRow(row));
  return row;
}

function buildDetailRow(record) {
  const detail = document.createElement("tr");
  detail.className = "detail-row hidden";
  detail.innerHTML = `
    <td colspan="5">
      <div class="detail-panel">
        <div class="detail-row-title">Expanded log details</div>
        <pre>${escapeHtml(record.raw)}</pre>
      </div>
    </td>
  `;
  return detail;
}

function toggleDetailRow(row) {
  const next = row.nextElementSibling;
  if (!next || !next.classList.contains("detail-row")) {
    return;
  }

  next.classList.toggle("hidden");
  row.classList.toggle("expanded");
}

async function fetchConfig() {
  try {
    const response = await fetch(`/api/config`);
    const payload = await response.json();
    if (response.ok) {
      document.getElementById("logPath").textContent =
        payload.logFile || "example.log";
    }
  } catch (error) {
    console.warn("Failed to fetch config", error);
  }
}

function getDateValue(input) {
  return input.value ? input.value : undefined;
}

async function fetchLogs() {
  if (!queryInput || !levelSelect || !limitSelect || !logTableBody) {
    console.warn("Cannot fetch logs before DOM is ready.");
    return;
  }

  const params = new URLSearchParams({
    q: queryInput.value,
    level: levelSelect.value,
    limit: limitSelect.value,
  });

  const startValue = getDateValue(startDateInput);
  const endValue = getDateValue(endDateInput);

  if (startValue) {
    params.set("start", startValue);
  }
  if (endValue) {
    params.set("end", endValue);
  }

  try {
    const response = await fetch(`/api/logs?${params.toString()}`);
    const payload = await response.json();

    if (!response.ok) {
      console.error(payload);
      return;
    }

    logTableBody.innerHTML = "";
    payload.records.forEach((record) => {
      const row = buildRow(record);
      const detail = buildDetailRow(record);
      logTableBody.appendChild(row);
      logTableBody.appendChild(detail);
    });

    if (autoScrollToggle.checked) {
      scrollToBottom();
    }

    updatedAt.textContent = new Date().toLocaleTimeString();
    recordCount.textContent = payload.count;
  } catch (error) {
    console.error("Failed to fetch logs", error);
  }
}

function scrollToBottom() {
  const tableShell = document.querySelector(".table-shell");
  if (tableShell) {
    tableShell.scrollTop = tableShell.scrollHeight;
  }
}

function updatePolling() {
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }

  if (liveToggle.checked) {
    refreshTimer = setInterval(fetchLogs, 2500);
  }
}

if (queryInput) {
  queryInput.addEventListener("input", () => fetchLogs());
}
if (startDateInput) {
  startDateInput.addEventListener("change", () => fetchLogs());
}
if (endDateInput) {
  endDateInput.addEventListener("change", () => fetchLogs());
}
if (levelSelect) {
  levelSelect.addEventListener("change", () => fetchLogs());
}
if (limitSelect) {
  limitSelect.addEventListener("change", () => fetchLogs());
}
if (refreshButton) {
  refreshButton.addEventListener("click", () => fetchLogs());
}
if (liveToggle) {
  liveToggle.addEventListener("change", updatePolling);
}
if (autoScrollToggle) {
  autoScrollToggle.addEventListener("change", () => {
    if (autoScrollToggle.checked) {
      scrollToBottom();
    }
  });
}

function initializeViewer() {
  if (!initDom()) {
    return;
  }

  fetchConfig().then(fetchLogs).then(updatePolling);
}

window.addEventListener("load", initializeViewer);
