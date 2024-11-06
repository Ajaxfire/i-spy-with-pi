# app.py
from flask import Flask, Response, render_template, jsonify, request
import cv2
import os
from datetime import datetime
from pathlib import Path
import threading
import time

app = Flask(__name__)

# Global variables
camera = None
picture_folder = str(Path.home() / "Pictures" / "camera_captures")
frame_buffer = None
frame_lock = threading.Lock()

# Ensure pictures directory exists
os.makedirs(picture_folder, exist_ok=True)

def get_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
        # Optimize camera settings
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Reduce resolution for better performance
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 30)  # Set FPS
        camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer size
    return camera

def update_frame_buffer():
    global frame_buffer
    while True:
        camera = get_camera()
        if camera is None:
            time.sleep(0.1)
            continue
            
        success, frame = camera.read()
        if success:
            # Optimize frame for web streaming
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if ret:
                with frame_lock:
                    frame_buffer = buffer.tobytes()
        time.sleep(0.033)  # ~30 FPS

def generate_frames():
    while True:
        with frame_lock:
            if frame_buffer is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_buffer + b'\r\n')
        time.sleep(0.033)  # ~30 FPS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture():
    camera = get_camera()
    success, frame = camera.read()
    if success:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.jpg"
        filepath = os.path.join(picture_folder, filename)
        cv2.imwrite(filepath, frame)
        return jsonify({"status": "success", "filename": filename})
    return jsonify({"status": "error"})

@app.route('/start_camera', methods=['POST'])
def start_camera():
    camera = get_camera()
    if camera.isOpened():
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    global camera
    if camera is not None:
        camera.release()
        camera = None
    return jsonify({"status": "success"})

# Start frame buffer update thread
frame_thread = threading.Thread(target=update_frame_buffer, daemon=True)
frame_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)