import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, BatchNormalization, MaxPooling2D, Flatten, Dense, Dropout, Input
from collections import deque, Counter
import os

# ==========================================
# 1. LOAD MODEL (Robust Architecture + Weights)
# ==========================================
def load_emotion_model(weights_path="model/emotion_model.h5"):
    model = Sequential([
        Input(shape=(48, 48, 1)),
        Conv2D(64, (3, 3), activation='relu', name='conv2d'),
        BatchNormalization(name='batch_normalization'),
        MaxPooling2D((2, 2), name='max_pooling2d'),
        
        Conv2D(128, (3, 3), activation='relu', name='conv2d_1'),
        BatchNormalization(name='batch_normalization_1'),
        MaxPooling2D((2, 2), name='max_pooling2d_1'),
        
        Conv2D(256, (3, 3), activation='relu', name='conv2d_2'),
        BatchNormalization(name='batch_normalization_2'),
        MaxPooling2D((2, 2), name='max_pooling2d_2'),
        
        Flatten(name='flatten'),
        Dense(512, activation='relu', name='dense'),
        Dropout(0.5, name='dropout'),
        Dense(7, activation='softmax', name='dense_1')
    ])
    
    if not os.path.exists(weights_path):
        raise FileNotFoundError(f"Model weights file not found at: {weights_path}")
        
    model.load_weights(weights_path)
    print(f"✅ Model weights loaded successfully from: {weights_path}")
    return model

model = load_emotion_model("model/emotion_model.h5")

labels = [
    "Angry",
    "Disgust",
    "Fear",
    "Happy",
    "Sad",
    "Surprise",
    "Neutral"
]

# ==========================================
# 2. MEDIAPIPE FACE DETECTION
# ==========================================
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.6
)

# ==========================================
# 3. SMOOTHING BUFFER (10 Frames)
# ==========================================
emotion_buffer = deque(maxlen=10)

# ==========================================
# 4. WEBCAM STREAM
# ==========================================
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Error: Could not open camera (index 0). Please ensure camera is connected.")
    print("If you are running in WSL, make sure camera is shared via USBIPD or run on native Windows.")

print("\n🚀 Starting Real-Time Emotion AI (MediaPipe)...")
print("👉 Press 'q' on your keyboard inside the window to exit.\n")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret or frame is None:
        print("⚠️ Failed to grab frame from camera.")
        break

    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = face_detection.process(rgb)

    if results.detections:
        for detection in results.detections:
            bbox = detection.location_data.relative_bounding_box

            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            bw = int(bbox.width * w)
            bh = int(bbox.height * h)

            # Safe bounding box bounds
            x1 = max(0, x)
            y1 = max(0, y)
            x2 = min(w, x + bw)
            y2 = min(h, y + bh)

            face = frame[y1:y2, x1:x2]

            if face.size == 0:
                continue

            # ==========================================
            # PREPROCESS (48x48 Grayscale for CNN Model)
            # ==========================================
            face_gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            roi = cv2.resize(face_gray, (48, 48))
            roi = roi.astype("float32") / 255.0
            roi = np.expand_dims(roi, axis=-1)  # (48, 48, 1)
            roi = np.expand_dims(roi, axis=0)   # (1, 48, 48, 1)

            # ==========================================
            # PREDICTION
            # ==========================================
            pred = model.predict(roi, verbose=0)[0]
            idx = np.argmax(pred)

            emotion = labels[idx]
            confidence = float(pred[idx]) * 100

            # ==========================================
            # TEMPORAL SMOOTHING
            # ==========================================
            emotion_buffer.append(emotion)
            smooth_emotion = Counter(emotion_buffer).most_common(1)[0][0]

            # ==========================================
            # VISUALIZATION
            # ==========================================
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            text = f"{smooth_emotion} ({confidence:.1f}%)"
            cv2.putText(
                frame,
                text,
                (x1, max(20, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

    cv2.imshow("Emotion AI Pro (MediaPipe)", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("👋 Emotion detection stopped.")