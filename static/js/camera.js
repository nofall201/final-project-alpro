const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');

const btnToggle = document.getElementById('btn-toggle');
const placeholderText = document.getElementById('placeholder-text');
const errorMsg = document.getElementById('error-msg');

const resText = document.getElementById('res-text');
const resConf = document.getElementById('res-conf');

let isRunning = false;
let intervalId = null;
let sendInterval = 5000;

async function setupCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: 640, height: 360 }
        });
        video.srcObject = stream;
        
        video.onloadedmetadata = () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            placeholderText.style.display = 'none';
        };
    } catch (err) {
        console.error(err);
        errorMsg.innerText = 'Camera access denied. Please use HTTPS or localhost.';
    }
}

async function sendFrame() {
    if (!isRunning) return;

    if (canvas.width !== video.videoWidth && video.videoWidth > 0) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
    }

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageBase64 = canvas.toDataURL('image/jpeg', 0.8);
    const siteVal = document.getElementById('site-input').value || 'Unknown';

    try {
        const res = await fetch('/api/predict', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                image: imageBase64, 
                site: siteVal 
            })
        });

        if (!res.ok) throw new Error(Server error ${res.status});
        const data = await res.json();
        updateUI(data.result, data.confidence);
        errorMsg.innerText = '';
    } catch (err) {
        console.error(err);
    }
}

function updateUI(result, confidence) {
    if (typeof confidence === 'number') {
        confidence = confidence.toFixed(2);
    }

    resText.innerText = result || '-';
    resConf.innerText = confidence || '-';

    if (result === 'No Helmet') {
        resText.className = 'metric-value text-red';
        resConf.className = 'metric-value text-red';
    } else {
        resText.className = 'metric-value text-green';
        resConf.className = 'metric-value text-green';
    }
}

btnToggle.addEventListener('click', async () => {
    if (!isRunning) {
        await setupCamera();
        try { await video.play(); } catch(e){}
        
        isRunning = true;
        btnToggle.innerText = 'Stop';
        btnToggle.style.backgroundColor = 'var(--accent-red)';
        btnToggle.style.color = 'white';

        sendFrame(); 
        intervalId = setInterval(sendFrame, sendInterval);

    } else {
        isRunning = false;
        
        if (video.srcObject) {
            video.srcObject.getTracks().forEach(t => t.stop());
            video.srcObject = null;
        }
        
        placeholderText.style.display = 'block';
        btnToggle.innerText = 'Activate';
        btnToggle.style.backgroundColor = 'var(--accent-green)';
        btnToggle.style.color = '#1c1c36';

        clearInterval(intervalId);
    
        resText.innerText = '-';
        resConf.innerText = '-';
        resText.className = 'metric-value text-green';
    }
});

document.getElementById('btn-save').addEventListener('click', () => {
    const val = document.getElementById('interval-select').value;
    sendInterval = parseInt(val, 10) * 1000;

    if (isRunning) {
        clearInterval(intervalId);
        intervalId = setInterval(sendFrame, sendInterval);
    }

    const btn = document.getElementById('btn-save');
    const oldText = btn.innerText;
    btn.innerText = 'Saved';
    setTimeout(() => btn.innerText = oldText, 1000);
});
