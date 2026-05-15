# Smart Crowd Management System

## Live Demo
[Open Live Website](https://smart-crowd-management.onrender.com)
https://smart-crowd-management.onrender.com

---

## Project Overview

Smart Crowd Management System is an AI-powered surveillance and monitoring application developed using Flask, OpenCV, and YOLOv8.

The system detects and monitors crowd density in real time using webcam, CCTV, or IP camera streams and helps prevent overcrowding situations through alerts and analytics.

---

## Features

- Real-time crowd detection
- YOLOv8-based person detection
- CCTV/IP Webcam integration
- Flask web dashboard
- Alert generation system
- Crowd statistics monitoring
- Cloud deployment using Render
- Scalable architecture for surveillance systems

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| OpenCV | Video processing |
| YOLOv8 | Crowd detection |
| HTML/CSS | Frontend |
| MySQL | Database |
| Render | Cloud hosting |
| GitHub | Version control |

---

## Live Crowd Detection Workflow

```text
Camera Stream
↓
OpenCV Video Capture
↓
YOLOv8 Person Detection
↓
Crowd Counting
↓
Flask Dashboard
↓
Alerts & Analytics
```

---

## Database Integration

The system supports MySQL database integration for:

- crowd logs
- alert history
- analytics
- monitoring reports
- detection records

Database integration was temporarily disabled in cloud deployment due to localhost restrictions on Render hosting.

---

## CCTV / IP Webcam Support

The system supports:
- local webcam
- CCTV RTSP streams
- Android IP Webcam streams

Example supported stream formats:

```python
cv2.VideoCapture(0)

cv2.VideoCapture("http://IP:8080/video")

cv2.VideoCapture("rtsp://username:password@IP:554/stream")
```

---

## Deployment

### GitHub Repository
Project source code hosted using GitHub.

### Cloud Hosting
Flask application deployed publicly using Render.

Live Website:
https://smart-crowd-management.onrender.com

---

## Future Enhancements

- GPU cloud deployment
- Heatmap visualization
- Multi-camera support
- Firebase notifications
- Mobile alerts
- Advanced analytics dashboard
- Face detection
- Emergency crowd alert system

---

## Author

Developed as an AI-based Smart Surveillance and Crowd Management project using Flask, OpenCV, and YOLOv8.
