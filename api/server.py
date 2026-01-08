import base64
import io

from PIL import Image
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

from api import update_flying_session, open_flying_session

app = FastAPI()
archive = []


@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        session_id = None
        while True:
            # קבלת ה-JSON מהלקוח
            data = await websocket.receive_json()

            # 1. פענוח ה-Base64 לבייטים
            img_base64 = data.get("frame")
            img_bytes = base64.b64decode(img_base64)

            # 2. המרה לאובייקט Pillow
            image = Image.open(io.BytesIO(img_bytes))

            # 3. חילוץ נתוני המטא-דאטה
            timestamp = data.get("timestamp")
            drone_width_cm = data.get("drone_width_cm")
            location = data.get("start_location")  # {lat: 32.1, lon: 34.8}

            if image is not None:
                # כאן יבוא עיבוד התמונה שלך
                print(f"Frame received at {timestamp} from {location}")
                if session_id:
                    processed_location, timestamp = update_flying_session(session_id, image, timestamp)
                else:
                    session_id, processed_location = open_flying_session(location, drone_width_cm, image)

                archive.append({"location": processed_location, "timestamp": timestamp})

                # החזרת תשובה ללקוח
                await websocket.send_json({
                    "status": "success",
                    "received_at": timestamp
                })

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")


@app.get("/")
async def health_check():
    return {"status": "healthy", "uptime": "ok"}

@app.get("/end")
async def end_connection():
    return archive, 200


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
