from flask import Flask, render_template, redirect, url_for, Response
import os
import cv2
import face_recognition
from datetime import datetime
import threading

app = Flask(__name__)

# Path to the folder containing user face images
faces_folder = ""

# Load all images from the folder and extract names and encodings
def load_known_faces(folder_path):
    known_face_encodings = []
    known_face_names = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            name = os.path.splitext(filename)[0]
            image_path = os.path.join(folder_path, filename)
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)

            if face_encodings:
                known_face_encodings.append(face_encodings[0])
                known_face_names.append(name)
    return known_face_encodings, known_face_names

# Initialize the list to track visitor data
visitors_data = []

# Access the webcam
webcam = cv2.VideoCapture(0)

# Global variables for threading and recognition state
is_recognizing = False

known_face_encodings, known_face_names = load_known_faces(faces_folder)
print(f"Loaded {len(known_face_encodings)} known faces.")

def recognize_faces():
    global is_recognizing, visitors_data

    while is_recognizing:
        successful_frame_read, frame = webcam.read()
        if not successful_frame_read:
            break
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        current_visitors = []

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            current_visitors.append(name)

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Update visitor data
        for visitor_name in current_visitors:
            found_visitor = False
            for visitor_data in visitors_data:
                if visitor_data['name'] == visitor_name:
                    visitor_data['last_seen'] = datetime.now()
                    found_visitor = True
                    break
            
            if not found_visitor:
                new_visitor_data = {
                    'name': visitor_name,
                    'first_seen': datetime.now(),
                    'last_seen': datetime.now(),
                    'total_duration': 0
                }
                visitors_data.append(new_visitor_data)

        # Check for visitors who have left
        for visitor_data in visitors_data[:]:
            if visitor_data['name'] not in current_visitors:
                time_spent = (datetime.now() - visitor_data['last_seen']).total_seconds()
                visitor_data['total_duration'] += time_spent

                
        # Print or format visitor data with 'sec' appended to total duration
        for visitor_data in visitors_data:
            total_duration_sec = visitor_data['total_duration']
            total_duration_formatted = f"{total_duration_sec:.2f} sec"
            print(f"Visitor: {visitor_data['name']}")
            print(f"First Seen: {visitor_data['first_seen'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Last Seen: {visitor_data['last_seen'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total Duration in sec: {total_duration_formatted}")
            print()
        

        # Display the frame with recognized faces
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imshow('Face Recognition', frame)
        key = cv2.waitKey(1)

        if key == 81 or key == 113:  # 'Q' or 'q' key pressed
            break

    # Release the webcam and close OpenCV windows
    webcam.release()
    cv2.destroyAllWindows()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_recognition')
def start_recognition():
    global is_recognizing
    is_recognizing = True

    # Start a new thread for face recognition
    threading.Thread(target=recognize_faces, daemon=True).start()

    return redirect(url_for('video_feed'))

@app.route('/stop_recognition')
def stop_recognition():
    global is_recognizing
    is_recognizing = False
    return redirect(url_for('index'))

@app.route('/video_feed')
def video_feed():
    return Response(video_feed_generator(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def video_feed_generator():
    global is_recognizing

    while is_recognizing:
        try:
            success, frame = webcam.read()
            if not success:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            ret, jpeg = cv2.imencode('.jpg', frame)

            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

        except Exception as e:
            print(f"Error: {e}")
            break

    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + b'\r\n\r\n')

@app.route('/visitor_data')
def visitor_data():
    return render_template('visitor_data.html', visitors=visitors_data)

if __name__ == '__main__':
    app.run(debug=True)
