# Real-Time Emotion AI (MediaPipe + Upgraded 4-Stage ConvNet)

A real-time facial emotion recognition system using **Google MediaPipe** for robust face detection and an **Upgraded 4-Stage Convolutional Neural Network (CNN)** trained on the **FER2013** dataset with **Focal Loss** and **Label Smoothing**.

Classifies 7 human emotions live from webcam:  
`Angry` · `Disgust` · `Fear` · `Happy` · `Sad` · `Surprise` · `Neutral`

---

## ⚡ Key Improvements & Optimization Features

1. **Categorical Focal Loss ($\gamma = 2.0$)**:
   - Reduces loss weighting for easy, majority-class samples (*Happy*, *Neutral*) and heavily penalizes errors on hard/minority classes (*Disgust*, *Fear*).
2. **Label Smoothing ($0.1$)**:
   - Softens hard targets (`[1, 0, 0...]` $\to$ `[0.91, 0.015...]`), improving generalization on noisy, subjective FER2013 labels.
3. **Upgraded 4-Stage Deep Architecture**:
   - 4 Convolutional blocks (`64` $\to$ `128` $\to$ `256` $\to$ `512` filters) with Batch Normalization, L2 regularization (`1e-4`), Global Average Pooling, and Dropout (`0.5`).
4. **Enhanced Data Augmentation**:
   - Random rotations ($\pm 20^\circ$), width/height shifts ($\pm 15\%$), zoom ($\pm 15\%$), brightness adjustments (`0.8`-`1.2`), and horizontal flips.
5. **Real-Time Temporal Smoothing Buffer**:
   - 10-frame majority vote buffer (`Counter().most_common(1)`) to eliminate frame-by-frame prediction flickering.

---

## 🚀 Quick Start (Windows)

Launch the project with a single click using the batch launcher:

```cmd
cd F:\emotion-detection
.\run_webcam.bat
```

*Press **`q`** in the camera window to exit.*

---

## 💻 Manual Execution Order

### Option A: Windows PowerShell / Command Prompt
```powershell
# 1. Navigate to directory
cd F:\emotion-detection

# 2. Activate virtual environment
.\venv_win\Scripts\activate

# 3. Launch live emotion detector
python live_detect_pro.py
```

### Option B: WSL / Ubuntu Terminal (GPU Recommended)
```bash
# 1. Navigate to directory
cd /mnt/f/emotion-detection

# 2. Activate virtual environment
source venv/bin/activate

# 3. Launch live emotion detector
python live_detect_pro.py
```

---

## 🏋️ How to Train the Model

To train or retrain the upgraded model manually:

```bash
# Activate your environment (Windows or WSL)
python train.py
```

Training saves the model weights to `model/emotion_model.h5`.

---

## 📊 Evaluation & Metrics Benchmark

To compute evaluation metrics (Accuracy, Loss, Precision, Recall, F1-Score, Confusion Matrix) on the 7,178 test images:

```bash
python evaluate_all.py
```

### Summary Benchmark:
- **Baseline Accuracy**: **63.51%** on FER2013 test set (approaching the human baseline of ~65%).
- **Weighted F1-Score**: **62.91%**
- **Top Class Performance**: *Happy* (86.1% Recall, 84.3% F1), *Neutral* (74.5% Recall, 75.4% F1), *Sad* (68.0% Recall, 61.1% F1).

---

## 📦 Requirements & Dependencies

The project is configured for **Python 3.10**:
- `tensorflow == 2.15.0`
- `mediapipe == 0.10.9`
- `opencv-python == 4.8.0.76`
- `numpy == 1.26.4`
- `h5py`, `pillow`, `scikit-learn`, `matplotlib`

Dependencies are listed in [`requirements.txt`](file:///f:/emotion-detection/requirements.txt).

---

## 🗂️ Project Structure

```
emotion-detection/
├── live_detect_pro.py        # Primary real-time detector (MediaPipe + 4-Stage CNN)
├── live_detect.py            # Alternate live detection script
├── train.py                  # Training pipeline (Focal Loss + Label Smoothing + 4-Stage CNN)
├── evaluate_all.py           # Evaluation script (Accuracy, F1, Confusion Matrix)
├── performance_metrics.json  # Comprehensive test evaluation metrics
├── run_webcam.bat            # One-click Windows launcher
├── requirements.txt          # Production dependencies
├── labels.txt                # 7 emotion class names
├── model/                    # Model weights directory (emotion_model.h5)
└── dataset/                  # FER2013 train/test dataset
```
