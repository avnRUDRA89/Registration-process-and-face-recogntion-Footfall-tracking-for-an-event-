# Import necessary modules
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import qrcode
import string
import random
import os
import re

app = Flask(__name__)

# Function to clean filename by removing invalid characters
def clean_filename(data):
    valid_chars = "-_.() {}[]abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(c for c in data if c in valid_chars)

# Function to format user data into a string
def format_data(user_data):
    data = ""
    for key, value in user_data.items():
        data += f"{key}: {value}\n"
    return data

# Function to generate QR code based on user data
def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code to a specific folder (User's QR Data)
    folder_name = "User's QR Data"  # Change this to your desired folder name
    os.makedirs(folder_name, exist_ok=True)

    # Generate a unique filename based on user data and visitor ID
    visitor_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    file_name = f"{clean_filename(data)}_{visitor_id}.png"
    file_path = os.path.join(folder_name, file_name)

    try:
        img.save(file_path)
        return file_name
    except Exception as e:
        print(f"An error occurred while saving the QR code: {e}")
        return None

# Flask routes
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        contact_no = request.form['contact']
        email = request.form['email']

        user_data = {
            "Name": name,
            "Age": age,
            "Gender": gender,
            "Contact": contact_no,
            "Email": email
        }

        formatted_data = format_data(user_data)
        qr_file = generate_qr(formatted_data)

        if qr_file:
            return render_template('qr.html', qr_file=qr_file)
        else:
            return "Failed to generate QR code. Please try again."

    return render_template('register.html')

# Route to serve the QR code image for viewing
@app.route('/view/<filename>')
def view_qr(filename):
    directory = os.path.join(app.root_path, "User's QR Data")
    return send_from_directory(directory, filename)

# Route to serve the QR code image for download
@app.route('/download/<filename>')
def download_qr(filename):
    directory = os.path.join(app.root_path, "User's QR Data")
    return send_from_directory(directory, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
