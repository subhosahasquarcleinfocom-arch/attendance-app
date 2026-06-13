from flask import Flask, render_template, request, jsonify
import datetime
import os
import cv2
import numpy as np
import base64

app = Flask(__name__)

# Cloud Server-er temporary direct storage repository directory setup
CSV_FILE = "/tmp/attendance.csv" if os.environ.get("RENDER") else "attendance.csv"

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w") as f:
        f.write("Name,Date,Time,Status,Location\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/punch', methods=['POST'])
def punch():
    try:
        data = request.json
        punch_type = data.get('type')
        location = data.get('location', 'Unknown')
        image_data = data.get('image') 

        if not image_data:
            return jsonify({"status": "error", "message": "Camera image paini!"})

        # Base64 image ke processing grid standard-e ana
        header, encoded = image_data.split(",", 1)
        data_bytes = base64.b64decode(encoded)
        np_data = np.frombuffer(data_bytes, dtype=np.uint8)
        frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

        # Built-in Face Detection (Haar Cascade Algorithm)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            return jsonify({"status": "error", "message": "Mukh dekha jacche na! Thik bhabe samne ashun."})

        # Punch Track Data Formatting
        emp_name = "SUBHO_SAHA" 
        now = datetime.datetime.now()
        d_str = now.strftime("%Y-%m-%d")
        t_str = now.strftime("%H:%M:%S")

        # Live Append Log
        with open(CSV_FILE, "a") as f:
            f.write(f"{emp_name},{d_str},{t_str},{punch_type},{location}\n")

        return jsonify({"status": "success", "message": f"{punch_type} Done Successfully!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    # Cloud host setup dynamic selection architecture
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
