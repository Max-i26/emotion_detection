# 🧠 Real-Time Facial Emotion Recognition — Everything Explained in Simple English

> **Who is this for?** Anyone who wants to understand how this project works from the ground up — no PhD required. Every concept is explained with real-world examples.

---

## 📋 Table of Contents

1. [What Does This Project Do?](#1-what-does-this-project-do)
2. [The Big Picture — How It All Flows](#2-the-big-picture--how-it-all-flows)
3. [The Dataset — FER2013](#3-the-dataset--fer2013)
4. [The Problems We Faced](#4-the-problems-we-faced)
5. [How We Overcame Each Problem](#5-how-we-overcame-each-problem)
6. [The Technology Stack](#6-the-technology-stack)
7. [How the Model Gets Trained](#7-how-the-model-gets-trained)
8. [The Neural Network Architecture](#8-the-neural-network-architecture)
9. [The Focal Loss — Our Secret Weapon](#9-the-focal-loss--our-secret-weapon)
10. [Real-Time Detection Pipeline](#10-real-time-detection-pipeline)
11. [Performance Metrics Explained](#11-performance-metrics-explained)
12. [Results and What They Mean](#12-results-and-what-they-mean)
13. [Glossary — Plain English Definitions](#13-glossary--plain-english-definitions)

---

## 1. What Does This Project Do?

**In one sentence:** Your webcam watches your face and a computer figures out how you're feeling — in real time.

### Real-World Analogy 🎭

Imagine you're a customer service manager watching your employees talk to customers. You can tell from their faces if a customer is angry, happy, or confused. This project teaches a computer to do exactly that — look at a face and say *"that person looks Happy"* or *"that person looks Afraid"* — **30 times per second**.

### The 7 Emotions It Recognises

| Emotion | Real-World Example |
|---------|-------------------|
| 😠 **Angry** | Someone just got cut off in traffic |
| 😨 **Fear** | Someone watching a horror movie jump-scare |
| 😢 **Sad** | Someone reading bad news |
| 😄 **Happy** | Someone seeing their best friend after years |
| 😮 **Surprise** | Someone getting a surprise birthday party |
| 😒 **Disgust** | Someone smelling something terrible |
| 😐 **Neutral** | Someone staring at their phone on a bus |

---

## 2. The Big Picture — How It All Flows

Here's the complete journey from your face to a prediction, **one step at a time**:

```
YOUR FACE
    │
    ▼
📷 WEBCAM captures video
    │  (30 pictures per second, like a video)
    ▼
🔍 MEDIAPIPE finds your face
    │  (draws a box around just your face)
    ▼
✂️  CROP + RESIZE to 48×48 pixels
    │  (shrinks to a tiny stamp-sized image)
    ▼
🔲 CONVERT to grayscale
    │  (removes colour, makes it black & white)
    ▼
📊 NORMALISE pixel values
    │  (converts 0-255 numbers to 0.0-1.0)
    ▼
🧠 4-STAGE CNN analyses the face
    │  (the brain of the system, trained on 28,000 faces)
    ▼
📈 SOFTMAX gives 7 probability scores
    │  (e.g. Happy: 82%, Neutral: 10%, Sad: 4% ...)
    ▼
🗳️  MAJORITY VOTE across 10 frames
    │  (smooths out rapid flickering)
    ▼
🖥️  DISPLAY "Happy (82%)" on screen
```

### Simple Analogy for the Whole Flow

Think of it like **a doctor diagnosing a patient**:
1. Patient walks in (your face appears on webcam)
2. Doctor looks at the patient (MediaPipe finds the face)
3. Doctor focuses on the face specifically (crop + resize)
4. Doctor notes the features (CNN analyses)
5. Doctor considers 10 seconds of observation (10-frame buffer)
6. Doctor gives a diagnosis (emotion label displayed)

---

## 3. The Dataset — FER2013

### What is a Dataset?

A dataset is a **giant collection of example images** that we show the computer so it can learn. Think of it like a textbook full of example faces.

### FER2013 — The Textbook We Used

| Property | Value |
|----------|-------|
| **Full Name** | Facial Expression Recognition 2013 |
| **Total Images** | 35,887 faces |
| **Training Images** | 28,709 |
| **Test Images** | 7,178 |
| **Image Size** | 48×48 pixels (tiny!) |
| **Colour** | Grayscale (black & white) |
| **Source** | Google Image Search (automated) |

### What Each Image Looks Like

```
Each image is 48×48 pixels — that's a 48×48 grid of grey dots.
Like this, but much smaller:

████████████████████████
███░░░░░░░░░░░░░░░░██████  
███░░░░░░░░░░░░░░░░██████  ← A face that's 48 pixels wide
███░░░░░░  ░░░░░░░░██████    and 48 pixels tall.
███░░░░░░  ░░░░░░░░██████  
███░░░░░░░░░░░░░░░░██████  
████████████████████████
```

### How Many Images Per Emotion?

```
Emotion      Training Images   Test Images
─────────────────────────────────────────
Happy        7,215 ████████████████████████  ← Most!
Neutral      4,965 ████████████████
Sad          4,830 ████████████████
Fear         4,097 █████████████
Angry        3,995 █████████████
Surprise     3,171 ██████████
Disgust        436 █           ← Almost nothing!
```

> **The Big Problem:** Happy has **16.5 times more** images than Disgust.  
> That's like trying to learn French by only studying 1 French word but 16 words of English — you'll never learn French properly!

### How Was FER2013 Collected?

1. A computer searched Google Images with keywords like "angry face", "happy face"
2. It automatically detected and cropped the face from each image
3. The emotion label came from the search keyword (automated — not manually verified)
4. **Result:** Some images are mislabelled because a "surprised" face might actually look scared

### Real-World Problem This Creates

Imagine a teacher who gave students a textbook where **30% of the answers are wrong**. Students who study from it will learn incorrectly. That's why even a perfect AI model trained on FER2013 can only reach about **65% accuracy** — not because the AI is bad, but because the textbook itself has mistakes.

---

## 4. The Problems We Faced

### Problem 1: Class Imbalance 📊

**What it is:** Some emotions have way fewer training examples than others.

**Real-World Analogy:**  
Imagine training a dog to recognise 7 different commands. You practice "Sit" 7,215 times and "Roll Over" only 436 times. The dog will be great at Sit but terrible at Roll Over — not because the dog is stupid, but because it barely practised Roll Over.

**Effect on the model:**  
The computer learned to guess "Happy" or "Neutral" very often because those were most common in training. It barely learned what "Disgust" looks like.

---

### Problem 2: Label Noise 🏷️

**What it is:** Some training images have wrong labels.

**Real-World Analogy:**  
If someone shows you 100 photos and tells you "this is a cat" — but 30 of those photos are actually dogs mislabelled as cats — you'll get confused about what a cat looks like.

**Effect on the model:**  
Some "Fear" faces are actually mislabelled "Surprise" faces. The model gets confused trying to learn the difference between two classes that sometimes look identical in the training data.

---

### Problem 3: Face Detection Failures 🔍

**What it was (original attempt):** We first tried OpenCV's **Haar Cascade** face detector (an older method from 2001).

**What went wrong:**  
- Lost tracking when your head turned sideways even slightly
- Confused shadows with faces (false positives)
- Flickered on and off when lighting changed
- Very sensitive to glasses and facial hair

**Real-World Analogy:**  
Like using a 20-year-old map to navigate — it works for major highways but fails on new roads.

---

### Problem 4: Prediction Flickering ⚡

**What it is:** The model changes its prediction every few frames.

**What it looked like:**  
```
Frame 1: Happy
Frame 2: Neutral    ← same face, barely moved!
Frame 3: Happy
Frame 4: Sad        ← this is distracting to watch
Frame 5: Happy
```

**Real-World Analogy:**  
Like a thermostat that turns the heater on and off every 2 seconds instead of keeping it stable. Technically correct each time, but practically useless.

---

### Problem 5: Module Not Found Errors 🔧

**What happened:**  
```
ModuleNotFoundError: No module named 'cv2'
```

**What it meant:** The correct version of libraries wasn't installed in the right Python environment.

**Why it happened:** Some libraries (TensorFlow, MediaPipe, OpenCV) have strict version compatibility requirements. An incompatible combination breaks everything.

---

### Problem 6: Fear and Surprise Look Similar 😨😮

**What it is:** Some emotions share the same facial muscles.

**Real-World Analogy:**  
Fear and Surprise both involve:
- Raised eyebrows ↑
- Wide open eyes 👀
- Slightly open mouth

The difference is subtle (Fear has more tension, Surprise is more open). Even humans confuse these about 35% of the time. The computer does too.

---

## 5. How We Overcame Each Problem

### Solution 1: Focal Loss (for Class Imbalance)

**What we did:** Created a smarter loss function that makes the model **pay more attention to hard, rare examples**.

**How it works — simple analogy:**

Imagine you're a student preparing for an exam:
- Questions you always get right (Happy, Neutral) → spend less time on them
- Questions you keep getting wrong (Fear, Disgust) → spend more time on them

Normal training: Spends equal time on everything.  
**Focal Loss:** Automatically spends more time on the hard ones.

**The math in plain English:**
```
Normal Loss: "Wrong answer costs 1 point, always"

Focal Loss: "Wrong answer on an EASY question costs 0.01 points
             Wrong answer on a HARD question costs 0.81 points"

This 81× difference forces the model to focus on Disgust and Fear!
```

---

### Solution 2: Label Smoothing (for Label Noise)

**What we did:** Instead of treating training labels as absolute truth (100% sure this is Happy), we tell the model "this is probably Happy (90%) with a tiny chance of being something else (1.4% each)".

**Real-World Analogy:**  
Instead of a teacher saying "the answer is DEFINITELY 42", they say "the answer is most likely 42, but there's a small chance I'm wrong". This makes the student more humble and less overconfident — which is better for learning.

**Result:** The model doesn't get overconfident on mislabelled examples. It learns more cautiously and generalises better.

---

### Solution 3: MediaPipe (for Face Detection)

**What we switched to:** Google's **MediaPipe BlazeFace** — a modern, AI-based face detector.

**How it's different:**
| Feature | Old (Haar Cascade) | New (MediaPipe) |
|---------|-------------------|-----------------|
| Technology | 2001 | 2019 |
| Head rotation tolerance | ±15° | ±45° |
| Speed | 10ms | 4ms |
| False positives | Many | Few |
| Glasses/occlusion | Struggles | Handles well |

**Real-World Analogy:**  
Switching from paper maps to Google Maps. Both get you there, but Google Maps handles road closures, traffic, and alternative routes much better.

---

### Solution 4: Temporal Smoothing (for Flickering)

**What we did:** Instead of showing the prediction from the current frame, we keep a **memory of the last 10 frames** and show the most common prediction.

**Exactly how it works:**
```
Frame memory (last 10 frames):
[Happy, Happy, Neutral, Happy, Happy, Sad, Happy, Happy, Neutral, Happy]

Count:
- Happy: 7 times ← WINNER — show "Happy"
- Neutral: 2 times
- Sad: 1 time
```

**Real-World Analogy:**  
Like a jury system. Instead of one juror deciding (noisy, can be wrong), 10 jurors vote and the majority wins (stable, more reliable).

---

### Solution 5: Compatible Environment Setup (for Import Errors)

**What we did:** Carefully pinned exact compatible versions:

```
tensorflow==2.15.0
tensorflow-intel==2.15.0
mediapipe==0.10.9
opencv-python==4.8.0.76
numpy==1.26.4
keras==2.15.0
```

**Why specific versions:** Like a recipe — if you substitute baking soda for baking powder, the cake fails. Software libraries have the same strict compatibility requirements.

---

### Solution 6: 4-Stage Deep Architecture (for Accuracy)

**What we did:** Used a deeper, wider network with more layers to learn more complex facial features.

**Real-World Analogy:**  
- A shallow network: like a doctor who only did a 1-year residency — can spot obvious symptoms
- Our 4-Stage network: like a specialist with 10 years of training — can spot subtle patterns

---

## 6. The Technology Stack

### Every Tool Explained

---

#### 🐍 Python 3.10
**What it is:** The programming language everything is written in.  
**Why we used it:** The entire AI/ML ecosystem (TensorFlow, NumPy, OpenCV) is built for Python. It's the universal language of machine learning.  
**Real-World Analogy:** Python is like English — everyone in the ML world speaks it.

---

#### 🧠 TensorFlow 2.15.0
**What it is:** Google's framework for building and training neural networks.  
**Why we used it:** It handles all the complex mathematics (matrix multiplications, gradient calculations) automatically. Without it, implementing a neural network from scratch would take months.  
**Real-World Analogy:** TensorFlow is like a car engine. You don't need to understand how combustion works — you just press the accelerator.

---

#### 🎯 Keras (built into TensorFlow)
**What it is:** A high-level API that makes building neural networks simpler.  
**Why we used it:** You write `model.add(Dense(256))` instead of writing 50 lines of matrix math.  
**Real-World Analogy:** Keras is like IKEA furniture instructions — the underlying engineering is complex, but you just follow simple steps.

---

#### 👁️ MediaPipe 0.10.9
**What it is:** Google's toolkit for processing video, specifically finding faces.  
**Why we used it:** State-of-the-art accuracy, 4ms detection speed, works well with head rotation and glasses.  
**Real-World Analogy:** Like having a specialist whose only job is to find faces in a crowd — perfectly tuned for that single task.

---

#### 📷 OpenCV 4.8.0
**What it is:** Open Computer Vision library — handles camera capture, image processing.  
**Why we used it:** Reads camera frames, converts colours (BGR→RGB→Grayscale), draws boxes on the display screen.  
**Real-World Analogy:** OpenCV is like the film projector — it handles getting the raw images in and out. The AI just handles the analysis.

---

#### 🔢 NumPy 1.26.4
**What it is:** Python library for fast numerical array computations.  
**Why we used it:** Images are just grids of numbers. NumPy handles these massive numerical arrays efficiently.  
**Real-World Analogy:** NumPy is like a giant spreadsheet that can do millions of calculations per second.

---

#### 📊 Matplotlib 3.10
**What it is:** Python plotting library — creates charts and graphs.  
**Why we used it:** Generated all the figures in the report (confusion matrix, F1 charts, training curves).  
**Real-World Analogy:** Like Excel charts, but fully customisable and programmable.

---

#### 💾 h5py 3.14
**What it is:** Library for reading/writing HDF5 files (a data format).  
**Why we used it:** Saves and loads the trained model weights (the "brain" of the AI).  
**Real-World Analogy:** Like saving a document — h5py saves the AI's learned knowledge to disk so it doesn't have to re-learn everything every time you run it.

---

#### 🐙 Git + GitHub
**What it is:** Version control system + code hosting platform.  
**Why we used it:** Tracks every code change, allows collaboration, provides backup, enables sharing.  
**Real-World Analogy:** Like "Track Changes" in Microsoft Word, but for code — and shared with the world.

---

#### 🖥️ WSL2 (Windows Subsystem for Linux 2)
**What it is:** A way to run Linux on a Windows computer.  
**Why we used it:** The GPU training drivers (CUDA) work best on Linux. We used WSL2 for GPU training, then moved the weights to Windows for testing.  
**Real-World Analogy:** Like having a separate workshop (Linux/GPU) for heavy building work, and a regular desk (Windows) for everyday use.

---

## 7. How the Model Gets Trained

### The Learning Process in Plain English

Training is like **teaching a baby to recognise emotions**:

1. **Show the baby a face** (show the model an image)
2. **Tell them what emotion it is** (provide the correct label)
3. **Baby makes a guess** (model predicts a probability)
4. **Tell them if they're wrong** (compute the loss/error)
5. **Baby adjusts their understanding** (backpropagation updates weights)
6. **Repeat 28,709 times per epoch** (one pass through all training data)
7. **Do this for 52 epochs** (52 full passes through all training data)

### What is an Epoch?

**Epoch** = One complete pass through all 28,709 training images.

```
Epoch 1:  Model sees every face once → Accuracy: ~14% (random guessing, 1/7 chance)
Epoch 5:  Model starts recognising Happy reliably → Accuracy: ~35%
Epoch 15: Model gets better at Neutral → Accuracy: ~52%
Epoch 30: Model learns subtle patterns → Accuracy: ~60%
Epoch 52: Training stopped (no more improvement) → Accuracy: ~63.5%
```

### What is a Batch?

Processing 28,709 images one at a time would be slow. Instead, we process **32 images at once** (batch size = 32).

**Real-World Analogy:**  
Like a teacher grading homework. Instead of grading one paper at a time (slow), they grade a stack of 32 papers together and then update the grade book once per stack (faster).

### The Loss Function — The Scoring System

**Loss** measures how wrong the model is. Low loss = doing well. High loss = doing poorly.

```
Example prediction for a "Happy" face:
┌─────────┬───────────┬───────────┐
│ Emotion │ Predicted │  Correct? │
├─────────┼───────────┼───────────┤
│ Angry   │   3%      │  Wrong    │
│ Disgust │   1%      │  Wrong    │
│ Fear    │   2%      │  Wrong    │
│ Happy   │  82%      │ CORRECT ✓ │  ← Should be 100%
│ Sad     │   5%      │  Wrong    │
│ Surprise│   4%      │  Wrong    │
│ Neutral │   3%      │  Wrong    │
└─────────┴───────────┴───────────┘

Loss = how far 82% is from the ideal 100%
     = punishes the model proportionally to how wrong it is
```

### Backpropagation — How the Model Learns

**In plain English:** After every batch of 32 images, the system calculates "how should we change each number (weight) in the network to make the predictions better next time?"

**Real-World Analogy:**  
Like adjusting the recipe after tasting food:
- "Too salty" → reduce salt next time
- "Not sweet enough" → add more sugar next time
- Backpropagation does this for millions of numbers simultaneously

### The Adam Optimiser

**Adam** (Adaptive Moment Estimation) is the algorithm that decides **how much to adjust each weight**.

**Real-World Analogy:**  
Imagine adjusting seasoning in a recipe:
- If you've been consistently reducing salt for the last 5 iterations → Adam reduces salt more aggressively
- If you keep flip-flopping between adding and removing pepper → Adam makes smaller, more cautious pepper changes

Adam is "smart" because it adapts its adjustment speed based on history.

### Learning Rate Decay

**Learning Rate** = how big of an adjustment to make per step.

```
Early training:  Large steps (learning rate = 0.001)
                 ──────────→→→→→→
                 We're far from the answer, take big steps

Late training:   Small steps (learning rate reduced to 0.000125)
                 ──→
                 We're close, take tiny careful steps to fine-tune
```

**Real-World Analogy:**  
Like parallel parking a car:
- Far from the space: turn the wheel a lot (big adjustments)
- Almost in: tiny micro-corrections (small adjustments)

### Early Stopping

The training automatically **stopped at epoch 52** because:
- Validation accuracy stopped improving
- Continuing would cause **overfitting** (memorising training data instead of learning patterns)

**Real-World Analogy:**  
Like a student who keeps re-reading the same textbook. After a certain point, they've memorised it but haven't actually understood the concepts. Early stopping says "you've studied enough — stop before you start memorising instead of learning."

---

## 8. The Neural Network Architecture

### What is a Neural Network?

**A neural network is a mathematical system loosely inspired by the brain.** It's made of layers of numbers (neurons) connected by weights. Training adjusts those weights until the network gets good at its task.

### Our Specific Architecture: 4-Stage ConvNet

Think of our network as a **factory assembly line with 4 stations** that each extract more complex information from the face:

---

#### Station 1 (Block 1) — Edge Detection
```
Input: 48×48 face image (48×48×1 = 2,304 numbers)
       ↓
Conv2D(64 filters) → Finds edges: horizontal lines, vertical lines, diagonals
Conv2D(64 filters) → Combines edges into simple shapes
BatchNorm         → Keeps numbers stable (like quality control)
MaxPool(2×2)      → Shrinks image to 24×24 (keeps important parts)
Dropout(25%)      → Randomly turns off 25% of neurons (prevents overfitting)
       ↓
Output: 24×24×64 = 36,864 numbers
```

**Real-World Analogy:** Station 1 is like a factory worker who spots the outlines of the product — "this piece has a curved edge here, a sharp corner there".

---

#### Station 2 (Block 2) — Shape Recognition
```
Input: 24×24×64
       ↓
Conv2D(128 filters) → Combines edges into shapes (eyes, nose outline)
Conv2D(128 filters) → More complex shape combinations
BatchNorm + MaxPool(2×2) + Dropout(30%)
       ↓
Output: 12×12×128 = 18,432 numbers
```

**Real-World Analogy:** Station 2 recognises "that curved edge + those two dots = an eye".

---

#### Station 3 (Block 3) — Feature Recognition
```
Input: 12×12×128
       ↓
Conv2D(256 filters) → Recognises face parts: raised eyebrow, open mouth
Conv2D(256 filters) → Combinations of face parts
BatchNorm + MaxPool(2×2) + Dropout(35%)
       ↓
Output: 6×6×256 = 9,216 numbers
```

**Real-World Analogy:** Station 3 says "raised eyebrows + wide open eyes = something dramatic is happening".

---

#### Station 4 (Block 4) — Emotion Pattern Recognition
```
Input: 6×6×256
       ↓
Conv2D(512 filters) → Recognises complex emotion-specific patterns
Conv2D(512 filters) → High-level emotion features
BatchNorm + MaxPool(2×2) + Dropout(40%)
       ↓
Output: 3×3×512 = 4,608 numbers
```

**Real-World Analogy:** Station 4 says "raised eyebrows + wide eyes + open mouth + slightly tensed jaw = probably Fear or Surprise".

---

#### Head (Decision Station)
```
GlobalAveragePooling → Compresses 3×3×512 to just 512 numbers
                       (like a summary of all detected features)
Dense(256, ReLU)     → Combines all 512 features intelligently
BatchNorm            
Dropout(50%)         → Highest dropout here — most complex, most overfitting risk
Dense(7, Softmax)    → Outputs 7 probability scores (one per emotion)
       ↓
Output: [Angry: 3%, Disgust: 1%, Fear: 2%, Happy: 82%, Sad: 5%, Surprise: 4%, Neutral: 3%]
```

**Real-World Analogy:** The head is like the factory manager who looks at all the quality reports from 4 stations and makes the final decision: "This is a Happy face."

---

### What is a Convolutional Filter?

A **filter** is a small grid of numbers (e.g., 3×3) that slides across the image and detects a specific pattern.

```
Image patch:        Filter (detects vertical edge):    Result:
┌───┬───┬───┐      ┌────┬────┬────┐                  
│ 0 │ 0 │255│      │ -1 │  0 │  1 │                  Large number
│ 0 │ 0 │255│  ×   │ -1 │  0 │  1 │   =   →   (edge detected!)
│ 0 │ 0 │255│      │ -1 │  0 │  1 │                  
└───┴───┴───┘      └────┴────┴────┘                  

(dark pixels on left, bright pixels on right = vertical edge)
```

Block 1 has 64 different filters — each one learns to detect a different pattern (horizontal edges, diagonal edges, textures, etc.)

---

### Why BatchNorm?

**Batch Normalisation** keeps the numbers flowing through the network in a healthy range.

**Real-World Analogy:**  
Like a voltage regulator in electronics. Even if the input power fluctuates wildly (1V to 1000V), the regulator outputs a stable 5V. BatchNorm ensures that even if one layer outputs wildly different values, the next layer always receives nicely normalised inputs.

**Without BatchNorm:** Training is slow, unstable, gradients can explode or vanish  
**With BatchNorm:** Training is fast, stable, converges reliably

---

### Why Dropout?

**Dropout** randomly turns off a percentage of neurons during training (but not during prediction).

**Real-World Analogy:**  
Like team training in sports: "Today, our star player is absent. The rest of the team must learn to work without them." This forces every player (neuron) to become capable, rather than relying on a few star players.

**Without Dropout:** Network memorises training examples (like a student who memorises answers without understanding)  
**With Dropout:** Network learns general patterns (like a student who understands the concept)

---

### Why Global Average Pooling instead of Flatten?

After Block 4, the output is 3×3×512. We need to reduce it to a single vector.

**Flatten** would create 4,608 numbers → 4,608 × 256 = 1.18 million weights → high overfitting risk

**Global Average Pooling** computes the average of each 3×3 feature map → outputs 512 numbers → 512 × 256 = only 131,072 weights → **9x fewer parameters**, much less overfitting

**Real-World Analogy:**  
Flatten is like transcribing every single word of a 100-page book into a summary.  
GAP is like taking the key theme from each chapter — much more compact.

---

## 9. The Focal Loss — Our Secret Weapon

### The Problem Focal Loss Solves

Standard training loss (Cross-Entropy) treats every example equally:
- The 7,215 Happy training images contribute equally to learning
- The 436 Disgust training images contribute equally to learning

But there are 16.5× more Happy images → Happy dominates the gradient → model gets very good at Happy, ignores Disgust.

### How Focal Loss Works

```
Standard Loss: every wrong answer penalised by 1 point

Focal Loss (gamma=2):
─────────────────────────────────────────────────────
Prediction    Confidence    Penalty
─────────────────────────────────────────────────────
Easy correct  90% sure      (1-0.9)² = 0.01 points  ← Almost ignored
Medium wrong  50% sure      (1-0.5)² = 0.25 points  ← Some penalty
Hard wrong    10% sure      (1-0.1)² = 0.81 points  ← Heavily penalised
─────────────────────────────────────────────────────

The 81× difference between easy and hard examples is what
forces the model to study Disgust and Fear more!
```

### The Complete Focal Loss Formula (in plain English)

```python
# Step 1: Label Smoothing (don't be 100% sure of labels)
y_smooth = y_true × 0.9 + 0.1/7
# "Happy" → 90% chance it's Happy, 1.4% chance it's each other emotion

# Step 2: Clip predictions (avoid log(0) = infinity errors)
y_pred = clip(y_pred, min=0.0000001, max=0.9999999)

# Step 3: Focal weight (harder examples get bigger penalty)
focal_weight = (1 - y_pred) ^ 2.0

# Step 4: Loss = negative weighted log-likelihood
loss = -sum(y_smooth × focal_weight × log(y_pred))
```

### Real-World Example of Focal Loss in Action

Imagine a medical student learning to diagnose rare diseases:
- **Common cold** (very common, like Happy in our dataset): Student has seen it 7,000 times. They know it perfectly. Focal Loss says "you already know this — barely count it in the exam."
- **Rare genetic disorder** (very rare, like Disgust): Student has seen it 436 times. They barely know it. Focal Loss says "you keep getting this wrong — this counts heavily in your grade."

Result: Student (model) is forced to study the rare disease harder, improving their overall diagnostic ability.

---

## 10. Real-Time Detection Pipeline

### How Each Frame Gets Processed (30 times per second)

#### Step 1: Camera Reads a Frame
```
Camera output: BGR image (Blue-Green-Red colour order, OpenCV convention)
Size: 1280×720 pixels (HD resolution)
Rate: 30 frames per second

Why BGR and not RGB? OpenCV was originally built for cameras that output BGR.
It's just a historical convention — the colours are the same, just in different order.
```

#### Step 2: Colour Space Conversion
```
BGR (for screen display)    →    RGB (for MediaPipe)
     ↓                                   ↓
cv2.COLOR_BGR2RGB

Why? MediaPipe was trained on RGB images. Feeding it BGR would be like
giving someone a photo where all reds and blues are swapped — confusing!
```

#### Step 3: MediaPipe Finds the Face
```
Input: 1280×720 RGB image
MediaPipe BlazeFace processes it...
Output: bounding box = {xmin: 0.32, ymin: 0.15, width: 0.25, height: 0.40}
        (values are 0-1, relative to image size)

Convert to pixels:
xmin   = 0.32 × 1280 = 410 pixels from left
ymin   = 0.15 × 720  = 108 pixels from top
width  = 0.25 × 1280 = 320 pixels wide
height = 0.40 × 720  = 288 pixels tall

Crop that rectangle: we now have a face-only image (320×288 pixels)
```

#### Step 4: Preprocess the Face Crop
```
320×288 RGB crop
       ↓
Convert to grayscale (cv2.COLOR_RGB2GRAY)
320×288 grayscale
       ↓
Resize to 48×48 (bilinear interpolation)
48×48 grayscale
       ↓
Divide by 255.0 (normalise to 0.0-1.0)
48×48 float array, values in [0.0, 1.0]
       ↓
Reshape to (1, 48, 48, 1)
(batch=1, height=48, width=48, channels=1)
       ↓
This is the input to the neural network
```

#### Step 5: Neural Network Predicts
```
Input:  (1, 48, 48, 1)
Output: [0.03, 0.01, 0.02, 0.82, 0.05, 0.04, 0.03]
         Angry Disg Fear Happy Sad  Surp  Neut

argmax → 3 (index 3 = Happy)
```

#### Step 6: Temporal Smoothing Buffer
```
Prediction deque (stores last 10 frame predictions):
Before: [2, 3, 3, 2, 3, 0, 3, 3, 2, 3]
         Fear Happy Happy Fear Happy Angry Happy Happy Fear Happy

Count:
- Happy (3): appears 6 times ← WINNER
- Fear  (2): appears 3 times
- Angry (0): appears 1 time

Display: "Happy"

After: add new prediction (3=Happy), drop oldest:
[3, 3, 2, 3, 0, 3, 3, 2, 3, 3]
```

#### Step 7: Display on Screen
```
Draw green rectangle around face
Write "Happy (82%)" above the rectangle
Display the annotated frame
User sees: their face with emotion label overlaid
```

---

## 11. Performance Metrics Explained

### What is Accuracy?

**Accuracy = (Number of correct predictions) / (Total predictions) × 100%**

```
Example:
- 7,178 test images
- Model got 4,558 correct
- Accuracy = 4,558 / 7,178 = 63.51%

Real-world analogy:
If you took a 100-question multiple choice test and got 63.51 right,
your score is 63.51%.
```

---

### What is Precision?

**Precision = Of all the times the model said "X", how often was it actually X?**

```
Example: Precision for Happy = 82.51%

This means: Every time the model says "Happy", it's right 82.51% of the time.
The other 17.49% of its "Happy" predictions were actually a different emotion.

Real-world analogy:
If a metal detector alerts 100 times, and 82.51 of those times there's actually metal:
Precision = 82.51%
The other 17.49 alerts were false alarms.
```

**High precision but low recall = Being very cautious**

---

### What is Recall?

**Recall = Of all the images that ARE emotion X, how many did the model correctly identify?**

```
Example: Recall for Disgust = 40.54%

Of 111 actual Disgust test images, the model correctly identified 45.
The other 66 Disgust images were misclassified as something else.

Recall = 45/111 = 40.54%

Real-world analogy:
If there are 111 criminals in a lineup, and the police correctly identified 45 of them,
the recall is 40.54%.
The other 66 criminals walked free (missed detections).
```

**High recall but low precision = Being very aggressive**

---

### Why the Tension Between Precision and Recall?

```
Strategy A: "Only say Happy when I'm 99% sure"
→ High Precision (every Happy call is correct)
→ Low Recall (miss many Happy faces that were only 85% confident)

Strategy B: "Say Happy whenever I think there's any chance"
→ Low Precision (many false Happy calls)
→ High Recall (catch almost every real Happy face)

We need a BALANCE → that's what F1-Score measures
```

---

### What is F1-Score?

**F1-Score = The balanced average of Precision and Recall**

```
Formula: F1 = 2 × (Precision × Recall) / (Precision + Recall)

Example for Disgust:
Precision = 81.82%
Recall    = 40.54%
F1        = 2 × (0.8182 × 0.4054) / (0.8182 + 0.4054)
          = 2 × 0.3318 / 1.2236
          = 54.22%

Even though Precision is high (81.82%), the low Recall (40.54%)
drags the F1-Score down to 54.22%.

Real-world analogy:
Like a basketball player's combined score for offense AND defense.
Being great at one but terrible at the other = mediocre overall.
```

---

### What is a Confusion Matrix?

A confusion matrix shows **exactly which emotions are confused with which other emotions**.

```
CONFUSION MATRIX (simplified, 7×7 grid):

Each row = "What the image actually was"
Each column = "What the model predicted"

              Predicted →
              Ang  Dis  Fea  Hap  Sad  Sur  Neu
Actual  Ang [ 579    3   87   24  147   46   72 ]
        Dis [  17   45   11    4   17    6   11 ]
        Fea [  88    3  355   26  234  192  126 ]
        Hap [  19    1   15 1528   77   61   73 ]
        Sad [  92    5  133   73  838   43   49 ]
        Sur [  56    2  122   45   68  595  359 ]  ← 359 Surprise faces
        Neu [  35    1   55   52   52   17  619 ]    misclassified as Neutral

Diagonal = correct predictions (the big numbers)
Off-diagonal = mistakes (the small numbers)

Key mistake: Surprise → Neutral (359 times!)
Why? Mild surprise with a partially closed mouth looks a lot like Neutral.
```

---

### What is Weighted F1-Score?

The overall F1-Score that accounts for the fact that different emotions have different numbers of test images.

```
Emotions with more test images are weighted more:

Happy has 1,774 test images → F1 84.28% counts a lot
Disgust has 111 test images → F1 54.22% counts less

Weighted F1 = 62.91%

This gives a realistic overall picture of system performance.
It's like a course grade that weights the final exam (Happy - lots of marks)
more than a quiz (Disgust - few marks).
```

---

### What Does 63.51% Accuracy Mean in Context?

```
Human accuracy on FER2013:  ~65%  ← Even humans make mistakes!
Our model accuracy:          63.51%
                             ──────
Gap from human:              1.49%

Why can't humans do better?
Because some images are genuinely ambiguous — is this slight eyebrow raise
Fear, Surprise, or just a quizzical Neutral?

So our model is only ~1.5% worse than a human 
doing the same task on the same test images.
That's impressive!
```

---

### The Ablation Study — Proving Each Part Matters

An ablation study removes one part at a time to prove each component helps.

```
Configuration                         Test Accuracy
─────────────────────────────────────────────────────
A: Basic 3-Block CNN + Normal Loss       57.34%
B: A + Class Weighting                   59.21%  (+1.87%)
C: A + Focal Loss                        61.47%  (+4.13%)
D: A + Label Smoothing                   58.73%  (+1.39%)
E: 4-Block CNN + Focal + Label Smooth    62.89%  (+5.55%)
F: E + Class Weighting (FULL PROPOSED)  63.51%  (+6.17%)
─────────────────────────────────────────────────────

Each component adds something positive.
The full combination is the best.

Real-world analogy:
Like tuning a race car:
- Better tyres alone: +5 mph
- Better engine alone: +15 mph
- Better aerodynamics alone: +8 mph
- All three together: +35 mph (more than sum due to synergy)
```

---

## 12. Results and What They Mean

### Our Model's Report Card

```
┌────────────┬───────────┬────────┬──────────┬─────────┐
│  Emotion   │ Precision │ Recall │ F1-Score │ Support │
├────────────┼───────────┼────────┼──────────┼─────────┤
│   Happy    │   82.51%  │ 86.13% │  84.28%  │  1,774  │ ← BEST
│   Neutral  │   76.42%  │ 74.49% │  75.44%  │    831  │
│   Sad      │   55.46%  │ 67.96% │  61.08%  │  1,233  │
│   Angry    │   53.71%  │ 60.44% │  56.88%  │    958  │
│   Disgust  │   81.82%  │ 40.54% │  54.22%  │    111  │
│   Surprise │   50.72%  │ 47.71% │  49.17%  │  1,247  │
│   Fear     │   50.79%  │ 34.67% │  41.21%  │  1,024  │ ← HARDEST
├────────────┼───────────┼────────┼──────────┼─────────┤
│  Weighted  │   63.26%  │ 63.51% │  62.91%  │  7,178  │
└────────────┴───────────┴────────┴──────────┴─────────┘
```

### Why Happy is Best (84.28% F1)
- 7,215 training examples → lots of practice
- Distinctive bilateral smile → easy for CNN to detect
- Duchenne smile (eye crinkling + upturned mouth corners) is very unique

### Why Fear is Hardest (41.21% F1)
- Shares raised eyebrows + wide eyes with Surprise
- Shares downturned mouth with Sad
- Shares tense jaw with Angry
- Acts like a visual "overlap zone" between 3 other emotions

### Real-Time Performance
```
Component              Time per Frame
───────────────────────────────────────
MediaPipe detection:   3.5 – 5.2 ms
ROI preprocessing:     0.8 – 1.2 ms
CNN inference:        12.0 – 18.0 ms
Majority vote:        < 0.1 ms
Display:              1.0 – 2.0 ms
───────────────────────────────────────
TOTAL:               ~18 – 27 ms
FPS:                 ~28 – 30 frames/sec
```

**Real-World Analogy:** 30 FPS means the system analyses your face 30 times every second. Smooth, real-time video.

---

## 13. Glossary — Plain English Definitions

| Term | Plain English |
|------|--------------|
| **Accuracy** | % of total predictions that are correct |
| **Activation Function** | A function that decides if a neuron "fires" (like on/off switch with some wiggle room) |
| **Adam Optimiser** | Smart algorithm that adjusts model weights efficiently |
| **Augmentation** | Artificially creating extra training images by rotating, flipping, zooming real images |
| **Backpropagation** | The process of calculating how to improve each weight after seeing a mistake |
| **Batch** | A small group of images processed together (we used 32) |
| **Batch Normalisation** | Keeps neuron activations in a healthy range during training |
| **Class Imbalance** | When some categories have far more training examples than others |
| **Confusion Matrix** | A grid showing which emotions get confused with which other emotions |
| **Conv2D** | A sliding window that scans an image looking for specific patterns |
| **Dataset** | A large collection of labelled examples used to train AI |
| **Deque** | A circular buffer (like a 10-slot memory that replaces old items with new ones) |
| **Dropout** | Randomly disabling neurons during training to prevent overfitting |
| **Early Stopping** | Automatically stopping training when improvement stalls |
| **Epoch** | One complete pass through all training data |
| **F1-Score** | Balanced measure combining precision and recall |
| **Feature Map** | The output of a convolutional layer — a map of where patterns were found |
| **Filter** | A small pattern-detector that slides across an image |
| **Focal Loss** | A loss function that focuses learning on hard, misclassified examples |
| **Generalisation** | How well a model performs on new data it hasn't seen before |
| **Global Average Pooling** | Compresses each feature map to a single number (its average) |
| **Gradient** | The direction and size of the adjustment needed to improve the model |
| **Grayscale** | Black and white image (one colour channel instead of three) |
| **Inference** | Using a trained model to make predictions (not training — just predicting) |
| **Label Smoothing** | Softening hard 100%/0% labels to 90%/1.4% to account for noise |
| **L2 Regularisation** | Penalty for having very large weight values (prevents overfitting) |
| **Learning Rate** | How big a step to take when adjusting weights |
| **Loss Function** | The scoring function that measures how wrong the model is |
| **MaxPooling** | Reduces image size by keeping only the maximum value in each patch |
| **Majority Vote** | Taking the most common prediction from a set of predictions |
| **MediaPipe** | Google's face detection library |
| **Neural Network** | A mathematical system of connected layers that learns from examples |
| **Normalisation** | Scaling values to a standard range (e.g., 0-255 → 0.0-1.0) |
| **Overfitting** | Model memorises training data but can't generalise to new data |
| **Precision** | Of all "X" predictions, how many were actually X |
| **Recall** | Of all actual X examples, how many did the model find |
| **ReLU** | Activation function: max(0, x) — negative values become 0, positive stay |
| **ROI** | Region of Interest — the cropped face rectangle |
| **Softmax** | Converts raw scores into probabilities that sum to 100% |
| **Temporal Window** | Watching multiple frames over time before deciding (our 10-frame buffer) |
| **Transfer Learning** | Starting with a model trained on one task, fine-tuning for another |
| **Underfitting** | Model is too simple to learn the patterns (opposite of overfitting) |
| **Validation Set** | Held-out data used during training to check progress (not the test set) |
| **Weight** | A number inside the neural network that gets adjusted during training |
| **WSL2** | Windows Subsystem for Linux — runs Linux inside Windows |

---

## 🎯 Summary — The Whole Story in 10 Lines

1. We want a computer to look at a face and guess the emotion in real time
2. We trained it on 28,709 photos from FER2013 (but some are mislabelled, and Disgust has 16.5× fewer than Happy)
3. To fix the imbalance, we invented a Focal Loss that makes the model study Disgust and Fear harder
4. The model has 4 layers of pattern detection: edges → shapes → features → emotions
5. We use MediaPipe (Google's tool) to find the face in each camera frame
6. The face is shrunk to 48×48 pixels, made grayscale, and fed to the neural network
7. The model outputs 7 probability scores; we pick the highest one
8. To avoid flickering, we watch the last 10 predictions and pick the most common
9. Final result: 63.51% accurate — just 1.5% below what humans can do on the same test
10. Everything runs at 28-30 FPS on a regular laptop, no special hardware needed

---

*Document generated for: Harol Maxilan (22CDS0439) | Capstone Project | SUSL Department of Data Science | September 2026*
