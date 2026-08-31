# Emotion AI - Real-Time Facial Emotion Recognition

A real-time facial emotion recognition system using **MediaPipe** face detection and a **Custom CNN** trained on the **FER2013** dataset.

Detects 7 emotions live from webcam: `Angry` · `Disgust` · `Fear` · `Happy` · `Sad` · `Surprise` · `Neutral`

---

## 🚀 Quick Start (Windows)

```cmd
cd F:\emotion-detection
.\run_webcam.bat
```

Press **`q`** in the camera window to exit.

---

## 📦 Environment Setup (First Time)

Requires **Python 3.10** installed on Windows.

```cmd
py -3.10 -m venv venv_win
.\venv_win\Scripts\activate
pip install tensorflow==2.15.0 tensorflow-intel==2.15.0
pip install mediapipe==0.10.9
pip install "opencv-python==4.8.0.76" numpy==1.26.4 h5py pillow scikit-learn
```

---

## 🖥️ Run Order

| Step | Command | Purpose |
|------|---------|---------|
| 1 | `cd F:\emotion-detection` | Navigate to project |
| 2 | `.\venv_win\Scripts\activate` | Activate virtual environment |
| 3 | `python live_detect_pro.py` | Start live webcam detection |
| 4 | Press **`q`** | Exit the camera window |
| 5 | `deactivate` | Leave environment when done |

---

## 📊 Performance Metrics (Test Set — 7,178 images)

| Model | Accuracy | Loss |
|-------|----------|------|
| Custom CNN (48×48 Grayscale) | **63.51%** | 1.001 |
| EfficientNetB0 Transfer (96×96 RGB) | 43.90% | 1.479 |

### Per-Class Results (Custom CNN)

| Emotion | Precision | Recall | F1-Score |
|---------|-----------|--------|----------|
| Happy | 82.51% | 86.13% | 84.28% |
| Neutral | 76.42% | 74.49% | 75.44% |
| Sad | 55.46% | 67.96% | 61.08% |
| Angry | 53.71% | 60.44% | 56.88% |
| Disgust | 81.82% | 40.54% | 54.22% |
| Surprise | 50.72% | 47.71% | 49.17% |
| Fear | 50.79% | 34.67% | 41.21% |

---

## 🧠 Architecture

- **Face Detection**: MediaPipe FaceDetection (model_selection=0)
- **Classifier**: Custom 3-layer CNN (Conv2D → BN → MaxPool × 3) + Dense(512) + Dropout(0.5) + Softmax(7)
- **Input**: 48×48 grayscale face crop, normalized to [0,1]
- **Smoothing**: 10-frame majority vote buffer (reduces flickering)
- **Dataset**: FER2013 (28,709 train / 7,178 test images)

---

## 🗂️ Project Structure

```
emotion-detection/
├── live_detect_pro.py        # Main real-time detector (MediaPipe + CNN)
├── live_detect.py            # Alternate detector
├── live_detect_maximized.py  # EfficientNetB0 variant
├── train.py                  # Training script (EfficientNetB0)
├── train_maximized.py        # Advanced training with resume support
├── evaluate_all.py           # Full evaluation + metrics report
├── performance_metrics.json  # Test set metrics (JSON)
├── run_webcam.bat            # One-click Windows launcher
├── run_train.sh              # WSL training script (GPU)
├── requirements.txt          # Python dependencies
├── model/                    # Trained model weights (not tracked in git)
├── dataset/                  # FER2013 train/test (not tracked in git)
└── venv_win/                 # Windows virtual env (not tracked in git)
```
