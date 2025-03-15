import cv2
import face_recognition
import mysql.connector
import numpy as np
import os
from config import DB_CONFIG

def store_face_encodings():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    for filename in os.listdir("known_faces"):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join("known_faces", filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                encoding_str = str(encodings[0].tolist())
                name = os.path.splitext(filename)[0]

                cursor.execute("INSERT INTO students (name, encoding) VALUES (%s, %s)", (name, encoding_str))
    
    conn.commit()
    conn.close()
    print("Face encodings stored successfully!")

store_face_encodings()
