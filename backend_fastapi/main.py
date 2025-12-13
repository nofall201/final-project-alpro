from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from ultralytics import YOLO
import base64, numpy as np, cv2, os
from db import init_db, save_detection, get_latest_detection, get_all_detections, get_detections_by_date

app = FastAPI()
model = YOLO("best.pt")
init_db()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("screenshots", exist_ok=True)
last_capture = datetime.min


@app.websocket("/yolo")
async def detect_ws(ws: WebSocket):
    await ws.accept()
    global last_capture

    while True:
        raw = await ws.receive_text()

        # decode frame
        _, encoded = raw.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

        results = model(frame)[0]

        classes_raw = [model.names[int(c)] for c in results.boxes.cls]
        boxes = results.boxes.xyxy.tolist()

        # NORMALISASI CLASS
        classes = []
        for c in classes_raw:
            if c == "head":
                classes.append("person")
            else:
                classes.append(c)

        # hitung deteksi
        person_count = classes.count("person")
        helmet_count = classes.count("helmet")
        violation_count = max(person_count - helmet_count, 0)

        screenshot_path = None
        now = datetime.now()

        if violation_count > 0 and (now - last_capture).total_seconds() >= 5:
            fname = f"violation_{now:%Y%m%d_%H%M%S}.jpg"
            save_path = os.path.join("screenshots", fname)
            cv2.imwrite(save_path, frame)
            screenshot_path = f"screenshots/{fname}"

            save_detection(person_count, violation_count, screenshot_path)
            last_capture = now

        # kirim JSON ke frontend
        await ws.send_json({
            "person": person_count,
            "violation": violation_count,
            "screenshot": screenshot_path,
            "boxes": boxes,
            "classes": classes
        })


# API
@app.get("/api/latest")
def latest():
    return get_latest_detection()

@app.get("/api/list")
def all_list():
    return get_all_detections()

@app.get("/api/filter")
def filter_date(start: str, end: str):
    return get_detections_by_date(
        datetime.fromisoformat(start),
        datetime.fromisoformat(end)
    )
