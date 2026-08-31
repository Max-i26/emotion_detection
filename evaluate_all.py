import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import Conv2D, BatchNormalization, MaxPooling2D, Flatten, Dense, Dropout, Input
from sklearn.metrics import classification_report, confusion_matrix
import json

CLASS_LABELS = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

def evaluate_custom_cnn():
    print("=" * 60)
    print("Evaluating Custom CNN (model/emotion_model.h5) on 48x48 Grayscale")
    print("=" * 60)
    
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
    
    weights_path = "model/emotion_model.h5"
    if not os.path.exists(weights_path):
        print(f"Error: {weights_path} not found.")
        return None
        
    model.load_weights(weights_path)
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    
    test_datagen = ImageDataGenerator(rescale=1./255)
    test_data = test_datagen.flow_from_directory(
        "dataset/test",
        target_size=(48, 48),
        color_mode="grayscale",
        class_mode="categorical",
        batch_size=32,
        shuffle=False
    )
    
    loss, accuracy = model.evaluate(test_data, verbose=1)
    predictions = model.predict(test_data, verbose=1)
    predicted_classes = np.argmax(predictions, axis=1)
    true_classes = test_data.classes
    
    report = classification_report(true_classes, predicted_classes, target_names=CLASS_LABELS, digits=4, output_dict=True)
    report_text = classification_report(true_classes, predicted_classes, target_names=CLASS_LABELS, digits=4)
    cm = confusion_matrix(true_classes, predicted_classes).tolist()
    
    print("\nCustom CNN Results:")
    print(f"Test Loss:     {loss:.4f}")
    print(f"Test Accuracy: {accuracy*100:.2f}%")
    print("\nClassification Report:\n", report_text)
    print("\nConfusion Matrix:\n", np.array(cm))
    
    return {
        "model_name": "Custom CNN (48x48 Grayscale)",
        "test_loss": float(loss),
        "test_accuracy": float(accuracy),
        "classification_report_text": report_text,
        "classification_report": report,
        "confusion_matrix": cm
    }

def evaluate_efficientnet():
    print("\n" + "=" * 60)
    print("Evaluating EfficientNetB0 (model/emotion_maximized_model.keras) on 96x96 RGB")
    print("=" * 60)
    
    model_path = "model/emotion_maximized_model.keras"
    if not os.path.exists(model_path):
        print(f"File {model_path} not found.")
        return None
        
    try:
        model = load_model(model_path)
    except Exception as e:
        print(f"Error loading {model_path}: {e}")
        return None
        
    test_datagen = ImageDataGenerator()
    test_data = test_datagen.flow_from_directory(
        "dataset/test",
        target_size=(96, 96),
        color_mode="rgb",
        class_mode="categorical",
        batch_size=32,
        shuffle=False
    )
    
    loss, accuracy = model.evaluate(test_data, verbose=1)
    predictions = model.predict(test_data, verbose=1)
    predicted_classes = np.argmax(predictions, axis=1)
    true_classes = test_data.classes
    
    report = classification_report(true_classes, predicted_classes, target_names=CLASS_LABELS, digits=4, output_dict=True)
    report_text = classification_report(true_classes, predicted_classes, target_names=CLASS_LABELS, digits=4)
    cm = confusion_matrix(true_classes, predicted_classes).tolist()
    
    print("\nEfficientNetB0 Results:")
    print(f"Test Loss:     {loss:.4f}")
    print(f"Test Accuracy: {accuracy*100:.2f}%")
    print("\nClassification Report:\n", report_text)
    print("\nConfusion Matrix:\n", np.array(cm))
    
    return {
        "model_name": "EfficientNetB0 Transfer Learning (96x96 RGB)",
        "test_loss": float(loss),
        "test_accuracy": float(accuracy),
        "classification_report_text": report_text,
        "classification_report": report,
        "confusion_matrix": cm
    }

if __name__ == "__main__":
    results = {}
    cnn_res = evaluate_custom_cnn()
    if cnn_res:
        results["custom_cnn"] = cnn_res
    eff_res = evaluate_efficientnet()
    if eff_res:
        results["efficientnet"] = eff_res
        
    with open("performance_metrics.json", "w") as f:
        json.dump(results, f, indent=4)
    print("\n✅ Metrics saved to performance_metrics.json")
