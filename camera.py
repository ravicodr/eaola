import cv2
import threading
import time
import numpy as np
import platform


class VideoCamera(object):
    def __init__(self):
        print("[CAMERA] Initializing...")
        self.lock = threading.Lock()
        self.current_frame = None
        self.is_running = True

        # Try to open camera — skip on Linux servers (no physical camera)
        self.video = None
        try:
            if platform.system() == 'Windows':
                cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(0)
            if cap.isOpened():
                self.video = cap
                print("[CAMERA] Camera opened successfully.")
            else:
                cap.release()
                print("[CAMERA] No camera found — running in no-camera mode.")
        except Exception as e:
            print(f"[CAMERA] Camera init failed: {e} — running in no-camera mode.")

        if self.video:
            self.thread = threading.Thread(target=self.update_frames)
            self.thread.daemon = True
            self.thread.start()

    def update_frames(self):
        while self.is_running and self.video:
            if self.video.isOpened():
                success, frame = self.video.read()
                if success:
                    frame = cv2.resize(frame, (640, 480))
                    with self.lock:
                        self.current_frame = frame
                else:
                    time.sleep(1)
            else:
                time.sleep(1)
            time.sleep(0.01)

    def get_frame(self):
        with self.lock:
            if self.current_frame is None:
                blank = np.zeros((480, 640, 3), np.uint8)
                cv2.putText(blank, "Starting Camera...", (180, 240),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                return blank
            return self.current_frame.copy()

    def __del__(self):
        self.is_running = False
        if self.video.isOpened():
            self.video.release()


# Single global camera instance shared across the app
global_camera = VideoCamera()
