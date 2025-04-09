import os
import cv2
import face_recognition
from datetime import datetime

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

known_face_encodings, known_face_names = load_known_faces(faces_folder)
print(f"Loaded {len(known_face_encodings)} known faces.")

while True:
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
    for visitor_data in visitors_data[:]:  # Iterate over a copy of the list
        if visitor_data['name'] not in current_visitors:
            time_spent = (datetime.now() - visitor_data['last_seen']).total_seconds()
            visitor_data['total_duration'] += time_spent
            print(f"{visitor_data['name']} was in the frame for {time_spent:.2f} seconds")
            print(f"Visitor Data for {visitor_data['name']}:")
            print(f"First Seen: {visitor_data['first_seen'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Last Seen: {visitor_data['last_seen'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total Duration in Sec: {visitor_data['total_duration']:.2f} seconds")
            print()

            # If visitor has not been seen for a while, remove them from visitors_data
            if (datetime.now() - visitor_data['last_seen']).total_seconds() > 5:
                print(f"{visitor_data['name']} exited. Total time spent: {visitor_data['total_duration']:.2f} seconds")
                visitors_data.remove(visitor_data)

    cv2.imshow('Face Recognition', frame)
    key = cv2.waitKey(1)
    
    if key == 81 or key == 113:  # 'Q' or 'q' key pressed
        break

# Release the webcam and close all windows
webcam.release()
cv2.destroyAllWindows()
