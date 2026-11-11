const reportUrl = "/api/optimization";
const refreshButton = document.querySelector("#refresh-dashboard");

function setText(selector, value) {
  document.querySelector(selector).textContent = value;
}

function formatNumber(value) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(value);
}

function formatBytes(value) {
  return `${formatNumber(value)} bytes`;
}

function setMeasurementUnavailable(message) {
  document.querySelector("#measurement-alert").textContent = message;
  document.querySelector("#measurement-alert").hidden = false;
  setText("#measurement-time", "Report unavailable");
  setText("#baseline-tag", "No Docker measurement report");
  setText("#optimized-tag", "No Docker measurement report");
}

function renderMeasurements(report) {
  document.querySelector("#measurement-alert").hidden = true;
  setText("#measurement-time", new Date(report.generated_at).toLocaleString());
  setText("#baseline-size", `${formatNumber(report.baseline_size_mb)} MB`);
  setText("#baseline-tag", report.baseline_image);
  setText("#optimized-size", `${formatNumber(report.optimized_size_mb)} MB`);
  setText("#optimized-tag", report.optimized_image);
  setText("#saved-size", `${formatNumber(report.saved_mb)} MB`);
  setText("#saved-bytes", `${formatBytes(report.saved_bytes)} · ${formatNumber(report.saved_mib)} MiB`);
  setText("#reduction", `${formatNumber(report.reduction_percent)}%`);
  setText("#baseline-chart-size", `${formatNumber(report.baseline_size_mb)} MB`);
  setText("#optimized-chart-size", `${formatNumber(report.optimized_size_mb)} MB`);
  setText("#baseline-mib", `${formatNumber(report.baseline_size_mib)} MiB`);
  setText("#optimized-mib", `${formatNumber(report.optimized_size_mib)} MiB`);

  const optimizedWidth = Math.min(100, Math.max(0, report.optimized_size_bytes / report.baseline_size_bytes * 100));
  document.querySelector("#baseline-bar").style.width = "100%";
  document.querySelector("#optimized-bar").style.width = `${optimizedWidth}%`;
  const action = report.saved_bytes >= 0 ? "smaller" : "larger";
  setText("#comparison-summary", `${formatNumber(Math.abs(report.saved_mb))} MB ${action} · ${formatNumber(report.reduction_percent)}% relative size change`);
}

function updateServiceStatus(prefix, healthy, detail) {
  const badge = document.querySelector(`#${prefix}-status`);
  badge.classList.remove("status-ok", "status-error", "status-unknown");
  badge.classList.add(healthy ? "status-ok" : "status-error");
  badge.textContent = healthy ? "OPERATIONAL" : "UNAVAILABLE";
  const indicator = document.querySelector(`#${prefix}-indicator`);
  indicator.classList.remove("status-ok", "status-error");
  indicator.classList.add(healthy ? "status-ok" : "status-error");
  setText(`#${prefix}-status-detail`, detail);
}

async function checkEndpoint(path) {
  try {
    const response = await fetch(path, { cache: "no-store" });
    const body = await response.json();
    return { healthy: response.ok, body };
  } catch {
    return { healthy: false, body: null };
  }
}

async function refreshHealth() {
  const [appHealth, databaseHealth] = await Promise.all([
    checkEndpoint("/health"),
    checkEndpoint("/ready"),
  ]);
  updateServiceStatus(
    "app",
    appHealth.healthy,
    appHealth.healthy ? "HTTP health check passed" : "Health endpoint unavailable",
  );
  updateServiceStatus(
    "db",
    databaseHealth.healthy,
    databaseHealth.body?.database === "connected" ? "PostgreSQL connection ready" : "PostgreSQL connection unavailable",
  );
  setText("#last-checked", `Last checked ${new Date().toLocaleTimeString()}`);
}

async function refreshDashboard() {
  refreshButton.disabled = true;
  try {
    const response = await fetch(reportUrl, { cache: "no-store" });
    const report = await response.json();
    if (!response.ok || !report.available) {
      setMeasurementUnavailable(report.message || "Docker image measurements could not be loaded.");
    } else {
      renderMeasurements(report);
    }
  } catch {
    setMeasurementUnavailable("Docker image measurements could not be loaded. Check the report file and try again.");
  }

  await refreshHealth();
  refreshButton.disabled = false;
}

refreshButton.addEventListener("click", refreshDashboard);
refreshDashboard();
window.setInterval(refreshHealth, 30_000);

const navigationLinks = document.querySelectorAll(".nav-link");
navigationLinks.forEach((link) => {
  link.addEventListener("click", () => {
    navigationLinks.forEach((item) => item.classList.remove("active"));
    link.classList.add("active");
  });
});
