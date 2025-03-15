import cv2
import numpy as np
import face_recognition
import mysql.connector
import pickle
import csv
from flask import Flask, render_template, Response, jsonify
from datetime import datetime

app = Flask(__name__)

# MySQL Database Configuration
db_config = {
   "host": "localhost",
   "user": "tux",
   "password": "linux",
   "database": "attendance_db",
   "charset":"utf8mb4",
   "collation":"utf8mb4_general_ci"
}

# Global variable to track recognized face
recognized_face = None

def get_known_faces():
    """Retrieve known faces from the database."""
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT name, encoding FROM students")
    records = cursor.fetchall()
    
    known_names = []
    known_encodings = []

    for name, encoding in records:
        if isinstance(encoding, str):  # If encoding is stored as a string
            encoding = eval(encoding)  # Convert string to list
        elif isinstance(encoding, bytes):  # If it's stored as bytes
            encoding = pickle.loads(encoding)
        
        known_names.append(name)
        known_encodings.append(encoding)

    conn.close()
    return known_names, known_encodings

def mark_attendance(name):
    """Marks attendance in MySQL and CSV file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Store in MySQL
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attendance (name, timestamp) VALUES (%s, %s)", (name, timestamp))
    conn.commit()
    conn.close()

    # Store in CSV
    with open("attendance.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([name, timestamp])

    print(f"✅ Attendance marked for {name} at {timestamp}")

def gen_frames():
    """Capture video, perform face recognition, and return video stream."""
    global recognized_face
    recognized_face = None  # Reset before detection
    known_names, known_encodings = get_known_faces()

    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("❌ Error: Cannot open camera")
        return

    while True:
        success, frame = camera.read()
        if not success:
            print("❌ Error: Cannot read frame")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                match_index = matches.index(True)
                name = known_names[match_index]
                recognized_face = name  # Update recognized face
                mark_attendance(name)
                print(f"🎯 Face Recognized: {name}")

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    camera.release()

@app.route('/')
def index():
    """Render the main webpage."""
    return render_template('index.html')

@app.route('/video')
def video():
    """Stream video feed to the webpage."""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/check_recognition')
def check_recognition():
    """Check if a face was recently recognized."""
    global recognized_face
    if recognized_face:
        return jsonify({"status": "success", "recognized": recognized_face})
    else:
        return jsonify({"status": "failed", "recognized": None})

if __name__ == "__main__":
    app.run(debug=True)
