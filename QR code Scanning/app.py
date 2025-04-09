from flask import Flask, render_template, Response, request, redirect, url_for, session, flash
import cv2
import pyzbar.pyzbar as pyzbar
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
camera = None

def initialize_camera():
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            flash("Error: Unable to access the camera", "danger")
            return False
    return True

# Placeholder function to connect to the database 
def connect_to_database():
    return None  

# Placeholder function to retrieve user data 
def get_user_data(db_connection, qr_code_data):
    user_data = {}
    for line in qr_code_data.split("\n"):
        if line:
            key, value = line.split(": ")
            user_data[key] = value
    return user_data

# Function to save captured image to a dedicated folder
def save_captured_image(image, user_data):
    folder_name = "User's Face Data"
    os.makedirs(folder_name, exist_ok=True)
    filename = os.path.join(folder_name, f"user_{user_data['Name']}.jpg")
    cv2.imwrite(filename, image)
    print(f"Image saved as: {filename}")

def gen_frames():
    while True:
        if not initialize_camera():
            break
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if request.method == 'POST':
        if not initialize_camera():
            return render_template('scan.html', user_data=None)
        success, frame = camera.read()
        if not success:
            flash("Failed to capture image", "danger")
            return render_template('scan.html', user_data=None)
        qr_codes = pyzbar.decode(frame)
        if qr_codes:
            qr_code_data = qr_codes[0].data.decode("utf-8")
            db_connection = connect_to_database()
            user_data = get_user_data(db_connection, qr_code_data)
            if user_data:
                session['user_data'] = user_data
                return redirect(url_for('capture'))
            else:
                flash("Invalid QR code data or user not found", "danger")
        else:
            flash("No QR code detected", "warning")
    return render_template('scan.html', user_data=None)

@app.route('/capture', methods=['GET', 'POST'])
def capture():
    user_data = session.get('user_data', None)
    if request.method == 'POST':
        if not initialize_camera():
            return render_template('capture.html', user_data=user_data, message=None)
        success, frame = camera.read()
        if success:
            save_captured_image(frame, user_data)
            flash("Image captured successfully!", "success")
            return redirect(url_for('repeat'))
        else:
            flash("Failed to capture image", "danger")
    return render_template('capture.html', user_data=user_data, message=None)

@app.route('/repeat', methods=['GET', 'POST'])
def repeat():
    if request.method == 'POST':
        if 'repeat' in request.form:
            return redirect(url_for('scan'))
        elif 'finish' in request.form:
            return redirect(url_for('index'))
    return render_template('repeat.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
