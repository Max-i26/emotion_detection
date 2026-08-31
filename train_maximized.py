import tensorflow as tf
import numpy as np
import os

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D, Input
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, Callback
from sklearn.utils.class_weight import compute_class_weight

# ==========================================
# 1. GPU CONFIGURATION & MEMORY GROWTH
# ==========================================
gpus = tf.config.list_physical_devices('GPU')
print("Available GPUs:", gpus)
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print("✅ Dynamic GPU memory growth enabled.")
    except RuntimeError as e:
        print("❌ Error configuring GPU memory growth:", e)

# ==========================================
# 2. HYPERPARAMETERS
# ==========================================
IMG_SIZE = 96
BATCH_SIZE = 32
STAGE1_EPOCHS = 40  # Stage 1: epochs 0 to 40
STAGE2_EPOCHS = 65  # Stage 2: epochs 40 to 65 (total 25 epochs fine-tuning)
NUM_CLASSES = 7

train_dir = "dataset/train"
test_dir = "dataset/test"

os.makedirs("model", exist_ok=True)

# Custom callback to log the last completed epoch
class EpochLogger(Callback):
    def __init__(self, filename="model/last_epoch.txt"):
        super(EpochLogger, self).__init__()
        self.filename = filename
    def on_epoch_end(self, epoch, logs=None):
        with open(self.filename, "w") as f:
            f.write(str(epoch + 1))
        print(f"\n📝 Logged completed epoch: {epoch + 1}")

# ==========================================
# 3. ROBUST DATA AUGMENTATION (No rescaling)
# ==========================================
train_datagen = ImageDataGenerator(
    validation_split=0.2,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.15,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode="nearest"
)

test_datagen = ImageDataGenerator()

# ==========================================
# 4. DATA LOADERS
# ==========================================
print("\nLoading datasets...")
train_data = train_datagen.flow_from_directory(
    train_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    color_mode="rgb",
    class_mode="categorical",
    batch_size=BATCH_SIZE,
    subset="training",
    shuffle=True
)

val_data = train_datagen.flow_from_directory(
    train_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    color_mode="rgb",
    class_mode="categorical",
    batch_size=BATCH_SIZE,
    subset="validation",
    shuffle=False
)

test_data = test_datagen.flow_from_directory(
    test_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    color_mode="rgb",
    class_mode="categorical",
    batch_size=BATCH_SIZE,
    shuffle=False
)

# ==========================================
# 5. CLASS WEIGHT BALANCING
# ==========================================
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_data.classes),
    y=train_data.classes
)
class_weights = dict(enumerate(class_weights))
print("\nBalanced Class Weights:", class_weights)

# ==========================================
# 6. RESUME DETECTION & MODEL BUILDING
# ==========================================
checkpoint_path = "model/emotion_maximized_model.keras"
epoch_log_path = "model/last_epoch.txt"

last_completed_epoch = 0
if os.path.exists(epoch_log_path) and os.path.exists(checkpoint_path):
    try:
        with open(epoch_log_path, "r") as f:
            last_completed_epoch = int(f.read().strip())
        print(f"\n🔄 Resuming training from epoch {last_completed_epoch + 1}...")
        model = load_model(checkpoint_path)
        print("✅ Model loaded successfully from checkpoint.")
    except Exception as e:
        print("⚠️ Could not load checkpoint, starting from scratch. Error:", e)
        last_completed_epoch = 0

if last_completed_epoch == 0:
    print("\n🆕 Building model from scratch based on Pretrained EfficientNetB0...")
    base_model = EfficientNetB0(
        include_top=False,
        weights="imagenet",
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )
    base_model.trainable = False  # Freeze EfficientNet weights in Stage 1

    inputs = Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    x = base_model(inputs, training=False)
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation="relu")(x)
    x = Dropout(0.5)(x)
    outputs = Dense(NUM_CLASSES, activation="softmax")(x)

    model = Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

# Callbacks
callbacks = [
    EarlyStopping(
        monitor="val_accuracy",
        patience=10,
        restore_best_weights=True
    ),
    ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=3,
        min_lr=1e-7,
        verbose=1
    ),
    ModelCheckpoint(
        checkpoint_path,
        monitor="val_accuracy",
        save_best_only=True,
        verbose=1
    ),
    EpochLogger(epoch_log_path)
]

# ==========================================
# 7. STAGE 1: TRAIN CLASSIFIER HEAD
# ==========================================
if last_completed_epoch < STAGE1_EPOCHS:
    print(f"\n🔥 STAGE 1: Training classifier head (Epoch {last_completed_epoch + 1} to {STAGE1_EPOCHS})")
    model.fit(
        train_data,
        validation_data=val_data,
        epochs=STAGE1_EPOCHS,
        initial_epoch=last_completed_epoch,
        class_weight=class_weights,
        callbacks=callbacks
    )
    # Ensure last completed epoch is marked as STAGE1_EPOCHS
    last_completed_epoch = STAGE1_EPOCHS
    with open(epoch_log_path, "w") as f:
        f.write(str(last_completed_epoch))

# ==========================================
# 8. STAGE 2: FINE-TUNING THE BASE MODEL
# ==========================================
if last_completed_epoch < STAGE2_EPOCHS:
    print(f"\n🔥 STAGE 2: Fine-tuning base model (Epoch {last_completed_epoch + 1} to {STAGE2_EPOCHS})")
    
    # Check if base model needs to be unfrozen
    # (If we loaded the model from checkpoint, we need to locate the base model layer and unfreeze it)
    base_model_layer = None
    for layer in model.layers:
        if isinstance(layer, Model) or (hasattr(layer, 'name') and 'efficientnet' in layer.name):
            base_model_layer = layer
            break

    if base_model_layer:
        print(f"Unfreezing top layers of {base_model_layer.name}...")
        base_model_layer.trainable = True
        for layer in base_model_layer.layers[:-30]:
            layer.trainable = False
    else:
        print("⚠️ Warning: Could not find base model layer to unfreeze. Training whole model...")
        model.trainable = True

    # Recompile with fine-tuning learning rate
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    model.fit(
        train_data,
        validation_data=val_data,
        epochs=STAGE2_EPOCHS,
        initial_epoch=last_completed_epoch,
        class_weight=class_weights,
        callbacks=callbacks
    )

# ==========================================
# 9. EVALUATION & SAVE FINAL MODEL
# ==========================================
print("\nSaving final model weights...")
model.save("model/emotion_maximized_model.h5")
print("✅ Model saved to model/emotion_maximized_model.h5")

# Clear the resume log files as training successfully finished
if os.path.exists(epoch_log_path):
    os.remove(epoch_log_path)

print("\nEvaluating model on the test dataset...")
test_loss, test_acc = model.evaluate(test_data)
print(f"\n======================================")
print(f"Maximized Model Test Loss:     {test_loss:.4f}")
print(f"Maximized Model Test Accuracy: {test_acc*100:.2f}%")
print(f"======================================\n")
