import cv2
import numpy as np
import tensorflow as tf
from collections import deque, Counter

# ==========================================
# 1. LOAD MAXIMIZED MODEL
# ==========================================
model_path = "model/emotion_maximized_model.h5"
print("Loading model from:", model_path)
model = tf.keras.models.load_model(model_path, compile=False)
print("Model loaded successfully.")

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

# Smoothing buffer
emotion_buffer = deque(maxlen=10)

# ==========================================
# 3. WEBCAM STREAM
# ==========================================
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
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

            # Safe bounding box limits
            x1 = max(0, x)
            y1 = max(0, y)
            x2 = min(w, x + bw)
            y2 = min(h, y + bh)

            face = frame[y1:y2, x1:x2]
            if face.size == 0:
                continue

            # ==========================================
            # 4. PREPROCESS (96x96 RGB for EfficientNetB0)
            # ==========================================
            face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            roi = cv2.resize(face_rgb, (96, 96))  # 96x96 instead of 48x48
            roi = roi.astype("float32")
            roi = np.expand_dims(roi, axis=0)

            # ==========================================
            # 5. PREDICTION
            # ==========================================
            pred = model.predict(roi, verbose=0)[0]
            idx = np.argmax(pred)

            emotion = labels[idx]
            confidence = float(pred[idx]) * 100

            # Smoothing
            emotion_buffer.append(emotion)
            smooth_emotion = Counter(emotion_buffer).most_common(1)[0][0]

            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw label
            text = f"{smooth_emotion} ({confidence:.1f}%)"
            cv2.putText(
                frame,
                text,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

    cv2.imshow("Emotion AI Maximized (EfficientNetB0)", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
