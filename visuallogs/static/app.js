const queryInput = document.getElementById("queryInput");
const levelSelect = document.getElementById("levelSelect");
const limitSelect = document.getElementById("limitSelect");
const refreshButton = document.getElementById("refreshButton");
const updatedAt = document.getElementById("updatedAt");
const recordCount = document.getElementById("recordCount");
const logTableBody = document.getElementById("logTableBody");
const liveToggle = document.getElementById("liveToggle");

let refreshTimer = null;

function formatSource(file, line) {
  if (!file) {
    return "—";
  }
  return `${file}${line ? `:${line}` : ""}`;
}

function buildRow(record) {
  const row = document.createElement("tr");

  row.innerHTML = `
    <td><time>${record.time || "—"}</time></td>
    <td><span class="level-chip ${record.levelClass}">${record.icon || ""}${record.level}</span></td>
    <td>${record.message || "—"}</td>
    <td class="source"><strong>${record.module || ""}</strong><br />${formatSource(record.file, record.line)}</td>
    <td class="context">PID ${record.process || "—"} • ${record.thread || "—"}</td>
  `;

  return row;
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

async function fetchLogs() {
  const params = new URLSearchParams({
    q: queryInput.value,
    level: levelSelect.value,
    limit: limitSelect.value,
  });

  try {
    const response = await fetch(`/api/logs?${params.toString()}`);
    const payload = await response.json();

    if (!response.ok) {
      console.error(payload);
      return;
    }

    logTableBody.innerHTML = "";
    payload.records.forEach((record) => {
      logTableBody.appendChild(buildRow(record));
    });

    updatedAt.textContent = new Date().toLocaleTimeString();
    recordCount.textContent = payload.count;
  } catch (error) {
    console.error("Failed to fetch logs", error);
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

queryInput.addEventListener("input", () => fetchLogs());
levelSelect.addEventListener("change", () => fetchLogs());
limitSelect.addEventListener("change", () => fetchLogs());
refreshButton.addEventListener("click", () => fetchLogs());
liveToggle.addEventListener("change", updatePolling);

fetchConfig().then(fetchLogs).then(updatePolling);
