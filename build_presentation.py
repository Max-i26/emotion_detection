"""
build_presentation.py  -  Fill Official Template In-Place
Loads the original 14-slide template and replaces ONLY the text content
of each existing shape. Backgrounds, colours, fonts, and layout are
ALL preserved from the master template.

Student : Harol Maxilan | 22CDS0439
Supervisor: Mr. Dimuthu Lakshan | HOD: Dr. UAP Ishanka
"""
import os, copy
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from lxml import etree

TPL  = "Report/Final Presentation-Capstone Project in Data Science II.pptx"
OUT  = "Report/Capstone_Project_Presentation.pptx"
LOGO = "Report/Screenshot 2026-08-29 095328.png"


# ── helpers ───────────────────────────────────────────────────────────────────

def clear_tf(shape):
    """Remove all paragraphs from a text frame, leaving one empty one."""
    tf = shape.text_frame
    # keep only the first paragraph, delete the rest
    txBody = tf._txBody
    for p in txBody.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}p')[1:]:
        txBody.remove(p)
    # clear the first paragraph's runs
    ns = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    first_p = txBody.find(f'{{{ns}}}p')
    for r in first_p.findall(f'{{{ns}}}r'):
        first_p.remove(r)


def set_para(shape, lines, sz=16, bold=False, color=None):
    """
    Replace the text frame content with the provided list of strings.
    Each string = one paragraph. Lines starting with '   ' are sub-bullets.
    """
    tf = shape.text_frame
    tf.word_wrap = True
    txBody = tf._txBody
    ns = 'http://schemas.openxmlformats.org/drawingml/2006/main'

    # Clone the first paragraph element as a template for new paras
    existing_paras = txBody.findall(f'{{{ns}}}p')
    # Use first para as template; remove all
    for p_el in existing_paras:
        txBody.remove(p_el)

    for i, line in enumerate(lines):
        is_sub = line.startswith('   ')
        text = line.strip()

        # Build <a:p> element
        p_el = etree.SubElement(txBody, f'{{{ns}}}p')

        # paragraph properties
        pPr = etree.SubElement(p_el, f'{{{ns}}}pPr')
        if is_sub:
            pPr.set('lvl', '1')
            pPr.set('indent', '-228600')
            pPr.set('marL', '685800')

        if not text:
            # empty line = spacer
            etree.SubElement(p_el, f'{{{ns}}}endParaRPr', {'lang': 'en-US'})
            continue

        # run
        r_el = etree.SubElement(p_el, f'{{{ns}}}r')

        # run properties
        rPr = etree.SubElement(r_el, f'{{{ns}}}rPr', {'lang': 'en-US', 'dirty': '0'})
        font_sz = (sz - 2) if is_sub else sz
        rPr.set('sz', str(int(font_sz * 100)))
        if bold or (not is_sub and text.endswith(':') and not text.startswith('[') and not text.startswith('Step')):
            rPr.set('b', '1')

        if color:
            solidFill = etree.SubElement(rPr, f'{{{ns}}}solidFill')
            srgbClr = etree.SubElement(solidFill, f'{{{ns}}}srgbClr')
            srgbClr.set('val', f'{color.red:02X}{color.green:02X}{color.blue:02X}')

        # text
        t_el = etree.SubElement(r_el, f'{{{ns}}}t')
        t_el.text = text


def set_title(shape, text, sz=28, bold=True, color=None):
    """Replace a title placeholder text."""
    tf = shape.text_frame
    txBody = tf._txBody
    ns = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    existing = txBody.findall(f'{{{ns}}}p')
    for p_el in existing:
        txBody.remove(p_el)

    p_el = etree.SubElement(txBody, f'{{{ns}}}p')
    pPr = etree.SubElement(p_el, f'{{{ns}}}pPr')
    r_el = etree.SubElement(p_el, f'{{{ns}}}r')
    rPr = etree.SubElement(r_el, f'{{{ns}}}rPr', {'lang': 'en-US', 'dirty': '0'})
    rPr.set('sz', str(int(sz * 100)))
    if bold:
        rPr.set('b', '1')
    if color:
        solidFill = etree.SubElement(rPr, f'{{{ns}}}solidFill')
        srgbClr = etree.SubElement(solidFill, f'{{{ns}}}srgbClr')
        srgbClr.set('val', f'{color.red:02X}{color.green:02X}{color.blue:02X}')
    t_el = etree.SubElement(r_el, f'{{{ns}}}t')
    t_el.text = text


def get_shape_by_name(slide, name):
    for sh in slide.shapes:
        if sh.name == name:
            return sh
    return None


def get_content_box(slide):
    """Return the main content text box (Rectangle 3 or similar)."""
    for sh in slide.shapes:
        if sh.has_text_frame and 'Rectangle' in sh.name:
            return sh
        if sh.has_text_frame and 'Shape' in sh.name:
            return sh
    return None


def get_title_ph(slide):
    """Return the title placeholder."""
    for sh in slide.shapes:
        if sh.has_text_frame and ('Title' in sh.name or 'INTRODUCTION' in sh.text_frame.text or
                                   sh.shape_type == 14):
            if 'Slide Number' not in sh.name and 'TextBox' not in sh.name and 'Rectangle' not in sh.name:
                return sh
    return None


# ── CONTENT DATA ──────────────────────────────────────────────────────────────

SLIDE_CONTENT = {}

# Slide 1 - Title (special handling below)

# Slide 2 - Contents
SLIDE_CONTENT[2] = {
    'content': [
        "1.   Introduction",
        "2.   Background",
        "3.   Specification and Design",
        "4.   Data Collection and Preprocessing",
        "5.   Feature Engineering and Selection",
        "6.   Model Selection, Training and Testing",
        "7.   Model Deployment and Integration",
        "8.   Results and Conclusion",
        "9.   Future Works and Recommendations",
        "10.  References",
        "11.  Demonstration",
    ],
    'sz': 18,
}

# Slide 3 - Introduction
SLIDE_CONTENT[3] = {
    'content': [
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
        "   Mental health tools: monitor emotional trends over time",
        "",
        "Scope: Real-time webcam input  =>  7 emotion labels  =>  30 FPS output",
        "   Single laptop, no internet, no special hardware needed",
    ],
    'sz': 16,
}

# Slide 4 - Background
SLIDE_CONTENT[4] = {
    'content': [
        "Dataset Used: FER2013  (Goodfellow et al., 2013) [1]",
        "   35,887 grayscale face images at 48 x 48 pixels",
        "   7 emotion categories collected from Google Images",
        "   Some images are mislabelled  -->  human accuracy ceiling is about 65%",
        "",
        "The Big Problem -- Class Imbalance:",
        "   Happy class   = 7,215 training images",
        "   Disgust class = only 436 training images  (16.5 times fewer!)",
        "   Standard training ignores Disgust -- model barely learns it",
        "",
        "Project Objectives:",
        "   O1: Design a 4-Stage Deep CNN trained on FER2013",
        "   O2: Apply Focal Loss + Label Smoothing to fix class imbalance",
        "   O3: Integrate MediaPipe for fast and reliable face detection",
        "   O4: Build a real-time system at 28-30 FPS on a regular laptop",
        "   O5: Achieve test accuracy close to the human baseline of ~65%",
    ],
    'sz': 16,
}

# Slide 5 - Specification and Design
SLIDE_CONTENT[5] = {
    'content': [
        "Use Case Diagram -- 6 Use Cases:",
        "   UC-1: Launch System",
        "   UC-2: Capture Video Frame from webcam",
        "   UC-3: Detect Face using MediaPipe BlazeFace",
        "   UC-4: Preprocess the Face Region (crop, resize 48x48, normalise)",
        "   UC-5: Classify Emotion using the 4-Stage CNN",
        "   UC-6: Smooth Prediction and Display emotion label on screen",
        "",
        "System Architecture -- 5-Stage Pipeline:",
        "   Webcam  -->  Face Detection  -->  ROI Preprocessing  -->  CNN  -->  Display",
        "",
        "Key Requirements:",
        "   FR: Accept 720p webcam | Classify 7 emotions | 10-frame majority vote",
        "   NFR: Min 20 FPS | Min 60% accuracy | Single-click startup on Windows",
    ],
    'sz': 16,
}

# Slide 6 - Data Collection and Preprocessing
SLIDE_CONTENT[6] = {
    'content': [
        "FER2013 Dataset:",
        "   35,887 total face images (28,709 train | 7,178 test)",
        "   48 x 48 pixels | Grayscale | 7 emotion categories",
        "   Source: automated Google Image search (automated labelling)",
        "   WARNING: Some images mislabelled -- human ceiling ~65%",
        "   Disgust (436 images) vs Happy (7,215 images) = 16.5x gap!",
        "",
        "Preprocessing Pipeline:",
        "   Step 1: Load images as grayscale (color_mode='grayscale')",
        "   Step 2: Divide pixels by 255 to get values [0.0 to 1.0]",
        "   Step 3: Reshape to (48, 48, 1) tensor format",
        "   Step 4: 85% training / 15% validation split (stratified)",
        "   Step 5: Shuffle training batches each epoch",
        "",
        "Data Augmentation (applied only during training):",
        "   Rotate +/- 20 degrees | Flip left-right | Zoom +/- 15%",
        "   Shift +/- 15% | Brightness 0.8 to 1.2 | Shear 0.15",
    ],
    'sz': 15,
}

# Slide 7 - Feature Engineering
SLIDE_CONTENT[7] = {
    'content': [
        "We do NOT hand-craft features -- the CNN learns them automatically",
        "",
        "How Convolutional Filters Work:",
        "   A 3x3 grid of numbers slides across the entire image",
        "   Each filter detects a specific pattern (edges, curves, textures)",
        "",
        "What Each Block Learns:",
        "   Block 1 (64 filters):    Simple edges -- lines and corners",
        "   Block 2 (128 filters):   Simple shapes -- eye outline, nose curve",
        "   Block 3 (256 filters):   Face parts -- raised eyebrow, open mouth",
        "   Block 4 (512 filters):   Full emotion patterns (Fear vs Surprise)",
        "",
        "Global Average Pooling (instead of Flatten):",
        "   Compresses 3x3 feature maps into 512 numbers",
        "   9 times fewer parameters -- much less risk of overfitting",
        "",
        "Why Grayscale? Emotion comes from facial shape, not colour",
    ],
    'sz': 16,
}

# Slide 8 - Model Selection, Training and Testing
SLIDE_CONTENT[8] = {
    'content': [
        "Model -- Custom 4-Stage Deep ConvNet:",
        "   Input: 48x48 grayscale face image",
        "   Block 1: Conv2D(64) x2 + BatchNorm + MaxPool + Dropout 25%",
        "   Block 2: Conv2D(128) x2 + BatchNorm + MaxPool + Dropout 30%",
        "   Block 3: Conv2D(256) x2 + BatchNorm + MaxPool + Dropout 35%",
        "   Block 4: Conv2D(512) x2 + BatchNorm + MaxPool + Dropout 40%",
        "   Head:    GlobalAvgPool --> Dense(256) --> Dropout(50%) --> Dense(7)",
        "   Total: ~6.4 million parameters",
        "",
        "Training Configuration:",
        "   Loss: Focal Loss (gamma=2.0) + Label Smoothing (epsilon=0.1)",
        "   Optimiser: Adam (lr=0.001) | Batch: 32 | Max epochs: 60",
        "   Class weighting: Disgust=4.8x | Happy=0.55x",
        "   EarlyStopping (patience=12) -- stopped at epoch 52",
        "   GPU: NVIDIA RTX 2050 via WSL2 | Training time: ~3.5 hours",
        "",
        "Evaluation: Test set = 7,178 images | Metrics: Accuracy, F1, Confusion Matrix",
    ],
    'sz': 15,
}

# Slide 9 - Model Deployment and Integration
SLIDE_CONTENT[9] = {
    'content': [
        "Real-Time Pipeline (live_detect_pro.py):",
        "   Step 1: OpenCV reads 720p camera frame at 30 FPS",
        "   Step 2: Convert BGR colour to RGB for MediaPipe",
        "   Step 3: MediaPipe BlazeFace detects face in 3-5 ms",
        "   Step 4: Crop face --> grayscale --> resize 48x48 --> divide by 255",
        "   Step 5: CNN predicts 7 probabilities in 12-18 ms",
        "   Step 6: Add to 10-frame memory --> majority vote --> stable label",
        "   Step 7: Show emotion label and confidence on screen",
        "",
        "Technology Stack:",
        "   Language:    Python 3.10",
        "   ML:          TensorFlow 2.15  |  Keras 2.15",
        "   Vision:      MediaPipe 0.10.9  |  OpenCV 4.8.0",
        "   Numerics:    NumPy 1.26.4",
        "   Launcher:    run_webcam.bat (one double-click on Windows)",
        "   Training:    WSL2 + NVIDIA RTX 2050 GPU",
    ],
    'sz': 16,
}

# Slide 10 - Results and Conclusion
SLIDE_CONTENT[10] = {
    'content': [
        "Classification Results (7,178 FER2013 test images):",
        "   Overall Test Accuracy:  63.51%",
        "   Weighted F1-Score:      62.91%",
        "   Human Baseline:         ~65%    (gap = only 1.49%!)",
        "",
        "Per-Class F1 Scores:",
        "   Happy 84.28% | Neutral 75.44% | Sad 61.08% | Angry 56.88%",
        "   Disgust 54.22% | Surprise 49.17% | Fear 41.21% (hardest)",
        "",
        "Ablation Study (proving each component helps):",
        "   Baseline 3-Block CNN + Normal Loss:     57.34%",
        "   + Focal Loss only:                      61.47%  (+4.13%)",
        "   + Label Smoothing only:                 58.73%  (+1.39%)",
        "   Full Proposed System (all combined):    63.51%  (+6.17%)",
        "",
        "Conclusions:",
        "   Near-human accuracy with a regular laptop at 28-30 FPS",
        "   All 10 real-time test cases: PASSED",
        "   Focal Loss + 10-frame buffer fixed the two main problems",
    ],
    'sz': 15,
}

# Slide 11 - Future Works
SLIDE_CONTENT[11] = {
    'content': [
        "1. Face-Specific Transfer Learning:",
        "   Use VGGFace2 or AffectNet pretrained model as starting point",
        "   Trained on millions of real faces -- much better features",
        "   Expected improvement: +4 to 8% accuracy",
        "",
        "2. Vision Transformer (ViT) Architecture:",
        "   Self-attention connects eyebrow and mouth patterns together",
        "   Better at spotting emotion cues spread across the whole face",
        "",
        "3. Multimodal Emotion Recognition:",
        "   Combine face + voice + body language for higher reliability",
        "",
        "4. Fix Demographic Bias:",
        "   Test on different ages, ethnicities, and genders",
        "   Apply corrections where any group performs worse",
        "",
        "5. Continuous Emotion Modelling:",
        "   Predict emotion on a sliding scale instead of 7 fixed labels",
    ],
    'sz': 16,
}

# Slide 12 - References
SLIDE_CONTENT[12] = {
    'content': [
        "[1]  Goodfellow et al., Challenges in Representation Learning, ICONIP 2013.",
        "[2]  T.-Y. Lin et al., Focal Loss for Dense Object Detection, ICCV 2017.",
        "[3]  Lugaresi et al., MediaPipe: A Framework for Perception Pipelines, arXiv 2019.",
        "[4]  P. Viola, M. J. Jones, Robust Real-Time Face Detection, IJCV vol.57, 2004.",
        "[5]  K. Simonyan, A. Zisserman, Very Deep Convolutional Networks, ICLR 2015.",
        "[6]  M. Tan, Q. V. Le, EfficientNet: Rethinking Model Scaling, ICML 2019.",
        "[7]  S. Ioffe, C. Szegedy, Batch Normalization, ICML 2015.",
        "[8]  N. Srivastava et al., Dropout, JMLR vol.15, 2014.",
        "[9]  K. He et al., Deep Residual Learning for Image Recognition, CVPR 2016.",
        "[10] A. Dosovitskiy et al., An Image is Worth 16x16 Words, ICLR 2021.",
        "[11] R. W. Picard, Affective Computing. MIT Press, 1997.",
        "[12] P. Ekman, W. V. Friesen, Constants Across Cultures, J. Personality & Social Psych., 1971.",
    ],
    'sz': 14,
}

# Slide 13 - Demonstration
SLIDE_CONTENT[13] = {
    'content': [
        "GitHub Repository: https://github.com/Max-i26/emotion_detection",
        "",
        "To Run the Live Demo:",
        "   Step 1: Open Windows PowerShell or Command Prompt",
        "   Step 2: Navigate to:   cd F:\\emotion-detection",
        "   Step 3: Activate:      .\\venv_win\\Scripts\\activate",
        "   Step 4: Run:           python live_detect_pro.py",
        "   Step 5: Press  Q  key to close the camera window",
        "",
        "   OR -- simply double-click:   run_webcam.bat",
    ],
    'sz': 17,
}


# ── BUILD ─────────────────────────────────────────────────────────────────────

def build():
    prs = Presentation(TPL)

    slides = list(prs.slides)

    # ── SLIDE 1: Title Page ───────────────────────────────────────────────────
    sl = slides[0]
    # Shape[0] = Title placeholder: "Project Title"
    # Shape[5] = TextBox with Index/Name/Supervisor
    # Shape[3] = bottom right text
    # Shape[4] = bottom left text

    # Replace title
    for sh in sl.shapes:
        if sh.name == 'Text Placeholder 14' and sh.has_text_frame:
            set_title(sh,
                "REAL-TIME FACIAL EMOTION RECOGNITION\n"
                "USING MEDIAPIPE AND DEEP CNN WITH FOCAL LOSS",
                sz=20, bold=True)

    # Replace Index/Name/Supervisor box
    for sh in sl.shapes:
        if sh.name == 'Rectangle 3' and sh.has_text_frame:
            set_para(sh, [
                "Index No        :  22CDS0439",
                "Name            :  Harol Maxilan",
                "Supervisor      :  Mr. Dimuthu Lakshan",
            ], sz=18, bold=True)

    # Add SUSL logo if not already there
    if os.path.exists(LOGO):
        # Check picture already exists
        has_pic = any(sh.shape_type == 13 for sh in sl.shapes)
        if not has_pic:
            from pptx.util import Inches
            sl.shapes.add_picture(LOGO, Inches(11.2), Inches(1.5),
                                  width=Inches(1.8), height=Inches(1.8))

    # ── SLIDES 2-13: standard content slides ─────────────────────────────────
    for slide_num in range(2, 14):
        sl = slides[slide_num - 1]
        data = SLIDE_CONTENT.get(slide_num)
        if not data:
            continue

        # Find the main content box (Rectangle 3 or Google Shape)
        content_shape = None
        for sh in sl.shapes:
            if sh.has_text_frame and ('Rectangle' in sh.name or 'Shape' in sh.name):
                content_shape = sh
                break

        if content_shape:
            set_para(content_shape, data['content'], sz=data['sz'])

    # ── SLIDE 14: Thank You (leave as-is — template already has it) ──────────

    prs.save(OUT)
    import os as _os
    sz_kb = _os.path.getsize(OUT) // 1024
    print(f"[OK] Saved: {OUT}  ({sz_kb} KB, {len(slides)} slides)")
    print("     Slide verification:")
    prs2 = Presentation(OUT)
    for i, sl2 in enumerate(prs2.slides):
        total_chars = sum(
            len(p.text)
            for sh in sl2.shapes if sh.has_text_frame
            for p in sh.text_frame.paragraphs
        )
        print(f"     Slide {i+1:2d}: {total_chars:4d} chars")


if __name__ == "__main__":
    build()
