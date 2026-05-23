import cv2
import numpy as np
import tensorflow as tf

model = tf.keras.models.load_model("model/emotion_model.h5")

labels = ["Angry","Disgust","Fear","Happy","Sad","Surprise","Neutral"]

cap = cv2.VideoCapture(0)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:

        roi_gray = gray[y:y+h, x:x+w]
        roi = cv2.resize(roi_gray, (48, 48))

        roi = roi.astype("float32") / 255.0
        roi = np.expand_dims(roi, axis=(0, -1))

        pred = model.predict(roi)[0]

        idx = np.argmax(pred)
        emotion = labels[idx]
        confidence = pred[idx] * 100

        # 🟩 DRAW BOX
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # 🟨 TEXT (emotion + %)
        text = f"{emotion} ({confidence:.1f}%)"

        cv2.putText(
            frame,
            text,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    cv2.imshow("Emotion Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()