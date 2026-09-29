"""
build_presentation.py  -  Capstone Presentation Builder (Clean Build)
Builds from a BLANK presentation to avoid PPTX corruption.
All styling applied manually to match the template colours.

Student : Harol Maxilan | 22CDS0439
Supervisor: Mr. Dimuthu Lakshan | HOD: Dr. UAP Ishanka
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree

# ── Colour palette ────────────────────────────────────────────────────────────
NAVY  = RGBColor(0x1F, 0x39, 0x64)   # dark blue (header / footer)
GOLD  = RGBColor(0xC9, 0x9A, 0x06)   # gold accent
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x10, 0x10, 0x10)
LGREY = RGBColor(0xD0, 0xD0, 0xD0)

SW = Inches(13.33)   # 16:9 wide slide
SH = Inches(7.50)


# ── Low-level helpers ─────────────────────────────────────────────────────────

def add_rect(slide, l, t, w, h, fill):
    """Filled rectangle with no border."""
    sp = slide.shapes.add_shape(1, l, t, w, h)
    sp.fill.solid()
    sp.fill.fore_color.rgb = fill
    sp.line.fill.background()
    return sp


def add_tb(slide, text, l, t, w, h,
           sz=15, bold=False, italic=False,
           color=BLACK, align=PP_ALIGN.LEFT, wrap=True):
    """Simple single-paragraph text box."""
    bx = slide.shapes.add_textbox(l, t, w, h)
    tf = bx.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(sz)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return bx


def add_multiline(slide, lines, l, t, w, h, sz=14, color=BLACK,
                  bold_lines=None, sub_prefix="   "):
    """
    Multi-paragraph text box.
    Lines starting with sub_prefix are rendered smaller and indented.
    bold_lines: set of line texts that should be bold.
    """
    bx = slide.shapes.add_textbox(l, t, w, h)
    tf = bx.text_frame
    tf.word_wrap = True
    bold_lines = bold_lines or set()

    first = True
    for raw in lines:
        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT

        is_sub = raw.startswith(sub_prefix)
        text = raw.lstrip()

        run = p.add_run()
        run.text = ("      " + text) if is_sub else text
        run.font.size = Pt(sz - 1.5 if is_sub else sz)
        run.font.color.rgb = color
        run.font.bold = (raw in bold_lines or (not is_sub and raw.endswith(":")))
    return bx


def header_bar(slide, section_label, slide_title):
    """Standard dark navy header bar with gold section label + white title."""
    add_rect(slide, 0, 0, SW, Inches(1.25), NAVY)
    add_tb(slide, section_label,
           Inches(0.35), Inches(0.05), Inches(12.5), Inches(0.48),
           sz=12, bold=True, color=GOLD, align=PP_ALIGN.LEFT)
    add_tb(slide, slide_title,
           Inches(0.35), Inches(0.52), Inches(12.5), Inches(0.65),
           sz=22, bold=True, color=WHITE, align=PP_ALIGN.LEFT)


def footer_bar(slide, text="Department of Data Science | Faculty of Computing | SUSL"):
    add_rect(slide, 0, Inches(7.10), SW, Inches(0.40), NAVY)
    add_tb(slide, text, Inches(0), Inches(7.12), SW, Inches(0.35),
           sz=9, color=WHITE, align=PP_ALIGN.CENTER)


def std_slide(prs, section, title, lines, sz=14):
    """One full-width bullet list slide."""
    sl = prs.slides.add_slide(prs.slide_layouts[6])  # blank layout
    header_bar(sl, section, title)
    add_multiline(sl, lines, Inches(0.50), Inches(1.35),
                  Inches(12.30), Inches(5.60), sz=sz)
    footer_bar(sl)
    return sl


def two_col_slide(prs, section, title, lh, left_lines, rh, right_lines):
    """Two-column slide with a vertical divider."""
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    header_bar(sl, section, title)
    # Left header
    add_tb(sl, lh, Inches(0.45), Inches(1.35), Inches(5.80), Inches(0.42),
           sz=13, bold=True, color=NAVY)
    add_multiline(sl, left_lines, Inches(0.45), Inches(1.82),
                  Inches(5.80), Inches(5.05), sz=13)
    # Divider
    add_rect(sl, Inches(6.53), Inches(1.32), Inches(0.06), Inches(5.80), LGREY)
    # Right header
    add_tb(sl, rh, Inches(6.75), Inches(1.35), Inches(6.20), Inches(0.42),
           sz=13, bold=True, color=NAVY)
    add_multiline(sl, right_lines, Inches(6.75), Inches(1.82),
                  Inches(6.20), Inches(5.05), sz=13)
    footer_bar(sl)
    return sl


# ═════════════════════════════════════════════════════════════════════════════
# MAIN BUILD
# ═════════════════════════════════════════════════════════════════════════════

def build():
    # Start from a BLANK presentation — no template loading to avoid corruption
    prs = Presentation()
    prs.slide_width  = SW
    prs.slide_height = SH

    LOGO = "Report/Screenshot 2026-08-29 095328.png"

    # ── SLIDE 1  TITLE PAGE ───────────────────────────────────────────────────
    sl = prs.slides.add_slide(prs.slide_layouts[6])

    # Top banner
    add_rect(sl, 0, 0, SW, Inches(1.00), NAVY)
    add_tb(sl, "Capstone Project in Data Science II  -  DS4105",
           Inches(0), Inches(0.12), SW, Inches(0.55),
           sz=14, bold=True, color=GOLD, align=PP_ALIGN.CENTER)

    # University logo (right side)
    if os.path.exists(LOGO):
        sl.shapes.add_picture(LOGO, Inches(10.95), Inches(1.10),
                              width=Inches(1.80), height=Inches(1.80))

    # Project title
    add_tb(sl,
           "REAL-TIME FACIAL EMOTION RECOGNITION\n"
           "USING MEDIAPIPE AND DEEP CNN WITH FOCAL LOSS",
           Inches(0.55), Inches(1.15), Inches(9.80), Inches(2.10),
           sz=24, bold=True, color=NAVY, align=PP_ALIGN.LEFT)

    # University info
    add_tb(sl,
           "Department of Data Science\n"
           "Faculty of Computing\n"
           "Sabaragamuwa University of Sri Lanka",
           Inches(0.55), Inches(3.40), Inches(7.50), Inches(1.20),
           sz=14, color=NAVY)

    # Student / supervisor details
    for i, (lbl, val) in enumerate([
        ("Index No",   "22CDS0439"),
        ("Name",       "Harol Maxilan"),
        ("Supervisor", "Mr. Dimuthu Lakshan"),
    ]):
        add_tb(sl, f"{lbl:<12} :  {val}",
               Inches(0.55), Inches(4.72 + i * 0.50), Inches(9.0), Inches(0.46),
               sz=15, bold=True, color=BLACK)

    # Bottom banner
    add_rect(sl, 0, Inches(6.80), SW, Inches(0.70), NAVY)
    add_tb(sl, "September 2026",
           Inches(0), Inches(6.85), SW, Inches(0.50),
           sz=14, color=WHITE, align=PP_ALIGN.CENTER)

    # ── SLIDE 2  TABLE OF CONTENTS ────────────────────────────────────────────
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
    add_multiline(sl, left_items,  Inches(1.00), Inches(1.50),
                  Inches(5.50), Inches(5.50), sz=17)
    add_multiline(sl, right_items, Inches(7.50), Inches(1.50),
                  Inches(5.50), Inches(5.50), sz=17)
    footer_bar(sl)

    # ── SLIDE 3  INTRODUCTION ─────────────────────────────────────────────────
    std_slide(prs, "INTRODUCTION", "Introduction to the Problem", [
        "What is Facial Emotion Recognition (FER)?",
        "   A computer looks at a face and figures out how the person feels",
        "   Like a teacher who knows if students are confused just by looking at them",
        "",
        "The Problem We Are Solving:",
        "   People show 7 emotions: Angry, Disgust, Fear, Happy, Sad, Surprise, Neutral",
        "   Computers cannot feel -- but they can be trained to read faces",
        "   Existing systems struggle with rare emotions and flickering predictions",
        "",
        "Why Does This Matter?",
        "   E-learning: adapt lessons if student looks confused or bored",
        "   Driver safety: alert driver when face shows fatigue or fear",
        "   Mental health tools: track emotional state over time",
        "",
        "Scope of This Project:",
        "   Real-time webcam input  =>  7 emotion labels  =>  30 FPS output",
        "   Single laptop, no internet, no special hardware needed",
    ])

    # ── SLIDE 4  BACKGROUND ───────────────────────────────────────────────────
    std_slide(prs, "BACKGROUND", "Background and Objectives", [
        "Dataset Used: FER2013  (Goodfellow et al., 2013) [1]",
        "   35,887 grayscale face images at 48 x 48 pixels",
        "   7 emotion categories -- images collected from Google Images",
        "   Some images are mislabelled  -->  human accuracy ceiling is about 65%",
        "",
        "The Big Problem -- Class Imbalance:",
        "   Happy class  = 7,215 training images",
        "   Disgust class = only 436 training images  (16.5 times fewer!)",
        "   Standard training ignores Disgust -- model barely learns it",
        "",
        "Project Objectives:",
        "   O1: Design a 4-Stage Deep CNN trained on FER2013",
        "   O2: Apply Focal Loss + Label Smoothing to fix class imbalance",
        "   O3: Integrate MediaPipe for fast and reliable face detection",
        "   O4: Build a real-time system running at 28-30 FPS on a regular laptop",
        "   O5: Achieve test accuracy close to the human baseline of ~65%",
    ])

    # ── SLIDE 5  SPECIFICATION AND DESIGN ────────────────────────────────────
    std_slide(prs, "SPECIFICATION & DESIGN", "Use Case Diagram and System Design", [
        "Use Case Diagram -- 6 Use Cases:",
        "   UC-1: Launch System (user runs the program)",
        "   UC-2: Capture Video Frame from webcam",
        "   UC-3: Detect Face using MediaPipe BlazeFace",
        "   UC-4: Preprocess the Face Region (crop, resize to 48x48, normalise)",
        "   UC-5: Classify Emotion using the 4-Stage CNN",
        "   UC-6: Smooth Prediction and Display emotion label on screen",
        "",
        "System Architecture -- 5-Stage Processing Pipeline:",
        "   Webcam  -->  Face Detection  -->  ROI Preprocessing  -->  CNN  -->  Display",
        "",
        "Key Functional Requirements:",
        "   FR-01: Accept 720p webcam at 30 FPS",
        "   FR-04: Classify into 7 emotions",
        "   FR-05: Apply 10-frame majority-vote for stable predictions",
        "   FR-07: Exit cleanly on Q key press",
        "",
        "Non-Functional: Min 20 FPS  |  Min 60% accuracy  |  Single-click startup",
    ], sz=13)

    # ── SLIDE 6  DATA COLLECTION AND PREPROCESSING ───────────────────────────
    two_col_slide(prs,
        "DATA COLLECTION & PREPROCESSING",
        "Data Collection and Preprocessing",
        "The FER2013 Dataset",
        [
            "Total images: 35,887",
            "Training images: 28,709",
            "Test images: 7,178",
            "Image size: 48 x 48 pixels",
            "Type: Grayscale (black & white)",
            "7 emotion categories",
            "Source: Automated Google Image search",
            "",
            "WARNING - Mislabelled images exist",
            "Human accuracy ceiling: ~65%",
            "Disgust (436) vs Happy (7,215) = 16.5x gap",
        ],
        "Preprocessing Pipeline",
        [
            "Step 1: Load images as grayscale",
            "Step 2: Divide pixels by 255 --> [0.0 to 1.0]",
            "Step 3: Reshape to (48, 48, 1) tensor",
            "Step 4: 85% training / 15% validation split",
            "Step 5: Shuffle training batches each epoch",
            "",
            "Data Augmentation (training only):",
            "   Rotate +/- 20 degrees",
            "   Flip left-right",
            "   Zoom +/- 15%",
            "   Shift +/- 15%",
            "   Brightness change 0.8 to 1.2",
            "   Shear 0.15",
        ])

    # ── SLIDE 7  FEATURE ENGINEERING ─────────────────────────────────────────
    std_slide(prs, "FEATURE ENGINEERING & SELECTION", "How Features Are Extracted", [
        "We do NOT hand-craft features -- the CNN learns them automatically",
        "",
        "How Convolutional Filters Work:",
        "   A 3x3 grid of numbers slides across the entire image",
        "   Each filter detects a specific pattern (edges, curves, textures)",
        "",
        "What Each Block Learns:",
        "   Block 1 (64 filters):   Simple edges -- straight lines and corners",
        "   Block 2 (128 filters):  Simple shapes -- eye outline, nose curve",
        "   Block 3 (256 filters):  Face parts -- raised eyebrows, open mouth",
        "   Block 4 (512 filters):  Full emotion patterns (Fear vs Surprise)",
        "",
        "Why Grayscale Images?",
        "   Emotion comes from facial shape, not colour",
        "   Simpler model, faster training, same accuracy",
        "",
        "Global Average Pooling (instead of Flatten):",
        "   Compresses 3x3 feature maps into 512 numbers",
        "   9 times fewer parameters --> much less risk of overfitting",
    ])

    # ── SLIDE 8  MODEL SELECTION, TRAINING AND TESTING ───────────────────────
    two_col_slide(prs,
        "MODEL SELECTION, TRAINING & TESTING",
        "Model Architecture and Training",
        "4-Stage Deep ConvNet  (Custom CNN)",
        [
            "Input: 48x48 grayscale face image",
            "",
            "Block 1: Conv2D(64) x2 + BatchNorm",
            "         MaxPool + Dropout 25%",
            "Block 2: Conv2D(128) x2 + BatchNorm",
            "         MaxPool + Dropout 30%",
            "Block 3: Conv2D(256) x2 + BatchNorm",
            "         MaxPool + Dropout 35%",
            "Block 4: Conv2D(512) x2 + BatchNorm",
            "         MaxPool + Dropout 40%",
            "Head:    GlobalAvgPool --> Dense(256)",
            "         Dropout 50% --> Dense(7, Softmax)",
            "",
            "Total parameters: ~6.4 million",
        ],
        "Training Configuration",
        [
            "Loss function:",
            "   Focal Loss (gamma = 2.0)",
            "   + Label Smoothing (epsilon = 0.1)",
            "",
            "Optimiser: Adam  (lr = 0.001)",
            "Batch size: 32 images",
            "Max epochs: 60  (stopped at epoch 52)",
            "",
            "Class Weighting:",
            "   Disgust weight = 4.8x",
            "   Happy weight = 0.55x",
            "",
            "Training time: ~3.5 hours",
            "GPU: NVIDIA RTX 2050 via WSL2",
            "EarlyStopping: patience = 12 epochs",
        ])

    # ── SLIDE 9  MODEL DEPLOYMENT AND INTEGRATION ─────────────────────────────
    std_slide(prs, "MODEL DEPLOYMENT & INTEGRATION",
              "Real-Time System and Technology Stack", [
        "Real-Time Pipeline -- each frame (30 per second):",
        "   Step 1: OpenCV reads 720p camera frame",
        "   Step 2: Convert colour BGR to RGB for MediaPipe",
        "   Step 3: MediaPipe BlazeFace detects face in 3-5 ms",
        "   Step 4: Crop face --> grayscale --> resize 48x48 --> divide by 255",
        "   Step 5: CNN predicts 7 probabilities in 12-18 ms",
        "   Step 6: Add to 10-frame memory --> majority vote --> stable label",
        "   Step 7: Show emotion label and score on screen",
        "",
        "Technology Stack:",
        "   Language      :  Python 3.10",
        "   ML Framework  :  TensorFlow 2.15  |  Keras 2.15",
        "   Vision        :  MediaPipe 0.10.9  |  OpenCV 4.8.0",
        "   Numerics      :  NumPy 1.26.4",
        "   Launcher      :  run_webcam.bat  (one double-click on Windows)",
        "   Training Env  :  WSL2 + NVIDIA RTX 2050 GPU",
        "   Versioning    :  Git + GitHub",
    ])

    # ── SLIDE 10  RESULTS AND CONCLUSION ─────────────────────────────────────
    two_col_slide(prs,
        "RESULTS & CONCLUSION",
        "Results and Conclusion",
        "Classification Results  (7,178 test images)",
        [
            "Overall Test Accuracy :  63.51%",
            "Weighted F1-Score     :  62.91%",
            "Human Baseline (FER2013) :  ~65%",
            "Gap from human baseline  :  only 1.49%",
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
            "All 10 live test cases: PASSED",
        ],
        "Conclusions",
        [
            "Achieved near-human accuracy on FER2013",
            "",
            "What worked best:",
            "   Focal Loss fixed imbalance (+4.13%)",
            "   4-Stage depth improved accuracy",
            "   10-frame buffer removed flickering",
            "   MediaPipe gave fast stable detection",
            "",
            "Ablation Study Summary:",
            "   Baseline (3-Block + CCE):     57.34%",
            "   + Focal Loss only:            61.47%",
            "   + Label Smoothing only:       58.73%",
            "   Full Proposed System:         63.51%",
            "   Each part adds improvement!",
            "",
            "Key remaining challenge:",
            "   Disgust recall still only 40%",
        ])

    # ── SLIDE 11  FUTURE WORKS ────────────────────────────────────────────────
    std_slide(prs, "FUTURE WORKS & RECOMMENDATIONS",
              "What Can Be Improved Next?", [
        "1. Face-Specific Transfer Learning:",
        "   Use VGGFace2 or AffectNet pretrained model as the starting point",
        "   Trained on millions of real faces -- gives much better features",
        "   Expected improvement: +4 to 8% accuracy",
        "",
        "2. Vision Transformer (ViT) Architecture:",
        "   Self-attention connects eyebrow movements with mouth patterns",
        "   Better at spotting emotion cues spread across the whole face",
        "",
        "3. Multimodal Emotion Recognition:",
        "   Combine face + voice + body language for higher reliability",
        "   Much more useful in noisy, real-world conditions",
        "",
        "4. Fix Demographic Bias:",
        "   Test on different ages, ethnicities, and genders",
        "   Apply corrections where any group performs worse",
        "",
        "5. Continuous Emotion Modelling:",
        "   Instead of 7 fixed labels, predict emotion on a sliding scale",
        "   More nuanced and useful for clinical and educational applications",
    ])

    # ── SLIDE 12  REFERENCES ──────────────────────────────────────────────────
    std_slide(prs, "REFERENCES", "References  (IEEE Format)", [
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
    ], sz=13)

    # ── SLIDE 13  DEMONSTRATION ───────────────────────────────────────────────
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    header_bar(sl, "DEMONSTRATION", "Live System Demo")
    add_tb(sl, "GitHub Repository:",
           Inches(0.55), Inches(1.45), Inches(12.0), Inches(0.48),
           sz=15, bold=True, color=NAVY)
    add_tb(sl, "https://github.com/Max-i26/emotion_detection",
           Inches(0.55), Inches(1.93), Inches(12.0), Inches(0.48),
           sz=14, color=BLACK)
    add_tb(sl, "To Run the Live Demo:",
           Inches(0.55), Inches(2.65), Inches(12.0), Inches(0.48),
           sz=15, bold=True, color=NAVY)
    add_multiline(sl, [
        "Step 1:  Open Windows PowerShell or Command Prompt",
        "Step 2:  Navigate to:   cd F:\\emotion-detection",
        "Step 3:  Activate:      .\\venv_win\\Scripts\\activate",
        "Step 4:  Run:           python live_detect_pro.py",
        "Step 5:  Press the  Q  key to close the camera window",
        "",
        "   OR  --  simply double-click:   run_webcam.bat",
    ], Inches(0.55), Inches(3.18), Inches(12.20), Inches(3.80), sz=15)
    footer_bar(sl)

    # ── SLIDE 14  THANK YOU ───────────────────────────────────────────────────
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    add_rect(sl, 0, 0, SW, SH, NAVY)   # full dark background
    add_tb(sl, "Thank You!",
           Inches(0), Inches(2.00), SW, Inches(1.60),
           sz=60, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_tb(sl, "Questions & Answers",
           Inches(0), Inches(3.80), SW, Inches(0.80),
           sz=28, color=GOLD, align=PP_ALIGN.CENTER)
    add_tb(sl, "Harol Maxilan  |  22CDS0439  |  Department of Data Science, SUSL",
           Inches(0), Inches(5.00), SW, Inches(0.60),
           sz=14, color=WHITE, align=PP_ALIGN.CENTER)

    # ── SAVE ──────────────────────────────────────────────────────────────────
    out = "Report/Capstone_Project_Presentation.pptx"
    prs.save(out)
    size_kb = os.path.getsize(out) // 1024
    print(f"[OK] Saved: {out}  ({size_kb} KB,  14 slides)")


if __name__ == "__main__":
    build()
