# 🎙️ Capstone Presentation & Live Demo Script
### Real-Time Facial Emotion Recognition Using MediaPipe and Deep CNN with Focal Loss
**Student:** Harol Maxilan | **Index:** 22CDS0439  
**Internal Supervisor:** Mr. Dimuthu Lakshan | **Head of Department:** Dr. UAP Ishanka  
**Institution:** Department of Data Science, Faculty of Computing, Sabaragamuwa University of Sri Lanka  
**Target Duration:** **10 – 12 Minutes Total** *(Presentation: ~8–9 min | Live Demo: ~2–3 min)*

---

## ⏱️ Time Allocation Overview

| Stage | Slides / Action | Target Time | Cumulative Time |
|---|---|---|---|
| **Part 1: Introduction & Background** | Slides 1 – 4 | ~2.5 mins | 2:30 |
| **Part 2: Design & Methodology** | Slides 5 – 8 | ~3.5 mins | 6:00 |
| **Part 3: Deployment, Results & Conclusion** | Slides 9 – 12 | ~2.5 mins | 8:30 |
| **Part 4: Live Webcam Demonstration** | Slide 13 + Running Demo | ~2.5 mins | 11:00 |
| **Part 5: Conclusion & Q&A** | Slide 14 | ~1 min | 12:00 |

---

## 🗣️ Slide-by-Slide Spoken Script

---

### 🟢 SLIDE 1 — TITLE SLIDE (0:00 – 0:40 | ~40 seconds)
> **[Action: Stand confidently, make eye contact with examiners, smile gently.]**

*"Good morning / Good afternoon respected panel members, supervisor Mr. Dimuthu Lakshan, and colleagues.*

*I am **Harol Maxilan**, Index Number **22CDS0439**, from the Department of Data Science, Faculty of Computing.*

*Today, I am proud to present my capstone project titled:  
**'Real-Time Facial Emotion Recognition Using MediaPipe and Deep Convolutional Neural Networks with Focal Loss.'**  

*This research addresses two critical real-world challenges in computer vision: handling severe dataset class imbalance, and eliminating high-frequency prediction flickering during live webcam deployment."*

---

### 🟢 SLIDE 2 — CONTENTS (0:40 – 1:00 | ~20 seconds)
> **[Action: Click next. Briefly guide the audience through the roadmap.]**

*"Here is an overview of my presentation today.*

*I will start with the problem background and project motivation, walk through our system design and data preprocessing pipeline, discuss how our 4-Stage CNN and Focal Loss were developed, review our evaluation results, and finally, I will conduct a **live real-time webcam demonstration** before concluding."*

---

### 🟢 SLIDE 3 — INTRODUCTION (1:00 – 1:45 | ~45 seconds)
> **[Action: Click next. Focus on the real-world importance.]**

*"To begin, what is Facial Emotion Recognition (FER)?  
It is the automated ability of an artificial intelligence system to look at human facial expressions and infer emotional states — categorised into seven fundamental classes: **Angry, Disgust, Fear, Happy, Sad, Surprise, and Neutral**.*

*While humans do this intuitively, teaching a computer to do so in real-time presents significant challenges:*
1. *First, facial expressions have subtle variations between different people.*
2. *Second, publicly available training datasets suffer from severe class imbalance — where rare emotions like Disgust have very few training samples compared to Happy.*
3. *Third, frame-by-frame predictions often flicker rapidly, creating an unstable user experience.*

*Overcoming these challenges is vital for impactful applications — including intelligent e-learning platforms that adapt when students look confused, driver safety monitoring systems detecting fatigue, and digital healthcare tools for mental health assessment.*

*The scope of this project is an end-to-end, standalone Windows application that processes 720p live webcam video at a smooth 30 frames per second on consumer hardware."*

---

### 🟢 SLIDE 4 — BACKGROUND & OBJECTIVES (1:45 – 2:35 | ~50 seconds)
> **[Action: Click next. Emphasize the 16.5× imbalance number.]**

*"The foundation of this research is the **FER2013 benchmark dataset** published by Goodfellow and colleagues.*

*FER2013 contains 35,887 grayscale images collected from Google search queries. Because of web search noise, even human annotator agreement on this dataset is only around **65%**, which serves as our practical benchmark ceiling.*

*More critically, there is a massive **16.5-to-1 class imbalance**. The dataset contains over 7,200 Happy images, but only **436 Disgust images** — which is just 1.5% of the data. Standard cross-entropy loss tends to ignore these minority classes.*

*To solve this, our project set five specific objectives:*
* *First: Build a deep 4-Stage CNN trained from scratch.*
* *Second: Implement Categorical Focal Loss combined with Label Smoothing to overcome the class imbalance.*
* *Third: Integrate Google MediaPipe BlazeFace for fast, robust face detection.*
* *Fourth: Achieve smooth real-time inference at 28 to 30 FPS on a standard laptop.*
* *And fifth: Reach classification accuracy competitive with the 65% human benchmark."*

---

### 🟢 SLIDE 5 — SPECIFICATION & DESIGN (2:35 – 3:20 | ~45 seconds)
> **[Action: Click next. Explain the 5-stage pipeline clearly.]**

*"Turning to system specification and architecture:*

*Our functional design consists of 6 primary use cases — launching the system, capturing video frames, face detection, region preprocessing, CNN emotion classification, and temporal smoothing.*

*Architecturally, the system operates as a **five-stage pipeline** shown here:*
1. ***Webcam Capture:** OpenCV streams BGR frames at 30 FPS.*
2. ***Face Detection:** MediaPipe BlazeFace extracts face bounding boxes in under 5 milliseconds.*
3. ***ROI Preprocessing:** The cropped face is converted to grayscale, resized to 48×48, and normalized.*
4. ***CNN Inference:** Our 4-Stage deep neural network outputs probability scores across all 7 emotions.*
5. ***Temporal Smoothing:** A 10-frame majority-vote buffer ensures the output on screen remains stable.*

*All of this runs locally with single-click startup, requiring zero GPU overhead during live inference."*

---

### 🟢 SLIDE 6 — DATA COLLECTION & PREPROCESSING (3:20 – 4:05 | ~45 seconds)
> **[Action: Click next. Explain the preprocessing steps.]**

*"For data preparation:*

*We split the 35,887 images into 28,709 training images and 7,178 official test images. The images were loaded in grayscale, normalized from 0–255 pixel integers to 0.0–1.0 floats, and reshaped into standard 48×48×1 tensors.*

*To combat overfitting and simulate real-world conditions, we implemented **on-the-fly data augmentation** exclusively during training.*

*This included random rotations of up to ±20 degrees, horizontal flips, random zoom and shift of ±15%, shear distortion, and brightness adjustments. This ensured our model learned expression geometry rather than memorizing static lighting or alignment."*

---

### 🟢 SLIDE 7 — FEATURE ENGINEERING & SELECTION (4:05 – 4:55 | ~50 seconds)
> **[Action: Click next. Explain how CNN features work simply.]**

*"A key strength of deep learning is that we do **not** rely on hand-crafted features like HOG or Haar filters. The convolutional layers learn facial feature representations hierarchically:*

* *In **Block 1**, 64 filters capture fundamental low-level features — edges, lines, and contrast boundaries.*
* *In **Block 2**, 128 filters combine those edges into local facial contours, such as eyelids and nose curves.*
* *In **Block 3**, 256 filters recognize distinct facial parts — raised eyebrows, furrowed brows, or open lips.*
* *In **Block 4**, 512 filters synthesize high-level emotion patterns — distinguishing subtle differences such as Fear versus Surprise.*

*Importantly, we replaced the traditional Flatten layer with **Global Average Pooling**. This reduced our head parameters by nearly **9 times**, drastically preventing overfitting while retaining spatial feature summaries."*

---

### 🟢 SLIDE 8 — MODEL SELECTION, TRAINING & TESTING (4:55 – 5:50 | ~55 seconds)
> **[Action: Click next. Explain Focal Loss clearly.]**

*"Slide 8 shows our complete neural network architecture and training configuration.*

*Our custom 4-Stage ConvNet contains **6.4 million parameters**, featuring double convolutions, Batch Normalization after every layer to stabilize gradient flow, and progressive Dropout rates scaling from 25% up to 50% in the dense classification head.*

*Our core algorithmic contribution is the training loss formulation:*
* *Instead of standard Cross-Entropy, we implemented **Categorical Focal Loss** with a focusing parameter gamma = 2.0.*
* *Focal Loss mathematically downweights easy, well-classified examples — like common Happy faces — by up to 81 times, forcing the gradient updates to focus intensely on hard, minority-class errors like Disgust and Fear.*
* *We paired this with **Label Smoothing (epsilon = 0.1)** to soften overconfident predictions against noisy dataset labels, and dynamic **class weighting**.*

*Training was executed on an NVIDIA RTX 2050 GPU via WSL2 for 52 epochs before EarlyStopping triggered, taking approximately 3.5 hours."*

---

### 🟢 SLIDE 9 — MODEL DEPLOYMENT & INTEGRATION (5:50 – 6:35 | ~45 seconds)
> **[Action: Click next. Highlight real-time efficiency.]**

*"Now looking at system deployment and integration:*

*In `live_detect_pro.py`, the entire inference loop takes only **18 to 27 milliseconds** per frame:*
* *MediaPipe face detection takes ~3 to 5 ms.*
* *Preprocessing takes ~1 ms.*
* *And CNN model inference takes ~12 to 18 ms on regular Intel CPU.*

*To prevent the flickering common in live FER systems, we implemented a **10-frame sliding deque window**.*
*At 30 FPS, 10 frames represent approximately **333 milliseconds** of video. The system takes a majority vote over this window.*
*If you blink or a single frame has a slight detection error, the displayed prediction remains completely stable without lag.*

*The application is fully containerized inside a local virtual environment and launches with a single click via `run_webcam.bat` on Windows 10 or 11."*

---

### 🟢 SLIDE 10 — RESULTS & CONCLUSION (6:35 – 7:35 | ~60 seconds)
> **[Action: Click next. Point to the metrics and the 1.49% gap.]**

*"Here are our quantitative experimental findings on the 7,178 unseen FER2013 test images:*

*Our proposed system achieved an **Overall Test Accuracy of 63.51%** and a **Weighted F1-Score of 62.91%**.*
*When compared to the human benchmark of approximately 65%, our model is **within just 1.49% of human-level performance**.*

*Looking at per-class performance:*
* *Happy achieved the highest F1-score at **84.28%**, followed by Neutral at **75.44%**.*
* *Fear remained the most challenging emotion at **41.21%**, primarily due to shared facial muscle activations with Surprise and Sadness.*

*Our **ablation study** clearly validates our design choices:*
* *A baseline 3-block CNN with standard cross-entropy scored 57.34%.*
* *Adding Focal Loss alone produced a massive jump of **+4.13%** to 61.47%.*
* *Adding our 4-Stage architecture and Label Smoothing delivered our final **63.51%** — a total improvement of **+6.17%** over the baseline.*

*All 10 structured real-time testing test cases passed with flying colours, sustaining 28 to 30 FPS on CPU."*

---

### 🟢 SLIDE 11 — FUTURE WORKS & RECOMMENDATIONS (7:35 – 8:15 | ~40 seconds)
> **[Action: Click next. Show research depth and future vision.]**

*"Based on our findings, we identified five promising directions for future expansion:*

1. ***Face-Specific Transfer Learning:** Pretraining on datasets like AffectNet or VGGFace2 could boost test accuracy by an estimated 4 to 8%.*
2. ***Vision Transformers (ViT):** Utilizing self-attention mechanisms to correlate distant facial features, such as eyebrow lifts and mouth openings simultaneously.*
3. ***Multimodal Emotion Recognition:** Fusing live facial analysis with speech prosody and audio cues.*
4. ***Demographic Fairness:** Evaluating across stratified age and ethnic groups to ensure zero demographic bias.*
5. ***Continuous Valence-Arousal Regression:** Moving beyond 7 discrete categories to a continuous spectrum of emotional intensity."*

---

### 🟢 SLIDE 12 — REFERENCES (8:15 – 8:30 | ~15 seconds)
> **[Action: Click next. Quick polite acknowledgment.]**

*"Here are the primary IEEE-standard academic references supporting this work, including Goodfellow et al. for FER2013, Lin et al. for Focal Loss, and Lugaresi et al. for Google MediaPipe."*

---

### 🟢 SLIDE 13 — DEMONSTRATION TRANSITION (8:30 – 8:50 | ~20 seconds)
> **[Action: Click next. Transition smoothly to the live demonstration.]**

*"All project source code, model weights, and evaluation pipelines are version-controlled and publicly accessible on GitHub.*

*Now, with the panel's permission, I would like to transition to the **Live Webcam Demonstration** to demonstrate the system operating in real-time."*

---

## 💻 LIVE WEBCAM DEMONSTRATION SCRIPT (8:50 – 11:15 | ~2.5 minutes)

> **Preparation Before Presentation:**
> - Ensure webcam is connected and clean.
> - Have PowerShell open in `F:\emotion-detection` OR have `run_webcam.bat` ready on your desktop/taskbar.
> - Good lighting on your face.

---

### 🎬 Demo Action 1: Launching the System (~20 seconds)
> **[Action: Double-click `run_webcam.bat` or run `.\run_webcam.bat` in PowerShell]**

**What to Say:**
*"I am now launching the live application using our single-click batch script `run_webcam.bat`.*

*The script activates our dedicated Windows virtual environment, initializes TensorFlow, loads our pre-trained 4-Stage CNN weights, and attaches to the webcam stream via MediaPipe BlazeFace.*

*[Wait 2–3 seconds until the camera window pops up]*

*As you can see, the video window has opened instantly at 720p resolution."*

---

### 🎬 Demo Action 2: Neutral Face (~25 seconds)
> **[Action: Look naturally at the camera with a relaxed, resting expression]**

**What to Say:**
*"Notice the green bounding box accurately tracking my face.*

*With a resting facial expression, the system predicts **'Neutral'** with approximately 70 to 85% confidence.*

*Notice the top-left overlay: the system is processing frames at a smooth **28 to 30 frames per second**, running entirely on my laptop CPU without any dedicated GPU acceleration."*

---

### 🎬 Demo Action 3: Happy Expression (~25 seconds)
> **[Action: Smile warmly with visible cheek raise and mouth curve]**

**What to Say:**
*"Now, as I smile...  
The system instantly shifts to **'Happy'** with over 90% confidence.*

*Notice how stable the prediction is: even as I slightly turn my head left and right by about 30 degrees, MediaPipe maintains lock on the face bounding box, and the 10-frame majority-vote buffer ensures there is zero flickering between frames."*

---

### 🎬 Demo Action 4: Surprise & Fear Expressions (~30 seconds)
> **[Action: Open mouth and raise eyebrows wide for Surprise, then tense expression for Fear/Angry]**

**What to Say:**
*"Now, let me express **Surprise** — raising my eyebrows and opening my mouth...  
The label immediately reflects **'Surprise'**.*

*Next, furrowing the brow for **'Angry'**...  
The system detects the tension in the eyebrow region and shifts accordingly.*

*This demonstrates that the hierarchical convolutional filters we discussed earlier are successfully recognizing real-world facial Action Units in real time."*

---

### 🎬 Demo Action 5: Head Movement, Stability & Clean Exit (~20 seconds)
> **[Action: Nod, tilt head slightly, then press 'Q' on the keyboard to exit]**

**What to Say:**
*"Finally, observing temporal stability: even during natural talking and minor head movements, the 333-millisecond majority-vote window filters out transient frame noise.*

*Now I will press the **'Q'** key...  
The camera stream releases immediately, memory is deallocated cleanly, and the process terminates gracefully."*

---

## 🟢 SLIDE 14 — CONCLUSION & Q&A (11:15 – 12:00 | ~45 seconds)
> **[Action: Switch back to PowerPoint Slide 14: 'Thank You!']**

*"In summary, this capstone project successfully implemented a complete end-to-end real-time Facial Emotion Recognition system.*

*By combining an upgraded 4-Stage CNN with Categorical Focal Loss and MediaPipe BlazeFace, we overcame the 16.5-to-1 dataset imbalance and achieved **63.51% test accuracy** — within 1.5% of human benchmark performance — while sustaining **30 FPS** on consumer hardware.*

*Thank you very much for your time and kind attention.*

*I am now ready and welcome any questions from the respected panel."*

---

## 🛡️ Quick Defense Cheat Sheet (Anticipated Panel Questions)

| Question from Examiner | Exact 10-Second Answer to Give |
|---|---|
| **"Why did you choose Focal Loss instead of oversampling or SMOTE?"** | *"SMOTE generates interpolated pixel values that don't represent anatomically valid faces. Focal Loss dynamically downweights easy samples by up to 81× during gradient backprop, forcing the model to learn rare classes directly from real images."* |
| **"Why 63.5%? Isn't that low compared to ImageNet models?"** | *"On FER2013, human annotator agreement is only ~65% due to web search label noise. So 63.51% is actually within 1.49% of the human ceiling, achieved on raw 48×48 grayscale images from scratch without pretraining."* |
| **"Why MediaPipe instead of OpenCV Haar Cascade?"** | *"Haar Cascade fails when heads tilt beyond 15 degrees and gives many false positives. MediaPipe BlazeFace uses a lightweight CNN that handles ±45° yaw, occlusions, and variable lighting while taking only 3–5 ms on CPU."* |
| **"What does the 10-frame buffer do to latency?"** | *"At 30 FPS, 10 frames equal 333 milliseconds — about one-third of a second. Human expressions last at least 500 ms, so 333 ms provides perfect smoothing without any noticeable display lag."* |
| **"Why is Fear accuracy lower than Happy?"** | *"Fear shares facial Action Units with both Surprise (raised eyebrows) and Sadness (mouth shape). Happy has a unique bilateral zygomaticus muscle contraction that is much easier for convolutional filters to isolate."* |

---
*Script generated for Harol Maxilan (22CDS0439) | Sabaragamuwa University of Sri Lanka | September 2026*
