# 🎟️ Event Registration & Footfall Tracking System

A complete end-to-end system for event registration, QR code generation, real-time QR scanning, face image capture, and footfall tracking using face recognition. Built using Flask, OpenCV, and Python, this system helps automate and digitize visitor management for physical events.

---

## 🧩 Features

### 🔹 1. Registration + QR Code Generation
- Users register via a web form
- Generates a unique QR code for each user
- QR code can be viewed and downloaded

### 🔹 2. QR Code Scanning & Face Capture
- Scans QR codes using webcam (browser or CLI)
- Extracts user details and stores face image
- Stores face images with matching names for recognition

### 🔹 3. Real-time Face Recognition & Footfall Tracking
- Detects faces using webcam feed
- Matches with known visitors and tracks duration
- Records first seen, last seen, and time spent at the event
- Displays live feed with recognition overlay
- Visual visitor dashboard showing attendance stats

---

## 🛠️ Tech Stack

| Purpose              | Tools/Libraries                           |
|----------------------|-------------------------------------------|
| Web Framework        | Flask                                     |
| QR Code Generation   | `qrcode`, `pyzbar`                        |
| Face Recognition     | `face_recognition`, `OpenCV`              |
| Front-End            | HTML5, CSS3, Jinja2 templating            |
| Camera Feed          | Webcam / OpenCV                           |
| QR Decoding          | Pyzbar                                    |

---

## 🗂️ Project Structure

