@echo off
setlocal

echo ==========================================
echo  Emotion AI - Real-Time MediaPipe Detector
echo ==========================================
echo.
echo  Packages: tensorflow 2.15 / mediapipe 0.10.9 / opencv 4.8 / numpy 1.26
echo  Model:    model/emotion_model.h5  (7-class CNN, ~63%% accuracy on FER2013)
echo.
echo  Starting webcam... Press Q in the window to exit.
echo ==========================================
echo.

.\venv_win\Scripts\python.exe live_detect_pro.py

echo.
echo Emotion detection stopped.
pause
