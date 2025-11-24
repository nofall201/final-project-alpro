const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const lastResult = document.getElementById("last-result");
const lastConfidence = document.getElementById("last-confidence");
const errorBox = document.getElementById("error");

let stream;
let timer;

async function initCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
  } catch (err) {
    errorBox.textContent = `Cannot access webcam: ${err.message}`;
  }
}

function captureFrame() {
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL("image/jpeg");
}

async function sendFrame() {
  const image = captureFrame();
  const site = document.getElementById("site").value || "Unknown";
  try {
    const res = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image, site }),
    });
    if (!res.ok) throw new Error(`Request failed with ${res.status}`);
    const data = await res.json();
    lastResult.textContent = data.result;
    lastConfidence.textContent = data.confidence;
    errorBox.textContent = "";
  } catch (err) {
    errorBox.textContent = err.message;
  }
}

function startSending() {
  const intervalSeconds = parseInt(document.getElementById("interval").value, 10) || 5;
  clearInterval(timer);
  sendFrame(); // send once immediately
  timer = setInterval(sendFrame, intervalSeconds * 1000);
}

function stopSending() {
  clearInterval(timer);
}

document.getElementById("start").addEventListener("click", startSending);
document.getElementById("stop").addEventListener("click", stopSending);

initCamera();
