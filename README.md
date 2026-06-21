# Smart Surveillance System Using Motion Detection

This project was developed as a Course Based Project to create a simple and efficient surveillance system using Python and OpenCV. The system continuously monitors live video from a webcam and automatically detects motion in the scene.

Whenever motion is detected, the system highlights the moving object, captures screenshots, records video footage, generates alerts, and stores event logs with timestamps. The main goal of this project is to provide a low-cost and automated surveillance solution that can be used for homes, offices, classrooms, laboratories, and other security-sensitive areas.

## Features

* Real-time motion detection using computer vision techniques
* Automatic video recording when motion is detected
* Screenshot capture with timestamp
* Motion event logging
* Audio alert generation
* Live dashboard showing system status
* Manual controls for recording and screenshots

## Technologies Used

* Python
* OpenCV
* Python-docx
* Winsound
* File Handling

## Project Structure

* `motion_detector.py` – Main surveillance system
* `generate_report.py` – Generates the project report document
* `surveillance_output/recordings` – Stores recorded videos
* `surveillance_output/screenshots` – Stores captured screenshots
* `surveillance_output/motion_log.txt` – Stores motion event logs

## How to Run

1. Install the required packages:

   pip install opencv-python python-docx

2. Run the surveillance system:

   python motion_detector.py

## Controls

* Press `q` to quit the application
* Press `r` to start or stop recording manually
* Press `s` to capture a screenshot manually

## Applications

* Home Security
* Office Monitoring
* Classroom Surveillance
* Warehouse Security
* Restricted Area Monitoring

## Future Improvements

* Face Recognition
* Object Detection using YOLO
* Email and SMS Notifications
* Cloud Storage Integration
* Multi-Camera Support
* Remote Monitoring Dashboard

## Author

Rishit Datta Kona
B.E. CSE (AI & ML)
Vasavi College of Engineering, Hyderabad

