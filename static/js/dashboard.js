async function fetchDashboard() {
  const res = await fetch("/api/dashboard");
  if (!res.ok) {
    document.getElementById("trend").textContent = "Error loading data";
    return;
  }
  const data = await res.json();
  document.getElementById("total-events").textContent = data.total_events;
  document.getElementById("no-helmet-ratio").textContent = data.no_helmet_ratio;
  document.getElementById("avg-confidence").textContent = data.average_confidence;

  document.getElementById("trend").textContent = JSON.stringify(
    data.trend,
    null,
    2
  );
  document.getElementById("composition").textContent = JSON.stringify(
    data.composition,
    null,
    2
  );

  const tbody = document.getElementById("recent-events");
  tbody.innerHTML = "";
  data.recent_events.forEach((evt) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${evt.created_at}</td>
      <td>${evt.result}</td>
      <td>${evt.confidence}</td>
      <td>${evt.site}</td>
      <td>${evt.image_path ? `<a href="/uploads/${evt.image_path}" target="_blank">View</a>` : ""}</td>
    `;
    tbody.appendChild(tr);
  });
}

fetchDashboard();
