import qrcode
import string
import random
import os
import re

# Function to clean filename by removing invalid characters
def clean_filename(data):
    valid_chars = "-_.() {}[]abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(c for c in data if c in valid_chars)

# Function to get user input for registration
def get_user_data():
    name = input("Enter your name: ").strip()
    while True:
        try:
            age = int(input("Enter your age: "))
            if age > 0:
                break
            else:
                print("Age must be a positive integer.")
        except ValueError:
            print("Please enter a valid age (integer).")
    gender = input("Enter your gender (M/F): ").upper()
    while gender not in ['M', 'F']:
        print("Please enter 'M' or 'F' for gender.")
        gender = input("Enter your gender (M/F): ").upper()
    contact_no = input("Enter your contact number: ").strip()
    
    while True:
        email = input("Enter your email address: ").strip()
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            break
        else:
            print("Please enter a valid email address.")

    user_data = {
        "Name": name,
        "Age": age,
        "Gender": gender,
        "Contact": contact_no,
        "Email": email
    }
    return user_data

# Function to format user data into a string
def format_data(user_data):
    data = ""
    for key, value in user_data.items():
        data += f"{key}: {value}\n"
    return data

# Function to generate QR code based on formatted data and visitor ID
def generate_qr(data, visitor_id):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Create folder if it doesn't exist
    folder_name = "User's QR Data"
    os.makedirs(folder_name, exist_ok=True)

    # Constructing filename with full path
    file_name = os.path.join(folder_name, f"{clean_filename(data)}_{visitor_id}.png")
    try:
        img.save(file_name)
        print(f"QR code generated and saved as: {file_name}")
    except Exception as e:
        print(f"An error occurred while saving the QR code: {e}")

# Main loop for multiple visitors
while True:
    user_data = get_user_data()
    formatted_data = format_data(user_data)
    visitor_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    generate_qr(formatted_data, visitor_id)

    # Ask for confirmation before generating QR code for another visitor
    choice = input("Generate QR code for another visitor (y/n)? ").lower()
    if choice != 'y':
        break

print("QR code generation complete!")