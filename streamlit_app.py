import streamlit as st
import tensorflow as tf
import numpy as np
import cv2
from PIL import Image

# Load model
model = tf.keras.models.load_model("model/emotion_model.h5")

labels = [
    "Angry",
    "Disgust",
    "Fear",
    "Happy",
    "Sad",
    "Surprise",
    "Neutral"
]

st.title("Emotion Detection AI")

uploaded_file = st.file_uploader(
    "Upload Face Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:

    image = Image.open(uploaded_file)
    img = np.array(image)

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    face = cv2.resize(gray, (48, 48))

    face = face.astype("float32") / 255.0
    face = np.expand_dims(face, axis=-1)
    face = np.expand_dims(face, axis=0)

    prediction = model.predict(face)[0]

    idx = np.argmax(prediction)

    label = labels[idx]
    confidence = prediction[idx] * 100

    st.image(image, caption="Uploaded Image")

    st.success(
        f"Emotion: {label} ({confidence:.2f}%)"
    )