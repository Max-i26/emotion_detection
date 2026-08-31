import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, BatchNormalization, MaxPooling2D, Flatten, Dense, Dropout, Input
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix

# 1. Reconstruct model architecture matching the weights
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

# 2. Load the weights from the saved h5 model
weights_path = "model/emotion_model.h5"
print("Loading weights from:", weights_path)
model.load_weights(weights_path)
print("Weights loaded successfully.")

# 3. Load the test dataset (grayscale 48x48)
print("Loading test data...")
test_datagen = ImageDataGenerator(rescale=1./255)
test_data = test_datagen.flow_from_directory(
    "dataset/test",
    target_size=(48, 48),
    color_mode="grayscale",
    class_mode="categorical",
    batch_size=32,
    shuffle=False
)

# 4. Compile and Evaluate
model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

print("Evaluating model on test dataset...")
loss, accuracy = model.evaluate(test_data, verbose=1)
print(f"\n======================================")
print(f"Test Loss:     {loss:.4f}")
print(f"Test Accuracy: {accuracy*100:.2f}%")
print(f"======================================\n")

# 5. Predictions & Detailed Reports
print("Generating predictions...")
predictions = model.predict(test_data, verbose=1)
predicted_classes = np.argmax(predictions, axis=1)
true_classes = test_data.classes
class_labels = list(test_data.class_indices.keys())

print("\n--- Classification Report ---")
report = classification_report(true_classes, predicted_classes, target_names=class_labels, digits=4)
print(report)

print("\n--- Confusion Matrix ---")
cm = confusion_matrix(true_classes, predicted_classes)
print("Classes:", class_labels)
print(cm)
