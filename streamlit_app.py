import streamlit as st
import cv2
import numpy as np
import tensorflow as tf
from mediapipe_utils import extract_face

model = tf.keras.models.load_model("model/emotion_model.h5")

labels = ["Angry","Disgust","Fear","Happy","Sad","Surprise","Neutral"]

st.title("😎 Real-Time Emotion Detection AI")

run = st.checkbox("Start Webcam")

cap = cv2.VideoCapture(0)

frame_window = st.image([])

while run:
    ret, frame = cap.read()
    if not ret:
        break

    face = extract_face(frame)

    if face is not None:
        img = face.astype("float32") / 255.0
        img = np.expand_dims(img, axis=[0, -1])

        pred = model.predict(img, verbose=0)[0]
        idx = np.argmax(pred)

        label = labels[idx]
        conf = pred[idx]

        cv2.putText(frame, f"{label} {conf:.2f}",
                    (50,50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,(0,255,0),2)

    frame_window.image(frame, channels="BGR")