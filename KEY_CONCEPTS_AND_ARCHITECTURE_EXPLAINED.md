# 🧠 Master Reference Guide: Key Concepts, Neural Architecture, and Functions Explained in Simple English

> **Document Purpose:** This guide breaks down every technical concept, architectural layer, mathematical formula, and real-time mechanism used in this project into simple, intuitive English with everyday real-world analogies.  
> **Student:** Harol Maxilan | **Index:** 22CDS0439  
> **Project:** Real-Time Facial Emotion Recognition Using MediaPipe and Deep CNN with Focal Loss

---

## 📑 Table of Contents

1. [The Two Core Problems & Their Solutions](#1-the-two-core-problems--their-solutions)
   - [Problem A: What is Class Imbalance?](#problem-a-what-is-class-imbalance)
   - [Problem B: What is Prediction Flickering?](#problem-b-what-is-prediction-flickering)
   - [Solution: The 10-Frame Deque & Majority Voting](#solution-the-10-frame-deque--majority-voting)
2. [The Loss Function Stack: Our Secret Weapon](#2-the-loss-function-stack-our-secret-weapon)
   - [Categorical Cross-Entropy (Standard Approach)](#categorical-cross-entropy-standard-approach)
   - [Focal Loss ($\gamma = 2.0$) — Deep Dive](#focal-loss-gamma--20--deep-dive)
   - [Why $\gamma = 2.0$? The 81× Math Ratio Explained](#why-gamma--20-the-81-math-ratio-explained)
   - [Label Smoothing ($\epsilon = 0.1$)](#label-smoothing-epsilon--01)
   - [Dynamic Class Weighting (4.8× vs 0.55×)](#dynamic-class-weighting-48-vs-055)
3. [The 4-Stage Deep ConvNet Architecture](#3-the-4-stage-deep-convnet-architecture)
   - [What is a Convolution ($Conv2D$)?](#what-is-a-convolution-conv2d)
   - [What is Batch Normalisation ($BatchNorm$)?](#what-is-batch-normalisation-batchnorm)
   - [What is Max Pooling ($MaxPool$)?](#what-is-max-pooling-maxpool)
   - [What is Dropout ($Dropout$)?](#what-is-dropout-dropout)
   - [Why Progressive Dropout (25% → 30% → 35% → 40%)?](#why-progressive-dropout-25--30--35--40)
   - [Step-by-Step Breakdown of Blocks 1, 2, 3, and 4](#step-by-step-breakdown-of-blocks-1-2-3-and-4)
4. [The Classification Head](#4-the-classification-head)
   - [Global Average Pooling ($GlobalAvgPool$) vs Flatten](#global-average-pooling-globalavgpool-vs-flatten)
   - [Dense(256, ReLU)](#dense256-relu)
   - [Dense(7, Softmax) & Argmax](#dense7-softmax--argmax)
5. [The Optimisation Engine & Training Callbacks](#5-the-optimisation-engine--training-callbacks)
   - [Adam Optimiser ($learning\_rate = 0.001$)](#adam-optimiser-learning_rate--0001)
   - [ReduceLROnPlateau](#reducelronplateau)
   - [EarlyStopping](#earlystopping)
   - [L2 Regularisation ($\lambda = 10^{-4}$)](#l2-regularisation-lambda--10-4)
6. [The Real-Time Vision Pipeline](#6-the-real-time-vision-pipeline)
   - [MediaPipe BlazeFace vs OpenCV Haar Cascades](#mediapipe-blazeface-vs-opencv-haar-cascades)
   - [ROI Preprocessing Pipeline Step-by-Step](#roi-preprocessing-pipeline-step-by-step)
   - [FPS and Latency Breakdown](#fps-and-latency-breakdown)
7. [Evaluation Metrics Explained](#7-evaluation-metrics-explained)
   - [Precision vs Recall](#precision-vs-recall)
   - [F1-Score & Weighted F1](#f1-score--weighted-f1)
   - [Confusion Matrix & Why Fear is Hard](#confusion-matrix--why-fear-is-hard)
   - [The ~65% Human Baseline Ceiling](#the-65-human-baseline-ceiling)
8. [Quick-Reference Summary Table (For Defense/Viva)](#8-quick-reference-summary-table-for-defenseviva)

---

# 1. The Two Core Problems & Their Solutions

### Problem A: What is Class Imbalance?

**In Simple English:**  
Imagine preparing for an exam with 7 subjects. In your study guide, there are **7,215 practice questions** for Math (Happy), but only **436 practice questions** for History (Disgust). 

Naturally, you become great at Math, but whenever a History question appears, you fail because you barely practiced it.

In FER2013:
- **Happy:** 7,215 images (25.1% of the dataset)
- **Disgust:** 436 images (only 1.5% of the dataset)
- **Ratio:** 16.5 to 1!

**Why does this break normal AI?**  
Standard neural networks want to minimize total mistakes. If the AI simply guesses "Happy" or "Neutral" all the time, it is already right 45% of the time without even trying. The model becomes lazy and completely ignores rare emotions like Disgust.

---

### Problem B: What is Prediction Flickering?

**In Simple English:**  
When you look at a live webcam, the camera takes 30 separate photos every second. In one single second:
- In Frame 1, your face looks 82% Happy.
- In Frame 2, you blink or the room light shifts slightly; the model gets confused and predicts Neutral.
- In Frame 3, it predicts Happy again.
- In Frame 4, it predicts Sad.

The label on the screen rapidly switches: `Happy -> Neutral -> Happy -> Sad -> Happy`.  
This rapid, jittery jumping is called **prediction flickering**. It looks glitchy, unprofessional, and is frustrating for any real-world user.

---

### Solution: The 10-Frame Deque & Majority Voting

**In Simple English:**  
Instead of displaying whatever the model guessed on *just the current micro-second frame*, we introduce a **memory buffer** of the last 10 frames.

**Real-World Analogy — The Jury of 10 People:**  
Imagine 10 judges watching you for a third of a second:
- 8 judges vote: "Happy!"
- 1 judge votes: "Neutral"
- 1 judge votes: "Surprise"

Instead of listening to the 1 confused judge, the system takes a **majority vote**. Since 8 out of 10 say Happy, the screen stays smoothly on **Happy**.

```
Frame Memory (Deque of size 10):
[ Happy, Happy, Neutral, Happy, Happy, Happy, Surprise, Happy, Happy, Happy ]
                           ▲
                  8 out of 10 = Happy
            DISPLAY: "Happy (Confidence: 88%)"
```

**Technical Details:**
- Implemented using Python's `collections.deque(maxlen=10)`.
- At 30 FPS, 10 frames = **333 milliseconds** (one-third of a second).
- Human emotional expressions naturally last between **500 ms to 4 seconds**.
- Therefore, 333 ms provides **perfect smoothing** with **zero noticeable lag** to human eyes.

---

# 2. The Loss Function Stack: Our Secret Weapon

The loss function is the **grading system** that tells the neural network how wrong it was so it can adjust its weights.

---

### Categorical Cross-Entropy (Standard Approach)
Standard Cross-Entropy (CCE) penalizes errors linearly:
$$\text{Loss} = -\log(p_t)$$
Where $p_t$ is the probability the model assigned to the correct emotion.

**The Flaw:**  
If the model sees 7,215 Happy faces and gets them 90% right, the tiny remaining errors on those 7,200 faces add up and overwhelm the gradient updates. The 436 Disgust faces produce such a tiny total signal that the model never adjusts its weights to learn them.

---

### Focal Loss ($\gamma = 2.0$) — Deep Dive

**What it does:**  
Focal Loss adds a **modulating factor** $(1 - p_t)^\gamma$ to the loss:

$$\text{FL}(p_t) = -(1 - p_t)^\gamma \cdot \log(p_t)$$

**Real-World Analogy — The Smart Tutor:**  
A smart student does not spend 5 hours studying things they already know 95% of the time (Happy). They skip the easy questions and spend 95% of their time on the tough, tricky questions they keep getting wrong (Disgust & Fear).

Focal Loss does this mathematically:
- If an example is **easy** (e.g., $p_t = 0.90$, model is 90% sure it's Happy):
  $$(1 - 0.90)^2 = (0.10)^2 = \mathbf{0.01}$$
  The loss penalty is **slashed to 1%** of its normal size! The model says: *"I already know this, ignore it."*

- If an example is **hard or rare** (e.g., $p_t = 0.10$, model only gave 10% chance to Disgust):
  $$(1 - 0.10)^2 = (0.90)^2 = \mathbf{0.81}$$
  The loss penalty retains **81%** of its full force!

---

### Why $\gamma = 2.0$? The 81× Math Ratio Explained

Look at the ratio between a hard sample ($p_t = 0.1$) and an easy sample ($p_t = 0.9$):

$$\frac{0.81}{0.01} = \mathbf{81\times}$$

By setting $\gamma = 2.0$, **hard, misclassified samples are weighted 81 times more heavily than easy samples during training**. This 81× leverage forces the backpropagation algorithm to focus its learning capacity on the minority classes (Disgust, Fear, Surprise).

In our ablation study:
- Baseline with standard CCE: **57.34%** accuracy
- Baseline + Focal Loss ($\gamma = 2.0$): **61.47%** accuracy  
👉 **A massive +4.13% single-component jump!**

---

### Label Smoothing ($\epsilon = 0.1$)

**In Simple English:**  
Normally, in one-hot encoding, the ground truth label is 100% absolute:
$$\text{Happy} = [0, 0, 0, 1.0, 0, 0, 0]$$

**The Problem with FER2013:**  
Because FER2013 was collected automatically from Google Images, **some photos are mislabelled**. A person who was actually scared might be labelled "Surprise". If you force the neural network to be 100% confident on a wrongly labelled image, it destroys its learned weights trying to memorize an error.

**How Label Smoothing fixes this:**  
With $\epsilon = 0.1$, we shave off 10% of the certainty and distribute it equally among all 7 classes:
$$\tilde{y}_c = y_c \cdot (1 - \epsilon) + \frac{\epsilon}{K}$$
For $K = 7$ classes:
- The true class gets: $1.0 \times 0.9 + \frac{0.1}{7} = \mathbf{0.9143}$ (91.4%)
- Every other class gets: $0.0 \times 0.9 + \frac{0.1}{7} = \mathbf{0.0143}$ (1.4%)

**Real-World Analogy — The Humble Professor:**  
Instead of saying *"This is 100% definitely Happy, no debate allowed,"* the teacher says *"This is 91.4% likely to be Happy, but there is a 1.4% chance it could be another emotion."*  
This prevents the neural network from becoming dangerously overconfident on noisy training images.

---

### Dynamic Class Weighting (4.8× vs 0.55×)

In `train.py`, we also calculate Scikit-Learn's balanced class weights:
$$w_c = \frac{N_{\text{total}}}{K \cdot N_c}$$

- For **Disgust** ($N_c = 436$): weight $\approx \mathbf{4.82}$
- For **Happy** ($N_c = 7,215$): weight $\approx \mathbf{0.55}$

When combined with Focal Loss and Label Smoothing, this triple-layered defense completely eliminates the negative side-effects of class imbalance.

---

# 3. The 4-Stage Deep ConvNet Architecture

```
                    INPUT: (48, 48, 1) Grayscale Face
                                  │
┌─────────────────────────────────▼─────────────────────────────────┐
│ BLOCK 1: Conv2D(64)×2 ➔ BatchNorm ➔ MaxPool(2×2) ➔ Dropout(25%)   │ ➔ Out: 24×24×64
└─────────────────────────────────┬─────────────────────────────────┘
                                  │
┌─────────────────────────────────▼─────────────────────────────────┐
│ BLOCK 2: Conv2D(128)×2 ➔ BatchNorm ➔ MaxPool(2×2) ➔ Dropout(30%)  │ ➔ Out: 12×12×128
└─────────────────────────────────┬─────────────────────────────────┘
                                  │
┌─────────────────────────────────▼─────────────────────────────────┐
│ BLOCK 3: Conv2D(256)×2 ➔ BatchNorm ➔ MaxPool(2×2) ➔ Dropout(35%)  │ ➔ Out: 6×6×256
└─────────────────────────────────┬─────────────────────────────────┘
                                  │
┌─────────────────────────────────▼─────────────────────────────────┐
│ BLOCK 4: Conv2D(512)×2 ➔ BatchNorm ➔ MaxPool(2×2) ➔ Dropout(40%)  │ ➔ Out: 3×3×512
└─────────────────────────────────┬─────────────────────────────────┘
                                  │
┌─────────────────────────────────▼─────────────────────────────────┐
│ HEAD: GlobalAvgPool ➔ Dense(256) ➔ BatchNorm ➔ Dropout(50%)      │
│       ➔ Dense(7, Softmax)                                         │ ➔ Out: 7 Probabilities
└───────────────────────────────────────────────────────────────────┘
```

---

### What is a Convolution ($Conv2D$)?

**In Simple English:**  
A convolution is like sliding a tiny magnifying glass (a $3 \times 3$ grid of numbers called a **filter** or **kernel**) across the image.

**Real-World Analogy — Looking for Waldo:**  
You don't look at the entire puzzle at once. Your eyes scan small patches looking for red-and-white stripes.  
- Filter 1 checks: *"Is there a horizontal line here?"*
- Filter 2 checks: *"Is there a dark curved edge here?"*

When the filter finds a match, it outputs a high number. This creates a **Feature Map**.

---

### What is Batch Normalisation ($BatchNorm$)?

**In Simple English:**  
As data passes through layer after layer, the numbers can swing wildly — one layer might output numbers in the hundreds, the next layer in tiny decimals. This is called **internal covariate shift** and causes training to crash or slow down.

**Real-World Analogy — An Audio Sound Mixer:**  
Imagine 8 people singing into microphones. One person whispers, one person screams. The audio sound engineer adjusts all volume sliders so everyone's voice is balanced and clear.  
$BatchNorm$ re-centers and scales the layer activations so the numbers always stay in a healthy, stable range (mean $\approx 0$, variance $\approx 1$).

**Why it matters:**  
It allows us to train 8 deep convolutional layers without gradients exploding or vanishing.

---

### What is Max Pooling ($MaxPool$)?

**In Simple English:**  
$MaxPool2D(2 \times 2)$ looks at a $2 \times 2$ square of pixels (4 numbers) and **keeps only the largest number**, throwing away the other 3.

```
┌──────┬──────┐
│  12  │  85  │        MaxPool(2×2)
├──────┼──────┤      ───────────────►     [ 85 ]
│  30  │  44  │
└──────┴──────┘
```

**Real-World Analogy — Newspaper Headlines:**  
You don't need to read every single word in an article to know the main topic; you just read the bold headline. Max pooling keeps the strongest detected feature and cuts the image dimensions in half:
- Input: $48 \times 48 \rightarrow$ after MaxPool: $24 \times 24$
- After Block 2: $12 \times 12$
- After Block 3: $6 \times 6$
- After Block 4: $3 \times 3$

This reduces computation by 75% at each stage and gives the network **spatial translation invariance** (an eye is recognized as an eye whether it moves 2 pixels left or right).

---

### What is Dropout ($Dropout$)?

**In Simple English:**  
During training, Dropout randomly "turns off" or deletes a percentage of neurons on each training step.

**Real-World Analogy — Team Sports Practice:**  
Imagine a football team that depends entirely on one superstar player. If that player gets injured, the team falls apart.  
The coach decides: *"In today's practice, the star player sits on the bench. The rest of the team must learn to play together without relying on him."*

By randomly turning off 25% to 50% of the neurons:
- No single neuron can dominate or memorize the training faces.
- Every neuron is forced to learn useful, independent features.
- It is one of the most effective ways to **stop overfitting**.

---

### Why Progressive Dropout (25% → 30% → 35% → 40%)?

Notice how our Dropout rate increases as we go deeper:
- **Block 1:** Dropout(0.25)
- **Block 2:** Dropout(0.30)
- **Block 3:** Dropout(0.35)
- **Block 4:** Dropout(0.40)
- **Head:** Dropout(0.50)

**The Intuition:**  
Early layers (Block 1) extract basic edges and lines. There are only a few ways to detect a line, so you don't want to drop too many.  
Deep layers (Block 4 & Head) have 512 complex feature channels with millions of connections. They have immense capacity to memorize noise. Therefore, deeper layers require **stronger regularisation** (up to 50% dropout) to prevent overfitting.

---

### Step-by-Step Breakdown of Blocks 1, 2, 3, and 4

#### 🧱 Block 1: `Conv2D(64) × 2 -> BN -> MaxPool -> Dropout(0.25)`
- **What it learns:** Low-level primitive features: straight edges, diagonals, sharp corners, and contrast gradients.
- **Why double Conv2D?** Two stacked $3 \times 3$ convolutions have an effective receptive field of $5 \times 5$, but with fewer parameters and an extra non-linear ReLU activation in between, allowing richer feature representations.
- **Output tensor:** $24 \times 24 \times 64$

#### 🧱 Block 2: `Conv2D(128) × 2 -> BN -> MaxPool -> Dropout(0.30)`
- **What it learns:** Mid-level structural features: eye corners, curve of the nose bridge, lip outlines, chin boundaries.
- **Output tensor:** $12 \times 12 \times 128$

#### 🧱 Block 3: `Conv2D(256) × 2 -> BN -> MaxPool -> Dropout(0.35)`
- **What it learns:** Complex facial sub-components: furrowed eyebrows, raised brow arches, open/closed mouth shapes, squinted eyelids.
- **Output tensor:** $6 \times 6 \times 256$

#### 🧱 Block 4: `Conv2D(512) × 2 -> BN -> MaxPool -> Dropout(0.40)`
- **What it learns:** High-level emotional Action Units (AUs): combinations of wide-open eyes with dropped jaws (Surprise), upturned mouth corners with cheek crinkles (Happy Duchenne smile), or compressed brow with tightened lips (Anger).
- **Output tensor:** $3 \times 3 \times 512$

---

# 4. The Classification Head

Once Block 4 finishes, we have 512 feature maps of size $3 \times 3$. Now we must turn these spatial maps into an emotion prediction.

---

### Global Average Pooling ($GlobalAvgPool$) vs Flatten

This was one of the most critical design decisions in our upgraded model.

**Old Approach — Flatten:**  
Takes the $3 \times 3 \times 512$ tensor and unrolls it into a long line of $4,608$ numbers.  
Connecting $4,608$ inputs to a Dense(256) layer requires:
$$4,608 \times 256 = \mathbf{1,179,648\text{ weights!}}$$
More than 1.1 million parameters in one layer! This causes massive overfitting.

**Our Approach — Global Average Pooling (GAP):**  
Instead of unrolling, GAP takes each of the 512 feature maps ($3 \times 3$) and computes its **average**:
$$1 \text{ number per feature map} \times 512 \text{ maps} = \mathbf{512\text{ numbers total}}$$

Connecting 512 inputs to Dense(256) requires:
$$512 \times 256 = \mathbf{131,072\text{ weights}}$$

```
Flatten:            4,608 inputs  ➔  1,179,648 weights  (High Overfitting Risk)
GlobalAvgPool:        512 inputs  ➔    131,072 weights  (9× Reduction! Clean Generalisation)
```

**Real-World Analogy — Executive Summary:**  
Flatten is like forwarding a 50-page raw transcript to the CEO.  
GAP is like an executive assistant extracting a 1-page bulleted summary of key themes. The CEO gets all the essential insights without drowning in noise.

---

### Dense(256, ReLU)
A fully connected layer of 256 neurons that acts as the "Decision Council". It weighs and combines all 512 summarized facial features:
- *"If Feature 14 (cheek raise) is high AND Feature 89 (lip corner pull) is high $\rightarrow$ heavily favor Happy."*
- Followed by Batch Normalization and 50% Dropout.

---

### Dense(7, Softmax) & Argmax

The final layer has 7 neurons — exactly one for each emotion class:
$$\text{Output} = [z_0, z_1, z_2, z_3, z_4, z_5, z_6]$$

**The Softmax Function:**  
Converts raw logits $z_i$ into probabilities that strictly sum to 1.0 (100%):
$$P(\text{class } i) = \frac{e^{z_i}}{\sum_{j=1}^{7} e^{z_j}}$$

Example Softmax Output:
| Index | Class | Probability | Meaning |
|---|---|---|---|
| 0 | Angry | 0.02 | 2% chance |
| 1 | Disgust | 0.01 | 1% chance |
| 2 | Fear | 0.03 | 3% chance |
| 3 | **Happy** | **0.88** | **88% chance (Winner)** |
| 4 | Sad | 0.02 | 2% chance |
| 5 | Surprise | 0.03 | 3% chance |
| 6 | Neutral | 0.01 | 1% chance |

**Argmax:**  
`np.argmax(probabilities)` simply selects the index with the highest probability (Index 3 $\rightarrow$ "Happy").

---

# 5. The Optimisation Engine & Training Callbacks

### Adam Optimiser ($learning\_rate = 0.001$)

**In Simple English:**  
Adam stands for **Adaptive Moment Estimation**. It is the engine that decides *how much* to adjust each of the 6.4 million weights during backpropagation.

**Real-World Analogy — Driving a Car:**
- If you are on a long, straight empty highway $\rightarrow$ you accelerate smoothly (momentum).
- If you are approaching tight, bumpy curves $\rightarrow$ you slow down and make small, careful steering adjustments.

Adam calculates a separate, custom learning rate for every single parameter based on its historical gradients.

---

### ReduceLROnPlateau

```python
ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=4, min_lr=1e-7)
```

**What it does:**  
Monitors validation loss during training. If validation loss stops improving for **4 consecutive epochs**, it automatically cuts the learning rate in half (`factor = 0.5`).

**Real-World Analogy — Parallel Parking:**  
When parking a car:
- When you are far from the curb, you move fast with big steering turns ($lr = 0.001$).
- When you are 2 inches from the curb, big turns will crash the car. You switch to micro-adjustments ($lr = 0.0005 \rightarrow 0.00025 \rightarrow 0.000125$).

In our training:
- Triggered at **epoch 24, epoch 36, and epoch 44**, each time helping the model settle into a deeper, sharper loss minimum.

---

### EarlyStopping

```python
EarlyStopping(monitor='val_accuracy', patience=12, restore_best_weights=True)
```

**What it does:**  
Prevents the model from training for too long. If validation accuracy fails to hit a new all-time high for **12 consecutive epochs**, training immediately halts and restores the exact weights from the peak epoch.

**Why it matters:**  
Our maximum epochs was set to 60. EarlyStopping fired at **epoch 52**, saving the optimal weights from peak validation accuracy (63.7%) and stopping before overfitting could degrade generalisation.

---

### L2 Regularisation ($\lambda = 10^{-4}$)

Added to all Conv2D and Dense kernel weights via `kernel_regularizer=l2(1e-4)`.  
It penalizes large weight values:
$$\text{Total Loss} = \text{Focal Loss} + \lambda \sum w_i^2$$

**Why:**  
Prevents any single weight from becoming huge. Forces the network to distribute its decisions across many collaborative weights rather than relying on one brittle connection.

---

# 6. The Real-Time Vision Pipeline

```
Camera Frame (720p BGR)
       │
       ▼
cv2.cvtColor(BGR ➔ RGB)
       │
       ▼
MediaPipe BlazeFace  ➔  Face Bounding Box: [xmin, ymin, width, height]
       │
       ▼
Crop Face + 10px Margin  ➔  cv2.cvtColor(RGB ➔ Grayscale)
       │
       ▼
cv2.resize(48, 48)  ➔  divide by 255.0  ➔  reshape (1, 48, 48, 1)
       │
       ▼
CNN Model Predict  ➔  7 Softmax Probabilities
       │
       ▼
10-Frame Deque Buffer  ➔  Counter(deque).most_common(1)
       │
       ▼
cv2.rectangle + cv2.putText  ➔  Display on Screen (28-30 FPS)
```

---

### MediaPipe BlazeFace vs OpenCV Haar Cascades

| Feature | OpenCV Haar Cascade (Old 2001) | Google MediaPipe BlazeFace (Used Here) |
|---|---|---|
| **Underlying Tech** | AdaBoost + Hand-crafted rectangular features | Single-Shot Deep Convolutional Network |
| **Speed on CPU** | 10 – 15 ms | **3 – 5 ms** (Ultra-fast MobileNet backbone) |
| **Head Rotation** | Fails beyond $\pm 15^\circ$ head turn | **Handles up to $\pm 45^\circ$ yaw & tilt smoothly** |
| **Lighting Changes** | Frequent false detections in low light | Robust feature extraction across lighting |
| **Occlusion** | Loses tracking with glasses or hand near chin | Robustly tracks partially occluded faces |

---

### ROI Preprocessing Pipeline Step-by-Step

Every live camera crop must match the exact numerical distribution of the FER2013 training images:
1. **Grayscale conversion:** `cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)`  
   Removes colour biases (skin tone, room colour). FER2013 was trained on black-and-white images; colour is irrelevant to facial muscle Action Units.
2. **Bilinear Interpolation Resize:** `cv2.resize(gray_crop, (48, 48), interpolation=cv2.INTER_LINEAR)`  
   Shrinks the high-resolution face crop down to the exact $48 \times 48$ pixel grid expected by our input layer.
3. **Floating-point normalisation:** `gray_crop.astype('float32') / 255.0`  
   Converts integer pixel values $[0, 255]$ into floating-point numbers in the range $[0.0, 1.0]$.
4. **Tensor Expansion:** `np.reshape(normalised, (1, 48, 48, 1))`  
   Adds the batch dimension (1 image) and channel dimension (1 grayscale channel).

---

### FPS and Latency Breakdown

| Pipeline Stage | Time Taken |
|---|---|
| 1. Video capture & RGB conversion | ~1.0 ms |
| 2. MediaPipe BlazeFace detection | ~3.5 – 5.0 ms |
| 3. Crop, grayscale, resize, normalise | ~0.8 – 1.2 ms |
| 4. 4-Stage CNN inference (Intel CPU) | ~12.0 – 18.0 ms |
| 5. 10-frame majority vote | < 0.1 ms |
| 6. Overlay rendering & display | ~1.0 – 1.5 ms |
| **Total End-to-End Latency** | **~18.4 – 26.8 ms** |
| **Sustained Frame Rate** | **28 – 30 Frames Per Second (Real-Time)** |

---

# 7. Evaluation Metrics Explained

### Precision vs Recall

**Real-World Analogy — The Airport Metal Detector:**
- **Precision:** When the metal detector beeps, *how often is there actually a weapon?* (If it beeps 100 times, but 90 are just belt buckles, precision is low).
- **Recall:** Of *all the actual weapons* carried through, *how many did it catch?* (If 10 weapons passed through and it caught 9, recall is 90%).

In our emotion model:
- **Disgust Precision = 81.82%:** When the model says *"This is Disgust"*, it is right **81.8% of the time**! It rarely cries wolf.
- **Disgust Recall = 40.54%:** Out of all actual Disgust faces in the test set, it caught **40.5%**, missing the rest due to extreme training rarity.

---

### F1-Score & Weighted F1

**F1-Score** is the **harmonic mean** of Precision and Recall:
$$\text{F1} = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

Why not a simple average?  
If a model has 100% precision but 0% recall, a normal average gives 50% (misleading!).  
The harmonic mean punishes extremes: $2 \cdot \frac{1.0 \times 0.0}{1.0 + 0.0} = \mathbf{0\%}$.  
A high F1-score proves a model has **both strong precision AND strong recall**.

- **Weighted F1 (62.91%):** Weights each emotion's F1-score by how many test images belong to that class, giving an accurate picture of total real-world performance.

---

### Confusion Matrix & Why Fear is Hard

Looking at our test set confusion matrix:
- **Happy:** 1,528 out of 1,774 correct (**86.1% recall**). A smile uses the zygomaticus major muscle to pull the mouth corners outward and crinkle the eyes. No other emotion looks like this.
- **Fear:** Only 355 out of 1,024 correct (**34.7% recall**).
  - 234 Fear faces were confused with **Sad** (both have downturned mouth angles).
  - 192 Fear faces were confused with **Surprise** (both have widened eyes and raised inner eyebrows).

Fear is physiologically an "overlap emotion" that shares Action Units with both Surprise and Sadness, making it the most difficult class for any computer vision model.

---

### The ~65% Human Baseline Ceiling

When Goodfellow et al. evaluated human annotators on the FER2013 dataset in 2013, **human agreement was approximately 65%**.

**Why?**  
Because real human faces are ambiguous. If you show a picture of someone raising one eyebrow with a flat mouth to 10 humans:
- 4 will say Neutral
- 3 will say Surprise
- 2 will say Fear
- 1 will say Angry

There is no universal consensus on ambiguous photos.  
Therefore, our model achieving **63.51% test accuracy** is **within 1.49% of the human benchmark ceiling**, proving it has captured almost all learnable signal available in the dataset.

---

# 8. Quick-Reference Summary Table (For Defense/Viva)

| Technical Term | What It Is | Real-World Analogy | Value in Our Project |
|---|---|---|---|
| **Class Imbalance** | Disproportionate training samples per category | Practicing Math 7,200 times and History 436 times | 16.5× ratio between Happy (7,215) and Disgust (436) |
| **Prediction Flickering** | Rapid, distracting label jumping between frames | A flickering light switch or indecisive judge | Solved via 10-frame majority-vote deque (333 ms) |
| **Focal Loss** | Loss function downweighting easy samples | Student skipping easy questions to drill hard ones | $\gamma = 2.0$, producing up to 81× gradient boost on hard cases |
| **Label Smoothing** | Softening one-hot targets to prevent overconfidence | A humble teacher saying "91% sure, not 100%" | $\epsilon = 0.1$, true class target = 0.914, others = 0.014 |
| **$Conv2D(N)$** | Sliding $3 \times 3$ filter extracting visual patterns | Looking through a magnifying glass for edges/curves | $64 \rightarrow 128 \rightarrow 256 \rightarrow 512$ filters across 4 blocks |
| **$BatchNorm$** | Re-scaling activations to mean 0, variance 1 | Sound engineer balancing singer microphone levels | Stabilizes training across 8 deep convolution layers |
| **$MaxPool2D$** | Keeps the highest value in a $2 \times 2$ patch | Reading bold newspaper headlines instead of full text | Reduces spatial resolution by half ($48 \rightarrow 24 \rightarrow 12 \rightarrow 6 \rightarrow 3$) |
| **$Dropout(p)$** | Randomly disabling neurons during training | Practicing without the team superstar | Progressive: 25% $\rightarrow$ 30% $\rightarrow$ 35% $\rightarrow$ 40% $\rightarrow$ 50% |
| **$GlobalAvgPool$** | Averages each $3 \times 3$ feature map to 1 value | 1-page executive summary of a 50-page book | Slashes head weights from 1.18 Million to 131,072 (9× reduction) |
| **$Softmax$** | Normalises 7 raw logits into probabilities | 7 betting odds that must strictly sum to 100% | Outputs 7 confidence scores for emotion classes |
| **MediaPipe** | Google's lightweight CNN face detection pipeline | Dedicated face-spotter with wide peripheral vision | Detects face bounding box in 3–5 ms; handles $\pm 45^\circ$ head turn |
| **Adam** | Adaptive Moment Estimation optimiser | Smart driver accelerating on straights, slowing on curves | Initial learning rate = 0.001 with momentum decay |
| **ReduceLROnPlateau** | Cuts learning rate when validation loss stalls | Slowing car down to micro-adjustments when parking | Halves learning rate after 4 plateau epochs; fired 3 times |
| **EarlyStopping** | Halts training when validation accuracy peaks | Stopping study before you start memorizing verbatim | Stopped at epoch 52 (out of 60), restoring peak weights |
| **Test Accuracy** | Correct predictions divided by total test set | Final exam percentage score | **63.51%** (within 1.49% of ~65% human benchmark) |
| **Weighted F1** | F1-score averaged according to class sample counts | Course grade weighting final exam more than minor quiz | **62.91%** |
| **Throughput (FPS)** | Processed video frames per second | Video fluidity (standard film is 24 FPS) | **28 – 30 FPS** on consumer laptop CPU |

---
*Created for Harol Maxilan (22CDS0439) | Sabaragamuwa University of Sri Lanka | Capstone Defense Reference*
