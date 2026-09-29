"""
build_presentation.py  -  Capstone Presentation Builder
Student : Harol Maxilan | 22CDS0439
Supervisor: Mr. Dimuthu Lakshan | HOD: Dr. UAP Ishanka
Slides  : 14  (matching official template order)
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

NAVY  = RGBColor(0x1F, 0x39, 0x64)
GOLD  = RGBColor(0xC9, 0x9A, 0x06)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x00, 0x00, 0x00)
LGREY = RGBColor(0xF2, 0xF2, 0xF2)

SW = Inches(13.33)
SH = Inches(7.50)


# ─── helpers ──────────────────────────────────────────────────────────────────

def rect(slide, l, t, w, h, color):
    s = slide.shapes.add_shape(1, l, t, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = color
    s.line.fill.background()
    return s

def tb(slide, text, l, t, w, h, sz=16, bold=False, color=BLACK, align=PP_ALIGN.LEFT):
    b = slide.shapes.add_textbox(l, t, w, h)
    tf = b.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = text
    r.font.size = Pt(sz); r.font.bold = bold; r.font.color.rgb = color
    return b

def header_bar(slide, section, title):
    rect(slide, 0, 0, SW, Inches(1.30), NAVY)
    tb(slide, section,
       Inches(0.30), Inches(0.05), Inches(12.5), Inches(0.50),
       sz=12, bold=True, color=GOLD)
    tb(slide, title,
       Inches(0.30), Inches(0.55), Inches(12.5), Inches(0.65),
       sz=23, bold=True, color=WHITE)

def bullets(slide, items, l, t, w, h, sz=15):
    bx = slide.shapes.add_textbox(l, t, w, h)
    tf = bx.text_frame; tf.word_wrap = True
    first = True
    for item in items:
        if first:
            p = tf.paragraphs[0]; first = False
        else:
            p = tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        if item == "":
            r.text = ""
        elif item.startswith("   "):
            r.text = "      " + item.strip()
            r.font.size = Pt(sz - 2)
        else:
            r.text = item
            r.font.size = Pt(sz)
        r.font.color.rgb = BLACK
    return bx

def std_slide(prs, section, title, items, sz=15):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    header_bar(sl, section, title)
    bullets(sl, items, Inches(0.55), Inches(1.45), Inches(12.2), Inches(5.8), sz=sz)
    return sl

def two_col(prs, section, title, lh, li, rh, ri):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    header_bar(sl, section, title)
    tb(sl, lh, Inches(0.45), Inches(1.45), Inches(5.9), Inches(0.45),
       sz=14, bold=True, color=NAVY)
    bullets(sl, li, Inches(0.45), Inches(1.95), Inches(5.9), Inches(5.2), sz=13)
    rect(sl, Inches(6.58), Inches(1.40), Inches(0.05), Inches(5.80), LGREY)
    tb(sl, rh, Inches(6.80), Inches(1.45), Inches(6.10), Inches(0.45),
       sz=14, bold=True, color=NAVY)
    bullets(sl, ri, Inches(6.80), Inches(1.95), Inches(6.10), Inches(5.2), sz=13)
    return sl


# ─── build ────────────────────────────────────────────────────────────────────

def build():
    tpl = "Report/Final Presentation-Capstone Project in Data Science II.pptx"
    prs = Presentation(tpl) if os.path.exists(tpl) else Presentation()
    if os.path.exists(tpl):
        xml_sl = prs.slides._sldIdLst
        for s in list(xml_sl):
            xml_sl.remove(s)
    else:
        prs.slide_width = SW; prs.slide_height = SH

    LOGO = "Report/Screenshot 2026-08-29 095328.png"

    # ── Slide 1  TITLE ────────────────────────────────────────────────────────
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    rect(sl, 0, 0, SW, Inches(1.05), NAVY)
    tb(sl, "Capstone Project in Data Science II  -  DS4105",
       Inches(0.30), Inches(0.10), Inches(12.5), Inches(0.55),
       sz=13, bold=True, color=GOLD, align=PP_ALIGN.CENTER)

    tb(sl,
       "REAL-TIME FACIAL EMOTION RECOGNITION\nUSING MEDIAPIPE AND DEEP CNN WITH FOCAL LOSS",
       Inches(0.55), Inches(1.20), Inches(9.60), Inches(2.00),
       sz=23, bold=True, color=NAVY, align=PP_ALIGN.LEFT)

    if os.path.exists(LOGO):
        sl.shapes.add_picture(LOGO, Inches(10.85), Inches(1.15),
                              width=Inches(1.85), height=Inches(1.85))

    tb(sl, "Department of Data Science\nFaculty of Computing\nSabaragamuwa University of Sri Lanka",
       Inches(0.55), Inches(3.30), Inches(7.00), Inches(1.15), sz=14, color=NAVY)

    for i, (lbl, val) in enumerate([
        ("Index No    ", "22CDS0439"),
        ("Name        ", "Harol Maxilan"),
        ("Supervisor  ", "Mr. Dimuthu Lakshan"),
    ]):
        tb(sl, lbl + " :  " + val,
           Inches(0.55), Inches(4.60 + i * 0.48), Inches(9.0), Inches(0.44),
           sz=15, bold=True, color=BLACK)

    rect(sl, 0, Inches(6.75), SW, Inches(0.75), NAVY)
    tb(sl, "September 2026", Inches(0), Inches(6.80), SW, Inches(0.50),
       sz=13, color=WHITE, align=PP_ALIGN.CENTER)

    # ── Slide 2  CONTENTS ─────────────────────────────────────────────────────
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    header_bar(sl, "OVERVIEW", "Contents")
    left_items = [
        "1.   Introduction",
        "2.   Background",
        "3.   Specification and Design",
        "4.   Data Collection and Preprocessing",
        "5.   Feature Engineering and Selection",
        "6.   Model Selection, Training and Testing",
    ]
    right_items = [
        "7.   Model Deployment and Integration",
        "8.   Results and Conclusion",
        "9.   Future Works and Recommendations",
        "10.  References",
        "11.  Demonstration",
    ]
    bullets(sl, left_items,  Inches(0.80), Inches(1.55), Inches(5.80), Inches(5.50), sz=17)
    bullets(sl, right_items, Inches(7.20), Inches(1.55), Inches(5.80), Inches(5.50), sz=17)

    # ── Slide 3  INTRODUCTION ─────────────────────────────────────────────────
    std_slide(prs, "INTRODUCTION", "Introduction to the Problem",
        [
            "What is Facial Emotion Recognition (FER)?",
            "   A computer looks at a face and figures out how the person feels",
            "   Like a teacher who can tell if students are bored or confused",
            "",
            "The Problem We Are Solving:",
            "   People express 7 emotions: Angry, Disgust, Fear, Happy, Sad, Surprise, Neutral",
            "   Computers cannot feel -- but they can be trained to read faces",
            "   Existing systems struggle with rare emotions and flickering predictions",
            "",
            "Why Does This Matter?",
            "   E-learning: adapt lessons if student looks confused",
            "   Driver safety: alert driver if face shows fatigue or fear",
            "   Mental health tools: track emotional trends over time",
            "",
            "Scope of This Project:",
            "   Real-time webcam input  =>  7 emotion classes  =>  30 FPS output",
            "   Single laptop, no internet, no server needed",
        ])

    # ── Slide 4  BACKGROUND ───────────────────────────────────────────────────
    std_slide(prs, "BACKGROUND", "Background and Objectives",
        [
            "Dataset Used: FER2013 (Goodfellow et al., 2013) [1]",
            "   35,887 grayscale face images at 48 x 48 pixels",
            "   7 emotion categories collected from Google Images",
            "   Some images are mislabelled -- human accuracy ceiling is ~65%",
            "",
            "The Big Problem: Class Imbalance",
            "   Happy class = 7,215 training images",
            "   Disgust class = only 436 training images  (16.5x fewer!)",
            "   Standard training ignores Disgust -- model barely learns it",
            "",
            "Our Objectives:",
            "   O1: Design a 4-Stage Deep CNN trained on FER2013",
            "   O2: Apply Focal Loss + Label Smoothing to fix class imbalance",
            "   O3: Integrate MediaPipe for fast and reliable face detection",
            "   O4: Build a real-time system at 28-30 FPS on a regular laptop",
            "   O5: Achieve test accuracy close to the 65% human baseline",
        ])

    # ── Slide 5  SPECIFICATION AND DESIGN ────────────────────────────────────
    std_slide(prs, "SPECIFICATION & DESIGN", "Use Case Diagram and System Design",
        [
            "Use Case Diagram -- 6 Use Cases:",
            "   UC-1: Launch System",
            "   UC-2: Capture Video Frame (camera)",
            "   UC-3: Detect Face using MediaPipe",
            "   UC-4: Preprocess the Face Region (crop, resize, normalise)",
            "   UC-5: Classify Emotion using the CNN",
            "   UC-6: Smooth Prediction and Display on Screen",
            "",
            "System Architecture -- 5-Stage Pipeline:",
            "   Webcam  ->  Face Detection  ->  ROI Preprocessing  ->  CNN  ->  Display",
            "",
            "Key Requirements:",
            "   Accept 720p webcam input | Classify into 7 emotions",
            "   10-frame majority-vote buffer | Exit on Q key",
            "   Achieve 20+ FPS | 60%+ test accuracy",
        ])

    # ── Slide 6  DATA COLLECTION AND PREPROCESSING ───────────────────────────
    two_col(prs,
        "DATA COLLECTION & PREPROCESSING",
        "Data Collection and Preprocessing",
        "The FER2013 Dataset",
        [
            "35,887 total face images",
            "28,709 training images",
            "7,178 test images",
            "48 x 48 grayscale pixels",
            "7 emotion categories",
            "Source: automated Google Image search",
            "",
            "WARNING: Some images mislabelled",
            "Human agreement only ~65%",
            "Disgust: 436 vs Happy: 7,215",
        ],
        "Preprocessing Pipeline",
        [
            "Step 1: Load as grayscale",
            "Step 2: Divide by 255 -> [0.0 to 1.0]",
            "Step 3: Reshape to (48, 48, 1)",
            "Step 4: 85% train / 15% validation split",
            "Step 5: Shuffle training batches",
            "",
            "Augmentation (training only):",
            "Rotate +/-20 degrees",
            "Flip left-right",
            "Zoom +/-15%, Shift +/-15%",
            "Brightness change [0.8 to 1.2]",
            "Shear 0.15",
        ])

    # ── Slide 7  FEATURE ENGINEERING ─────────────────────────────────────────
    std_slide(prs, "FEATURE ENGINEERING & SELECTION",
        "How Features Are Extracted",
        [
            "We do NOT hand-craft features -- the CNN learns them automatically",
            "",
            "How Convolutional Filters Work:",
            "   A small 3x3 grid of numbers slides across the entire image",
            "   Each filter looks for a specific pattern (edge, curve, texture)",
            "   64 filters in Block 1 -- each finds a different pattern",
            "",
            "What Each Block Learns:",
            "   Block 1 (64 filters):  simple edges -- lines, corners",
            "   Block 2 (128 filters): simple shapes -- eye outline, nose shape",
            "   Block 3 (256 filters): face parts -- raised eyebrow, open mouth",
            "   Block 4 (512 filters): full emotion patterns (Fear vs Surprise)",
            "",
            "Why Grayscale?",
            "   Emotion comes from facial shape, not colour",
            "   Simpler model, faster training, same performance",
            "",
            "Global Average Pooling (instead of Flatten):",
            "   Compresses each 3x3 feature map into one number",
            "   9x fewer parameters -> much less risk of overfitting",
        ])

    # ── Slide 8  MODEL SELECTION TRAINING AND TESTING ────────────────────────
    two_col(prs,
        "MODEL SELECTION, TRAINING & TESTING",
        "Model Architecture and Training",
        "4-Stage Deep ConvNet (Custom CNN)",
        [
            "Input: 48x48 grayscale face image",
            "",
            "Block 1: Conv(64) x2 + MaxPool + Dropout 25%",
            "Block 2: Conv(128) x2 + MaxPool + Dropout 30%",
            "Block 3: Conv(256) x2 + MaxPool + Dropout 35%",
            "Block 4: Conv(512) x2 + MaxPool + Dropout 40%",
            "Head: GlobalAvgPool -> Dense(256) -> Dense(7)",
            "",
            "Total parameters: ~6.4 million",
            "BatchNorm after every Conv layer",
            "L2 regularisation on all weights",
        ],
        "Training Setup",
        [
            "Loss: Focal Loss (gamma=2.0)",
            "         + Label Smoothing (eps=0.1)",
            "Optimiser: Adam (lr = 0.001)",
            "Batch size: 32 images",
            "Max epochs: 60 (stopped at 52)",
            "",
            "Class Weighting:",
            "   Disgust weight = 4.8x",
            "   Happy weight = 0.55x",
            "",
            "Training time: ~3.5 hours",
            "GPU: NVIDIA RTX 2050 via WSL2",
            "",
            "EarlyStopping: patience 12 epochs",
            "ReduceLROnPlateau: patience 4 epochs",
        ])

    # ── Slide 9  MODEL DEPLOYMENT ─────────────────────────────────────────────
    std_slide(prs, "MODEL DEPLOYMENT & INTEGRATION",
        "Real-Time System and Technology Stack",
        [
            "Real-Time Pipeline (live_detect_pro.py):",
            "   Step 1: OpenCV reads 720p camera frame (30 FPS)",
            "   Step 2: Convert BGR colour -> RGB (for MediaPipe)",
            "   Step 3: MediaPipe BlazeFace detects face (takes 3-5 ms)",
            "   Step 4: Crop face -> grayscale -> resize to 48x48 -> divide by 255",
            "   Step 5: CNN predicts 7 probabilities (takes 12-18 ms)",
            "   Step 6: Add prediction to 10-frame memory -> majority vote",
            "   Step 7: Show emotion label on screen",
            "",
            "Technology Stack:",
            "   Language  : Python 3.10",
            "   ML        : TensorFlow 2.15  |  Keras 2.15",
            "   Vision    : MediaPipe 0.10.9  |  OpenCV 4.8.0",
            "   Numbers   : NumPy 1.26.4",
            "   Launcher  : run_webcam.bat  (one double-click on Windows)",
            "   Training  : WSL2 + NVIDIA RTX 2050 GPU",
            "   Versioning: Git + GitHub",
        ])

    # ── Slide 10  RESULTS AND CONCLUSION ─────────────────────────────────────
    two_col(prs,
        "RESULTS & CONCLUSION",
        "Results and Conclusion",
        "Classification Results  (7,178 test images)",
        [
            "Overall Test Accuracy :  63.51%",
            "Weighted F1-Score     :  62.91%",
            "Human Baseline (FER2013): ~65%",
            "Gap from human        :  only 1.49%",
            "",
            "Per-Class F1 Scores:",
            "   Happy    :  84.28%  (best)",
            "   Neutral  :  75.44%",
            "   Sad      :  61.08%",
            "   Angry    :  56.88%",
            "   Disgust  :  54.22%",
            "   Surprise :  49.17%",
            "   Fear     :  41.21%  (hardest)",
            "",
            "Real-Time: 28-30 FPS on regular laptop",
            "All 10 real-time test cases: PASSED",
        ],
        "Conclusions",
        [
            "We achieved near-human accuracy on FER2013",
            "",
            "What worked best:",
            "   Focal Loss fixed class imbalance (+4.13%)",
            "   4-Stage depth improved accuracy (+5.55%)",
            "   10-frame buffer removed flickering",
            "   MediaPipe gave fast stable detection",
            "",
            "Ablation Study Summary:",
            "   Baseline CCE:     57.34%",
            "   + Focal Loss:     61.47%",
            "   + Label Smooth:   58.73%",
            "   Full Proposed:    63.51%",
            "",
            "Key remaining gap:",
            "   Disgust recall still 40%",
            "   Fear confused with Surprise",
        ])

    # ── Slide 11  FUTURE WORKS ────────────────────────────────────────────────
    std_slide(prs, "FUTURE WORKS & RECOMMENDATIONS",
        "What Can Be Improved Next?",
        [
            "1. Face-Specific Transfer Learning",
            "   Use VGGFace2 or AffectNet pretrained model as starting point",
            "   These are trained on millions of real faces -- much better features",
            "   Expected improvement: +4 to 8% accuracy",
            "",
            "2. Vision Transformer (ViT) Architecture",
            "   Uses self-attention to connect eyebrows + mouth patterns together",
            "   Better at spotting emotion cues spread across the face",
            "",
            "3. Multimodal Emotion Recognition",
            "   Combine face + voice + body language",
            "   Much more reliable in real-world noisy conditions",
            "",
            "4. Fix Demographic Bias",
            "   Test on different ages, ethnicities, genders",
            "   Apply corrections where any group performs worse",
            "",
            "5. Continuous Emotion Modelling",
            "   Instead of 7 fixed labels, predict how happy/sad on a scale",
            "   More nuanced and useful for real applications",
        ])

    # ── Slide 12  REFERENCES ──────────────────────────────────────────────────
    refs = [
        "[1]  Goodfellow et al., Challenges in Representation Learning, ICONIP 2013.",
        "[2]  T.-Y. Lin et al., Focal Loss for Dense Object Detection, ICCV 2017.",
        "[3]  Lugaresi et al., MediaPipe: A Framework for Perception Pipelines, arXiv 2019.",
        "[4]  P. Viola and M. J. Jones, Robust Real-Time Face Detection, IJCV vol.57, 2004.",
        "[5]  K. Simonyan and A. Zisserman, Very Deep Convolutional Networks, ICLR 2015.",
        "[6]  M. Tan and Q. V. Le, EfficientNet: Rethinking Model Scaling, ICML 2019.",
        "[7]  S. Ioffe and C. Szegedy, Batch Normalization, ICML 2015.",
        "[8]  N. Srivastava et al., Dropout, JMLR vol.15, 2014.",
        "[9]  K. He et al., Deep Residual Learning for Image Recognition, CVPR 2016.",
        "[10] A. Dosovitskiy et al., An Image is Worth 16x16 Words, ICLR 2021.",
        "[11] R. W. Picard, Affective Computing. MIT Press, 1997.",
        "[12] P. Ekman and W. V. Friesen, Constants Across Cultures, J. Personality & Social Psych., 1971.",
    ]
    std_slide(prs, "REFERENCES", "References  (IEEE Format)", refs, sz=13)

    # ── Slide 13  DEMONSTRATION ───────────────────────────────────────────────
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    header_bar(sl, "DEMONSTRATION", "Live System Demo")
    tb(sl, "GitHub Repository:",
       Inches(0.55), Inches(1.60), Inches(12.0), Inches(0.50),
       sz=16, bold=True, color=NAVY)
    tb(sl, "https://github.com/Max-i26/emotion_detection",
       Inches(0.55), Inches(2.10), Inches(12.0), Inches(0.50),
       sz=15, color=BLACK)
    tb(sl, "To Run the Live Demo:",
       Inches(0.55), Inches(2.90), Inches(12.0), Inches(0.50),
       sz=16, bold=True, color=NAVY)
    steps = [
        "Step 1:  Open Windows PowerShell",
        "Step 2:  Type:   cd F:\\emotion-detection",
        "Step 3:  Type:   .\\venv_win\\Scripts\\activate",
        "Step 4:  Type:   python live_detect_pro.py",
        "Step 5:  Press  Q  to quit the camera window",
        "",
        "   OR simply double-click:   run_webcam.bat",
    ]
    bullets(sl, steps, Inches(0.55), Inches(3.50), Inches(12.0), Inches(3.50), sz=15)

    # ── Slide 14  THANK YOU ───────────────────────────────────────────────────
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    rect(sl, 0, 0, SW, SH, NAVY)
    tb(sl, "Thank You!", Inches(0), Inches(2.30), SW, Inches(1.40),
       sz=56, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tb(sl, "Questions & Answers",
       Inches(0), Inches(3.80), SW, Inches(0.80),
       sz=28, color=GOLD, align=PP_ALIGN.CENTER)
    tb(sl, "Harol Maxilan  |  22CDS0439  |  Dept. of Data Science, SUSL",
       Inches(0), Inches(5.10), SW, Inches(0.60),
       sz=14, color=WHITE, align=PP_ALIGN.CENTER)

    out = "Report/Capstone_Project_Presentation.pptx"
    prs.save(out)
    print("[OK] Saved:", out)


if __name__ == "__main__":
    build()
