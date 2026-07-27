# Architecture Documentation

## Real-Time Emotion Detection Agent — System Architecture

---

## 1. Architecture Overview

The application follows a **Layered Modular Architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │ Tkinter GUI │  │ Webcam View  │  │ Emotion Image View  │ │
│  └─────────────┘  └──────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                       │
│  ┌──────────────┐ ┌─────────────────┐ ┌──────────────────┐  │
│  │CameraManager │ │ EmotionDetector │ │  ImageManager    │  │
│  └──────────────┘ └─────────────────┘ └──────────────────┘  │
│  ┌──────────────┐ ┌─────────────────┐                       │
│  │ StateManager │ │   UIManager     │                       │
│  └──────────────┘ └─────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     CORE SERVICES                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  DeepFace    │  │   OpenCV     │  │   TensorFlow     │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                       UTILITIES                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ ConfigManager│  │    Logger    │  │   File Loader    │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow Diagram

```
User
  │
  ▼
Webcam
  │
  ▼
Frame Capture (CameraManager)
  │
  ▼
Face Detection (DeepFace)
  │
  ▼
Emotion Prediction (EmotionDetector)
  │
  ▼
Confidence Calculation
  │
  ▼
Emotion Change Detection (StateManager)
  │
  ▼
Load Corresponding Image (ImageManager — from cache)
  │
  ▼
Update GUI (UIManager)
  │
  ▼
Repeat
```

---

## 3. Application Workflow

```
Launch (main.py)
      │
      ▼
Initialize Configuration
      │
      ▼
Verify Dependencies
      │
      ▼
Load Emotion Images (cached in memory)
      │
      ▼
Initialize Camera
      │
      ▼
Initialize Emotion Detector
      │
      ▼
Create UI
      │
      ▼
Start Worker Threads
      │
      ├── Camera Thread ──► Capture frames continuously
      │
      └── Detection Thread ──► Predict emotions every 300ms
      │
      ▼
Main Thread ──► Refresh UI every ~33ms
      │
      ▼
User closes window
      │
      ▼
Release resources & Exit
```

---

## 4. Threading Model

```
┌──────────────────────────────────────────────────────────┐
│                      MAIN THREAD                          │
│  • Tkinter event loop                                     │
│  • UI updates (webcam display, labels, status)            │
│  • Never performs heavy AI computation                    │
└──────────────────────────────────────────────────────────┘

┌────────────────────────┐  ┌──────────────────────────────┐
│    CAMERA THREAD       │  │     DETECTION THREAD          │
│  • Frame capture       │  │  • DeepFace analysis          │
│  • Mirror flip         │  │  • Dominant emotion selection │
│  • FPS calculation     │  │  • Confidence calculation     │
└────────────────────────┘  └──────────────────────────────┘
```

---

## 5. Application States

| State | Description |
|-------|-------------|
| `INITIALIZING` | Application starting up |
| `CAMERA_READY` | Webcam initialized successfully |
| `DETECTING` | Active emotion detection in progress |
| `NO_FACE` | No face visible in frame |
| `EMOTION_UPDATED` | Emotion changed, UI updated |
| `ERROR` | Recoverable error occurred |
| `EXITING` | Application shutting down |

---

## 6. Module Responsibilities

| Module | Class | Responsibility |
|--------|-------|----------------|
| `main.py` | `EmotionApp` | Entry point, lifecycle, threading |
| `camera.py` | `CameraManager` | Webcam operations |
| `emotion_detector.py` | `EmotionDetector` | DeepFace integration |
| `ui.py` | `UIManager` | GUI construction and updates |
| `config.py` | `ConfigManager` | Constants and configuration |
| `utils.py` | Functions | Image loading, helpers |
| `image_manager.py` | `ImageManager` | Image caching |
| `state_manager.py` | `StateManager` | State and emotion change tracking |
| `logger.py` | `Logger` | Application logging |

---

## 7. Emotion Change Logic

```
Previous Emotion: Happy    Current Emotion: Happy
                           ↓
                    No UI update (image not reloaded)

Previous Emotion: Happy    Current Emotion: Sad
                           ↓
                    Update image, label, confidence
```

---

## 8. Error Handling Strategy

| Error Type | Handling |
|------------|----------|
| Camera unavailable | Retry up to 3 times, then exit safely |
| Camera disconnect | Attempt reconnection |
| DeepFace failure | Skip frame, log error, continue |
| Missing emotion image | Display "Missing Image: {emotion}", continue |
| TensorFlow init failure | Log warning, retry on first frame |
| Unexpected exception | Log, show friendly message, exit safely |

---

## 9. Folder Structure

```
EmotionDetectionAgent/
├── main.py
├── camera.py
├── emotion_detector.py
├── ui.py
├── config.py
├── utils.py
├── image_manager.py
├── state_manager.py
├── logger.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── assets/
│   └── emotion_images/
├── screenshots/
├── docs/
│   └── architecture.md
├── logs/
│   └── application.log
└── scripts/
    └── generate_placeholder_images.py
```
