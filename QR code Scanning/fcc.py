import cv2
import pyzbar.pyzbar as pyzbar
import os

# Placeholder function to connect to the database 
def connect_to_database():

    print("Scanning the QR code...")
    return None  

# Placeholder function to retrieve user data 
def get_user_data(db_connection, qr_code_data):
    # Parse the QR code data to extract user information
    user_data = {}
    for line in qr_code_data.split("\n"):
        if line:
            key, value = line.split(": ")
            user_data[key] = value
    return user_data  

# Function to save captured image to a dedicated folder
def save_captured_image(image, user_data):
    # Create folder if it doesn't exist
    folder_name = "User's Face Data"
    os.makedirs(folder_name, exist_ok=True)

    # Constructing filename with full path
    filename = os.path.join(folder_name, f"user_{user_data['Name']}.jpg")
    cv2.imwrite(filename, image)
    print(f"Image saved as: {filename}")

def main():
    
    db_connection = connect_to_database()

    # Open webcam
    cap = cv2.VideoCapture(0)

    while True:
        # Capture frame from webcam
        ret, frame = cap.read()

        # Decode QR code from frame
        qr_codes = pyzbar.decode(frame)
        if qr_codes:
            # Extract data from the first QR code
            qr_code_data = qr_codes[0].data.decode("utf-8")
            print("Decoded QR code data:", qr_code_data)

            # Retrieve user data from the QR code (simulated)
            user_data = get_user_data(db_connection, qr_code_data)
            if user_data:
                print(f"Welcome, {user_data['Name']}")

                # Capture user photo 
                capture_photo = input("Capture user photo (y/n)? ")
                if capture_photo.lower() == 'y':
                    # Capture a frame from the webcam
                    ret, photo_frame = cap.read()
                    if ret:
                        # Save captured image 
                        save_captured_image(photo_frame, user_data)
                    else:
                        print("Error capturing photo.")
            else:
                print("Invalid QR code data or user not found.")

            # Wait for user input to continue or exit
            continue_scanning = input("Scan another QR code (y/n)? ")
            if continue_scanning.lower() != 'y':
                break

        # Display frame with or without QR code
        cv2.imshow("QR Scanner", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    # Release webcam resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()