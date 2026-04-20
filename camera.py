import cv2
import threading
import time
import numpy as np


class VideoCamera(object):
    def __init__(self):
        print("[CAMERA] Initializing...")
        self.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.video.isOpened():
            self.video = cv2.VideoCapture(0)
        if not self.video.isOpened():
            self.video = cv2.VideoCapture(1)

        self.lock = threading.Lock()
        self.current_frame = None
        self.is_running = True

        self.thread = threading.Thread(target=self.update_frames)
        self.thread.daemon = True
        self.thread.start()

    def update_frames(self):
        while self.is_running:
            if self.video.isOpened():
                success, frame = self.video.read()
                if success:
                    frame = cv2.resize(frame, (640, 480))
                    with self.lock:
                        self.current_frame = frame
                else:
                    self.video.release()
                    time.sleep(1)
                    self.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
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
