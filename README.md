# Real-Time Emotion Detection Agent Using Computer Vision

**AI-powered desktop application for real-time facial emotion detection using Python, OpenCV and DeepFace.**

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13+-orange.svg)
![DeepFace](https://img.shields.io/badge/DeepFace-0.0.79+-purple.svg)

![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![Version](https://img.shields.io/badge/Version-1.0-blue.svg)


---

## Project Description

The **Real-Time Emotion Detection Agent** is an AI-powered desktop application that continuously detects facial emotions using a webcam.

Unlike traditional emotion detection projects, this application continuously monitors facial expressions until the webcam is closed.

Whenever an emotion changes, the application instantly displays a custom emotion image provided by the user together with the detected emotion name and confidence percentage.

---

## Features

- ✓ Real-time webcam
- ✓ Face Detection
- ✓ Emotion Detection
- ✓ Confidence Score
- ✓ Custom Emotion Images
- ✓ Automatic Image Switching
- ✓ Dark Theme
- ✓ Error Handling
- ✓ Image Caching
- ✓ Continuous Detection
- ✓ Professional Desktop UI

---

## Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Core application language |
| OpenCV | Webcam capture and frame processing |
| DeepFace | Facial emotion recognition |
| TensorFlow | Deep learning backend for DeepFace |
| Tkinter | Desktop graphical user interface |
| NumPy | Numerical array operations |
| Pillow | Image loading and display |

---

## Project Structure

```
EmotionDetectionAgent/
├── main.py                 # Application entry point
├── camera.py               # Webcam management
├── emotion_detector.py     # DeepFace emotion recognition
├── ui.py                   # Tkinter GUI
├── config.py               # Configuration constants
├── utils.py                # Helper functions
├── image_manager.py        # Emotion image caching
├── state_manager.py        # Application state tracking
├── logger.py               # Logging system
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── LICENSE                 # MIT License
├── .gitignore              # Git ignore rules
├── assets/
│   └── emotion_images/     # Custom emotion images
├── screenshots/            # Application screenshots
├── docs/                   # Architecture documentation
├── logs/                   # Application log files
└── scripts/
    └── generate_placeholder_images.py
```

---

## Installation Guide

### Step 1 — Clone Repository

```bash
git clone https://github.com/username/emotion-detection-agent.git
cd emotion-detection-agent/EmotionDetectionAgent
```

### Step 2 — Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Place Emotion Images

Add your custom emotion images to `assets/emotion_images/`:

```
assets/emotion_images/
├── happy.png
├── sad.png
├── angry.png
├── fear.png
├── surprise.png
├── neutral.png
└── disgust.png
```

To generate placeholder images for testing:

```bash
python scripts/generate_placeholder_images.py
```

### Step 5 — Run Application

```bash
python main.py
```

---

## Emotion Image Requirements

Provide one image per emotion using these naming conventions:

| Emotion | Accepted Filenames |
|---------|-------------------|
| Happy | `happy.png`, `happy.jpg`, `happy.jpeg` |
| Sad | `sad.png`, `sad.jpg`, `sad.jpeg` |
| Angry | `angry.png`, `angry.jpg`, `angry.jpeg` |
| Fear | `fear.png`, `fear.jpg`, `fear.jpeg` |
| Surprise | `surprise.png`, `surprise.jpg`, `surprise.jpeg` |
| Neutral | `neutral.png`, `neutral.jpg`, `neutral.jpeg` |
| Disgust | `disgust.png`, `disgust.jpg`, `disgust.jpeg` |

**Supported formats:** `.png`, `.jpg`, `.jpeg`

Images are loaded once at startup and cached in memory.

---

## Application Usage

```
Open application
        ↓
Camera starts
        ↓
Face detected
        ↓
Emotion predicted
        ↓
Corresponding image displayed
        ↓
Continue until camera closed
```

1. Launch the application with `python main.py`.
2. Allow webcam access when prompted by your operating system.
3. Position your face in front of the camera.
4. The application detects your emotion and displays the matching image.
5. When your expression changes, the image updates automatically.
6. Close the window to exit safely.

---

## Screenshots

| Application Home | 

Home<img width="957" height="560" alt="Screenshot 2026-07-27 212301" src="https://github.com/user-attachments/assets/706fc72e-b01e-489a-a248-54d5ae1843c2" />



  Happy<img width="956" height="563" alt="Screenshot 2026-07-27 212726" src="https://github.com/user-attachments/assets/08f9fac1-8771-42e9-81fa-740c460516a7" />
 



 Sad<img width="960" height="560" alt="Screenshot 2026-07-27 213344" src="https://github.com/user-attachments/assets/f3b6d9e5-d38f-45e8-8808-d3c04b693737" />


 
  Angry<img width="956" height="562" alt="Screenshot 2026-07-27 212851" src="https://github.com/user-attachments/assets/38c6fdd2-85b6-42c2-b1c9-2239c4be493d" />
 



| Neutral<img width="956" height="562" alt="image" src="https://github.com/user-attachments/assets/bf77ea53-ed2f-4acd-a138-95dd90027394" />




Surprise<img width="959" height="560" alt="image" src="https://github.com/user-attachments/assets/8f9fb62f-bbe0-40b5-aae0-f59da357c423" />

 



Fear<img width="959" height="561" alt="Screenshot 2026-07-27 213203" src="https://github.com/user-attachments/assets/b1958e3f-f529-4c90-9c61-be009a64f61f" />



 Disgust<img width="892" height="489" alt="image" src="https://github.com/user-attachments/assets/1b022b5a-67c7-4e8a-aa36-78572d4ebb27" />
 

| No Face Detected |


 No Face<img width="962" height="561" alt="image" src="https://github.com/user-attachments/assets/aa80ffa4-3562-470a-83dc-6541e9ebd6e6" />
 



---
## Architecture

See [docs/architecture.md](docs/architecture.md) for detailed system architecture, data flow, and workflow diagrams.

---

## Testing Checklist

| Test | Status |
|------|--------|
| Camera opens | PASS |
| Camera closes | PASS |
| Happy detection | PASS |
| Sad detection | PASS |
| Angry detection | PASS |
| Fear detection | PASS |
| Surprise detection | PASS |
| Neutral detection | PASS |
| Disgust detection | PASS |
| No Face | PASS |
| Confidence shown | PASS |
| Image switching | PASS |
| No crashes | PASS |

---

## Changelog

### Version 1.0

- Initial Release

---


## Future Enhancements

- Multiple Face Detection
- Emotion History
- Charts and Analytics
- CSV Export
- PDF Report
- Voice Feedback
- Fullscreen Mode
- Settings Window
- Custom Themes
- Database Support
- Cloud Synchronization
- REST API
- Model Selection
- GPU Acceleration
- Emotion Analytics
-------------------
👨‍💻 Author
-------------------
Dheeraj Kanna
-------------------
GITHUB - https://github.com/Dheeraj-kanna
