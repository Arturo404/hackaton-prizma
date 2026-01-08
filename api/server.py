from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import uvicorn

app = FastAPI()


@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected and ready to stream.")

    try:
        while True:
            # קבלת התמונה כבייטס (Binary Data) - הדרך היעילה ביותר
            data = await websocket.receive_bytes()

            # המרת הבייטס למערך נומפי (Numpy Array)
            nparr = np.frombuffer(data, np.uint8)

            # פענוח התמונה (Decoding)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is not None:
                # --- כאן נכנסת הפונקציה שלך לעיבוד התמונה ---
                # דוגמה: בדיקת רזולוציה
                h, w, _ = frame.shape

                # החזרת אישור או תוצאה מהירה ללקוח
                await websocket.send_json({
                    "status": "received",
                    "resolution": f"{w}x{h}"
                })

                # אופציונלי: הצגת התמונה על שרת מקומי (לצורכי דיבאג בלבד)
                # cv2.imshow("Server Stream", frame)
                # cv2.waitKey(1)
            else:
                await websocket.send_json({"error": "Failed to decode image"})

    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)