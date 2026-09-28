import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, BatchNormalization, MaxPooling2D, Flatten, Dense, Dropout, Input, GlobalAveragePooling2D
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.regularizers import l2
from sklearn.utils.class_weight import compute_class_weight

# =========================
# GPU CONFIGURATION
# =========================
gpus = tf.config.list_physical_devices('GPU')
print("Available GPUs:", gpus)
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print("✅ Dynamic GPU memory growth enabled.")
    except Exception as e:
        print("⚠️ GPU config warning:", e)

# =========================
# CONFIG & HYPERPARAMETERS
# =========================
IMG_SIZE = 48
BATCH_SIZE = 32
EPOCHS = 60
NUM_CLASSES = 7

train_dir = "dataset/train"
test_dir = "dataset/test"

os.makedirs("model", exist_ok=True)

# =========================
# DATA AUGMENTATION
# =========================
train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.15,
    rotation_range=20,
    width_shift_range=0.15,
    height_shift_range=0.15,
    shear_range=0.15,
    zoom_range=0.15,
    brightness_range=[0.8, 1.2],
    horizontal_flip=True,
    fill_mode="nearest"
)

test_datagen = ImageDataGenerator(rescale=1./255)

# Data Loaders
train_data = train_datagen.flow_from_directory(
    train_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    color_mode="grayscale",
    class_mode="categorical",
    batch_size=BATCH_SIZE,
    subset="training",
    shuffle=True
)

val_data = train_datagen.flow_from_directory(
    train_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    color_mode="grayscale",
    class_mode="categorical",
    batch_size=BATCH_SIZE,
    subset="validation",
    shuffle=False
)

test_data = test_datagen.flow_from_directory(
    test_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    color_mode="grayscale",
    class_mode="categorical",
    batch_size=BATCH_SIZE,
    shuffle=False
)

# =========================
# CLASS WEIGHTS
# =========================
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_data.classes),
    y=train_data.classes
)
class_weights = dict(enumerate(class_weights))
print("Balanced Class Weights:", class_weights)

# =========================
# FOCAL LOSS WITH LABEL SMOOTHING
# =========================
def categorical_focal_loss(gamma=2.0, alpha=None, label_smoothing=0.1):
    def focal_loss(y_true, y_pred):
        # Apply label smoothing
        if label_smoothing > 0:
            num_classes = tf.cast(tf.shape(y_true)[-1], y_true.dtype)
            y_true = y_true * (1.0 - label_smoothing) + (label_smoothing / num_classes)
            
        y_pred = tf.clip_by_value(y_pred, 1e-7, 1.0 - 1e-7)
        cross_entropy = -y_true * tf.math.log(y_pred)
        weight = tf.pow(1.0 - y_pred, gamma)
        
        if alpha is not None:
            weight = weight * alpha
            
        loss = weight * cross_entropy
        return tf.reduce_sum(loss, axis=-1)
    return focal_loss

# =========================
# UPGRADED 4-STAGE CNN ARCHITECTURE
# =========================
def build_upgraded_cnn():
    model = Sequential([
        Input(shape=(IMG_SIZE, IMG_SIZE, 1)),
        
        # Block 1
        Conv2D(64, (3, 3), padding='same', activation='relu', kernel_regularizer=l2(1e-4)),
        BatchNormalization(),
        Conv2D(64, (3, 3), padding='same', activation='relu', kernel_regularizer=l2(1e-4)),
        BatchNormalization(),
        MaxPooling2D((2, 2)),
        Dropout(0.25),
        
        # Block 2
        Conv2D(128, (3, 3), padding='same', activation='relu', kernel_regularizer=l2(1e-4)),
        BatchNormalization(),
        Conv2D(128, (3, 3), padding='same', activation='relu', kernel_regularizer=l2(1e-4)),
        BatchNormalization(),
        MaxPooling2D((2, 2)),
        Dropout(0.3),
        
        # Block 3
        Conv2D(256, (3, 3), padding='same', activation='relu', kernel_regularizer=l2(1e-4)),
        BatchNormalization(),
        Conv2D(256, (3, 3), padding='same', activation='relu', kernel_regularizer=l2(1e-4)),
        BatchNormalization(),
        MaxPooling2D((2, 2)),
        Dropout(0.35),
        
        # Block 4
        Conv2D(512, (3, 3), padding='same', activation='relu', kernel_regularizer=l2(1e-4)),
        BatchNormalization(),
        Conv2D(512, (3, 3), padding='same', activation='relu', kernel_regularizer=l2(1e-4)),
        BatchNormalization(),
        MaxPooling2D((2, 2)),
        Dropout(0.4),
        
        # Head
        GlobalAveragePooling2D(),
        Dense(256, activation='relu', kernel_regularizer=l2(1e-4)),
        BatchNormalization(),
        Dropout(0.5),
        Dense(NUM_CLASSES, activation='softmax')
    ])
    return model

model = build_upgraded_cnn()
model.summary()

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss=categorical_focal_loss(gamma=2.0, label_smoothing=0.1),
    metrics=["accuracy"]
)

# Callbacks
callbacks = [
    EarlyStopping(
        monitor="val_accuracy",
        patience=12,
        restore_best_weights=True
    ),
    ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=4,
        min_lr=1e-7,
        verbose=1
    ),
    ModelCheckpoint(
        "model/emotion_model_weights.h5",
        monitor="val_accuracy",
        save_best_only=True,
        save_weights_only=True,
        verbose=1
    )
]

# =========================
# TRAIN MODEL
# =========================
print("\n🔥 Starting Model Training with Focal Loss & Label Smoothing...")
history = model.fit(
    train_data,
    validation_data=val_data,
    epochs=EPOCHS,
    class_weight=class_weights,
    callbacks=callbacks
)

# Save final weights and full model
model.save_weights("model/emotion_model.h5")
print("\n✅ Training completed! Weights saved to model/emotion_model.h5")

# Evaluate on test set
print("\nEvaluating on Test Set...")
test_loss, test_acc = model.evaluate(test_data)
print(f"Test Loss: {test_loss:.4f}")
print(f"Test Accuracy: {test_acc*100:.2f}%")