# app.py
from flask import Flask, Response, render_template, jsonify, request
import cv2
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# Global variable for camera
camera = None
picture_folder = str(Path.home() / "Pictures" / "camera_captures")

# Ensure pictures directory exists
os.makedirs(picture_folder, exist_ok=True)

def get_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)  # Use first USB camera
    return camera

def generate_frames():
    camera = get_camera()
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)