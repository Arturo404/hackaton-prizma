import cv2
import numpy as np
import math


class DroneGlobalTracker:
    def __init__(self, drone_w, drone_h, focal_mm, sensor_w_mm, img_w, img_h):
        # נתוני רחפן ומצלמה
        self.real_w = drone_w
        self.real_h = drone_h

        # חישוב מטריצת מצלמה (K)
        f_px = (focal_mm / sensor_w_mm) * img_w
        self.K = np.array([
            [f_px, 0, img_w / 2],
            [0, f_px, img_h / 2],
            [0, 0, 1]
        ], dtype=np.float32)

        # מודל רחפן בתלת-ממד
        self.obj_points = np.array([
            [-drone_w / 2, drone_h / 2, 0],
            [drone_w / 2, drone_h / 2, 0],
            [drone_w / 2, -drone_h / 2, 0],
            [-drone_w / 2, -drone_h / 2, 0]
        ], dtype=np.float32)

        self.home_tvec = None

    def get_global_fix(self, pixel_points, lat_start, lon_start, azimuth_deg):
        """
        pixel_points: 4 נקודות [x,y] מהעיבוד
        lat_start, lon_start: נ"צ המראה
        azimuth_deg: זווית ראש המצלמה (0=צפון, 90=מזרח)
        """
        success, _, tvec = cv2.solvePnP(self.obj_points, np.array(pixel_points, dtype=np.float32), self.K, None)

        if not success:
            return None

        curr_x, curr_y, curr_z = tvec.flatten()

        # שמירת נקודת ייחוס (אפס) בפריים הראשון
        if self.home_tvec is None:
            self.home_tvec = (curr_x, curr_y, curr_z)
            return {"lat": lat_start, "lon": lon_start, "alt": 0.0}

        # 1. חישוב תזוזה במטרים (יחסי לנקודת ההמראה)
        dx = curr_x - self.home_tvec[0]
        dy = curr_y - self.home_tvec[1]
        altitude = curr_z - self.home_tvec[2]

        # 2. סיבוב הקואורדינטות לפי אזימוט המצלמה
        # המצלמה "מסתכלת" לשמיים, אז Y בפריים מתורגם לצפון/דרום ו-X למזרח/מערב
        rad = math.radians(azimuth_deg)
        # נוסחת סיבוב וקטור
        north_m = dy * math.cos(rad) - dx * math.sin(rad)
        east_m = dy * math.sin(rad) + dx * math.cos(rad)

        # 3. המרה לנ"צ עולמי
        # קבועים גיאודטיים בקירוב (WGS84)
        lat_step = 111132.0
        lon_step = 111132.0 * math.cos(math.radians(lat_start))

        current_lat = lat_start + (north_m / lat_step)
        current_lon = lon_start + (east_m / lon_step)

        return {
            "lat": current_lat,
            "lon": current_lon,
            "altitude": round(altitude, 3),
            "dist_from_start_m": round(math.sqrt(dx ** 2 + dy ** 2), 2)
        }

# --- דוגמה לשימוש ---
# tracker = DroneGlobalTracker(0.3, 0.3, 5.0, 6.0, 1920, 1080)
# fix = tracker.get_global_fix(points, 32.085, 34.781, 45.0) # 45 מעלות זה צפון-מזרח