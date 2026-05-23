import streamlit as st
import numpy as np
from PIL import Image

st.title("Emotion AI (Demo Mode)")

st.write("Upload an image for preview (model runs locally, not cloud)")

file = st.file_uploader("Upload Image", type=["jpg","png","jpeg"])

if file:
    img = Image.open(file)
    st.image(img, caption="Uploaded Image")

    st.warning("Cloud version does not run TensorFlow due to environment limits.")
    st.info("Run full AI locally using detect_mediapipe.py")