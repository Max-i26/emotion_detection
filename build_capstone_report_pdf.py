import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import black, white, gray, HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_header_footer(self, page_count):
        if self._pageNumber == 1:
            return  # Skip cover page
            
        self.saveState()
        self.setFont("Times-Roman", 9)
        
        # Margins: Left 35mm (99.2pt), Right 30mm (85.0pt) -> Width = 595.27
        # Top 30mm (85.0pt) -> Height = 841.89
        left_m = 35 * mm
        right_m = 595.27 - (30 * mm)
        top_h = 841.89 - (20 * mm)
        bot_h = 20 * mm
        
        # Header text
        self.drawString(left_m, top_h, "Department of Data Science")
        self.drawString(left_m, top_h - 10, "Faculty of Computing, SUSL")
        self.drawRightString(right_m, top_h - 5, "Project Report")
        
        # Header line
        self.setLineWidth(0.5)
        self.setStrokeColor(black)
        self.line(left_m, top_h - 15, right_m, top_h - 15)
        
        # Footer line
        self.line(left_m, bot_h + 10, right_m, bot_h + 10)
        
        # Footer page number: [i], [ii], etc. for preliminary, [1], [2] for body
        if self._pageNumber <= 6:
            roman_nums = ["", "i", "ii", "iii", "iv", "v", "vi"]
            p_str = f"[{roman_nums[self._pageNumber - 1]}]" if self._pageNumber - 1 < len(roman_nums) else f"[{self._pageNumber - 1}]"
        else:
            p_str = f"[{self._pageNumber - 6}]"
            
        self.drawCentredString((left_m + right_m) / 2, bot_h - 5, p_str)
        self.restoreState()

def create_report_pdf():
    pdf_filename = "Report/Capstone_Project_Report.pdf"
    
    # 35mm Left (99.2pt), 30mm Right (85pt), 30mm Top/Bottom (85pt)
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=35*mm,
        rightMargin=30*mm,
        topMargin=30*mm,
        bottomMargin=30*mm
    )

    styles = getSampleStyleSheet()
    
    # Custom Styles (Times-Roman, Black, 1.15 line spacing)
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=20,
        leading=24,
        alignment=1, # Center
        textColor=black
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=13,
        leading=16,
        alignment=1,
        textColor=black
    )
    
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=16,
        leading=20,
        spaceBefore=16,
        spaceAfter=10,
        textColor=black
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=13,
        leading=16,
        spaceBefore=12,
        spaceAfter=6,
        textColor=black
    )
    
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=11,
        leading=14.5, # 1.15 line spacing
        alignment=4, # Justified
        spaceAfter=6,
        textColor=black
    )

    bullet_style = ParagraphStyle(
        'ReportBullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    caption_style = ParagraphStyle(
        'Caption',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=9.5,
        leading=12,
        alignment=1,
        spaceBefore=4,
        spaceAfter=12,
        textColor=black
    )

    story = []

    # =========================================================
    # 1. COVER PAGE
    # =========================================================
    story.append(Paragraph("Sabaragamuwa University of Sri Lanka", title_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=black, spaceAfter=15, spaceBefore=0))
    
    if os.path.exists("Report/Screenshot 2026-08-29 095328.png"):
        story.append(Image("Report/Screenshot 2026-08-29 095328.png", width=2.0*inch, height=2.0*inch))
        story.append(Spacer(1, 15))
        
    story.append(Paragraph("[Project Report]", title_style))
    story.append(Spacer(1, 10))
    
    p_t = "<b>Project Title:</b> REAL-TIME FACIAL EMOTION RECOGNITION USING MEDIAPIPE AND DEEP CONVOLUTIONAL NEURAL NETWORKS WITH FOCAL LOSS"
    story.append(Paragraph(p_t, subtitle_style))
    story.append(Spacer(1, 15))
    
    p_sub = "<i>A Project Report submitted to the Faculty of Computing, Sabaragamuwa University of Sri Lanka, in partial fulfillment of the requirements for the Degree of Bachelor of Science Honours in Data Science.</i>"
    story.append(Paragraph(p_sub, ParagraphStyle('SubText', parent=body_style, alignment=1, fontSize=10)))
    story.append(Spacer(1, 20))

    # Cover Page Table
    cp_table_data = [
        [Paragraph("<b>Student Name</b>", body_style), Paragraph("<b>[INSERT NAME]</b>", body_style)],
        [Paragraph("<b>Index Number</b>", body_style), Paragraph("<b>[INSERT INDEX NUMBER]</b>", body_style)],
        [Paragraph("<b>Supervisor Name</b>", body_style), Paragraph("<b>Mr. Dimuthu Lakshan</b>", body_style)]
    ]
    t_cp = Table(cp_table_data, colWidths=[2.0*inch, 3.5*inch])
    t_cp.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_cp)
    story.append(Spacer(1, 25))

    story.append(Paragraph("<b>DEPARTMENT OF DATA SCIENCE<br/>FACULTY OF COMPUTING</b>", ParagraphStyle('Dept', parent=body_style, alignment=1, fontSize=11)))
    story.append(Spacer(1, 10))
    story.append(Paragraph("[September 2026]", ParagraphStyle('Dt', parent=body_style, alignment=1, fontSize=10)))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=black, spaceAfter=0, spaceBefore=10))

    story.append(PageBreak())

    # =========================================================
    # 2. DECLARATION (Appendix A)
    # =========================================================
    story.append(Paragraph("Declaration (Appendix A)", h1_style))
    story.append(Spacer(1, 5))
    
    dec_text = (
        "I declare that this thesis does not incorporate, without acknowledgment, any material previously submitted "
        "for a Degree or a Diploma in any University, and to the best of our knowledge and belief, it does not contain "
        "any material previously published or written by another person or ourself except where due reference is made in "
        "the text. Also, I hereby grant to Sabaragamuwa University of Sri Lanka the non-exclusive right to reproduce "
        "and distribute my report, in whole or in part in print, electronic or other medium. I retain the right to use "
        "this content in whole or part in future works (such as articles or books)."
    )
    story.append(Paragraph(dec_text, body_style))
    story.append(Spacer(1, 25))

    dec_tbl_data = [
        [Paragraph("<b>Date</b>", body_style), Paragraph("<b>Student Index Number</b>", body_style), Paragraph("<b>Student Name</b>", body_style), Paragraph("<b>Signature</b>", body_style)],
        [Paragraph("[Date]", body_style), Paragraph("[INSERT INDEX NUMBER]", body_style), Paragraph("[INSERT NAME]", body_style), Paragraph("_________________", body_style)]
    ]
    t_dec = Table(dec_tbl_data, colWidths=[1.3*inch, 1.6*inch, 1.4*inch, 1.4*inch])
    t_dec.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_dec)
    story.append(Spacer(1, 30))

    # =========================================================
    # 3. CERTIFICATE OF APPROVAL (Appendix B)
    # =========================================================
    story.append(Paragraph("Certificate of Approval (Appendix B)", h1_style))
    story.append(Spacer(1, 5))
    
    cert_text = (
        "We hereby declare that this thesis is from the student's own work and effort, and all other sources "
        "of information used have been acknowledged. This report has been submitted with our approval."
    )
    story.append(Paragraph(cert_text, body_style))
    story.append(Spacer(1, 20))

    cert_tbl_data = [
        [Paragraph("<b>Details</b>", body_style), Paragraph("<b>Signature</b>", body_style), Paragraph("<b>Date</b>", body_style)],
        [Paragraph("Internal Supervisor Name:<br/><b>Mr. Dimuthu Lakshan</b>", body_style), Paragraph("_______________________", body_style), Paragraph("[Date]", body_style)],
        [Paragraph("Head of Department (Signature):<br/><b>Dr. UAP Ishanka</b>", body_style), Paragraph("_______________________", body_style), Paragraph("[Date]", body_style)]
    ]
    t_cert = Table(cert_tbl_data, colWidths=[2.5*inch, 1.8*inch, 1.2*inch])
    t_cert.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_cert)

    story.append(PageBreak())

    # =========================================================
    # 4. ACKNOWLEDGMENTS
    # =========================================================
    story.append(Paragraph("Acknowledgments", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "The successful completion of this capstone project requires the contribution and support of several "
        "individuals. I wish to express my deepest gratitude to my internal supervisor, Mr. Dimuthu Lakshan, for the "
        "invaluable guidance, constructive criticism, and continuous encouragement provided throughout the course of "
        "this research. Your expertise and dedication were crucial in shaping this project from its inception to its final submission.",
        body_style
    ))
    story.append(Paragraph(
        "I am profoundly grateful to Dr. UAP Ishanka, Head of the Department of Data Science, and to all the academic and "
        "non-academic staff of the Faculty of Computing, Sabaragamuwa University of Sri Lanka, for providing the necessary "
        "computational facilities, academic resources, and a highly supportive learning environment.",
        body_style
    ))
    story.append(Paragraph(
        "Finally, I acknowledge the unwavering support of my family and colleagues, whose encouragement helped sustain "
        "my motivation and focus during this intensive period of research and development.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================
    # 5. ABSTRACT
    # =========================================================
    story.append(Paragraph("Abstract", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "This capstone project addresses a significant challenge in automated Computer Vision and Affective Computing: "
        "the real-time, robust recognition of human facial expressions under variable lighting, head poses, and dataset "
        "class imbalance. The purpose of this study is to design, train, and deploy an end-to-end facial emotion recognition "
        "system capable of classifying live webcam frames into seven discrete emotional categories (Angry, Disgust, Fear, "
        "Happy, Sad, Surprise, Neutral). The methodology employs Google MediaPipe for high-accuracy face bounding box detection, "
        "a customized 4-Stage Deep Convolutional Neural Network (CNN) incorporating Batch Normalization and L2 regularization, "
        "and a novel Categorical Focal Loss formulation combined with Label Smoothing (0.1) to mitigate severe minority-class "
        "underrepresentation. Key results indicate that the proposed system achieves a benchmark test accuracy of 63.51% and a "
        "weighted F1-score of 62.91% across 7,178 unseen FER2013 test images, approaching the established human baseline. The system "
        "demonstrates real-time inference capability at 30 frames per second using a 10-frame temporal prediction smoothing buffer "
        "that eliminates frame-to-frame prediction flickering. Based on these findings, the primary recommendation involves "
        "deploying the model within interactive human-computer interaction frameworks. The conclusion is that the proposed solution "
        "effectively meets the stated objectives, offering a robust and validated framework for automated emotion AI.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================
    # 6. TABLE OF CONTENTS
    # =========================================================
    story.append(Paragraph("Table of Contents", h1_style))
    story.append(Spacer(1, 10))
    
    toc_pdf = [
        ("Declaration (Appendix A)", "i"),
        ("Certificate of Approval (Appendix B)", "i"),
        ("Acknowledgments", "ii"),
        ("Abstract", "iii"),
        ("Table of Contents", "iv"),
        ("List of Figures", "v"),
        ("List of Tables", "v"),
        ("Chapter 1: Introduction", "1"),
        ("    1.1 Major Goals and Objectives", "1"),
        ("    1.2 Motivation", "1"),
        ("    1.3 Scope of the Completed Project", "2"),
        ("    1.4 Approach and Assumptions", "2"),
        ("    1.5 Summary of Major Outcomes", "3"),
        ("Chapter 2: Background", "4"),
        ("    2.1 Problem Statement and Context", "4"),
        ("    2.2 Evolution of Facial Emotion Recognition", "4"),
        ("    2.3 FER2013 Benchmark Analysis", "5"),
        ("    2.4 Face Detection: Haar Cascades vs MediaPipe", "6"),
        ("    2.5 Loss Function Innovations: Focal Loss vs Cross-Entropy", "7"),
        ("Chapter 3: Specification and Design", "8"),
        ("    3.1 System Requirements", "8"),
        ("    3.2 System Architecture", "8"),
        ("    3.3 Use Case Diagram & Specifications", "9"),
        ("    3.4 Sequence & State Diagram Specifications", "10"),
        ("Chapter 4: Methodology", "11"),
        ("    4.1 Data Preprocessing & Augmentation", "11"),
        ("    4.2 Focal Loss & Label Smoothing Formulation", "12"),
        ("    4.3 Upgraded 4-Stage ConvNet Architecture", "13"),
        ("    4.4 Real-Time Inference & Temporal Smoothing Buffer", "14"),
        ("Chapter 5: Results and Evaluation", "15"),
        ("    5.1 Experimental Setup & Evaluation Benchmark", "15"),
        ("    5.2 Classification Report & Per-Class Performance", "16"),
        ("    5.3 Confusion Matrix Analysis", "17"),
        ("    5.4 Real-Time Latency & FPS Performance", "18"),
        ("Chapter 6: Future Work", "19"),
        ("    6.1 Project Gaps & Limitations", "19"),
        ("    6.2 Proposals for Enhancement", "19"),
        ("Chapter 7: Conclusions", "20"),
        ("    7.1 Summary of Findings", "20"),
        ("    7.2 Validity & Significance", "20"),
        ("References", "21"),
        ("Appendices", "22")
    ]
    for item, p_num in toc_pdf:
        p_t = f"<b>{item}</b>" if item.startswith("Chapter") or item in ["Declaration (Appendix A)", "Certificate of Approval (Appendix B)", "Acknowledgments", "Abstract", "Table of Contents", "List of Figures", "List of Tables", "References", "Appendices"] else item
        story.append(Paragraph(f"{p_t} <seq format='.'/> .......................................................................................... {p_num}", ParagraphStyle('TOC', parent=body_style, leading=14)))

    story.append(PageBreak())

    # List of Figures & Tables
    story.append(Paragraph("List of Figures", h1_style))
    story.append(Spacer(1, 5))
    lof_pdf = [
        ("Figure 1.1: FER2013 Dataset Class Distribution (Train vs Test Set)", "5"),
        ("Figure 3.1: Real-Time Emotion AI Use Case Diagram", "9"),
        ("Figure 3.2: System Architecture & Real-Time Processing Pipeline", "9"),
        ("Figure 3.3: System Sequence Diagram for Real-Time Detection", "10"),
        ("Figure 5.1: Grayscale Confusion Matrix Heatmap on 7,178 Test Images", "17"),
        ("Figure 5.2: Per-Class F1-Score Performance Comparison", "17")
    ]
    for fig_t, p_num in lof_pdf:
        story.append(Paragraph(f"{fig_t} ........................................... {p_num}", body_style))

    story.append(Spacer(1, 15))
    story.append(Paragraph("List of Tables", h1_style))
    story.append(Spacer(1, 5))
    lot_pdf = [
        ("Table 3.1: Hardware and Software System Specifications", "8"),
        ("Table 4.1: Upgraded 4-Stage Deep ConvNet Architecture Details", "13"),
        ("Table 5.1: Overall Classification Performance Comparison", "15"),
        ("Table 5.2: Detailed Classification Report per Emotion Class", "16")
    ]
    for tab_t, p_num in lot_pdf:
        story.append(Paragraph(f"{tab_t} ........................................... {p_num}", body_style))

    story.append(PageBreak())

    # =========================================================
    # CHAPTER 1: INTRODUCTION
    # =========================================================
    story.append(Paragraph("Chapter 1: Introduction", h1_style))
    story.append(Paragraph(
        "Facial expressions constitute one of the primary non-verbal communication channels used by humans to express "
        "emotions, intentions, and psychological states. In recent years, automated Facial Emotion Recognition (FER) "
        "has emerged as a pivotal domain within Artificial Intelligence, Data Science, and Computer Vision. The capability "
        "to automatically detect and interpret facial affect in real-time has transformative applications in adaptive "
        "learning systems, mental health diagnostics, driver drowsiness monitoring, intelligent customer experience feedback, "
        "and human-robot interaction.",
        body_style
    ))
    
    story.append(Paragraph("1.1 Major Goals and Objectives", h2_style))
    story.append(Paragraph(
        "The primary goal of this capstone project is to develop, evaluate, and deploy a robust, end-to-end real-time "
        "facial emotion recognition system that operates efficiently on consumer-grade hardware. The specific objectives are:",
        body_style
    ))
    objs = [
        "To construct an optimized Deep Convolutional Neural Network (CNN) architecture capable of accurately classifying 7 discrete emotion categories (Angry, Disgust, Fear, Happy, Sad, Surprise, Neutral).",
        "To address severe dataset class imbalance in FER2013 by formulating a Categorical Focal Loss function combined with Label Smoothing (0.1) and dynamic class weighting.",
        "To integrate Google MediaPipe Face Detection for robust face bounding box extraction under varying illumination and head rotations.",
        "To implement a temporal prediction smoothing buffer (10-frame majority vote) to eliminate high-frequency prediction flickering during live webcam inference.",
        "To conduct a rigorous experimental evaluation using 7,178 test images to analyze test loss, accuracy, precision, recall, F1-scores, and confusion matrices."
    ]
    for obj in objs:
        story.append(Paragraph(f"• {obj}", bullet_style))

    story.append(Paragraph("1.2 Motivation", h2_style))
    story.append(Paragraph(
        "Traditional facial expression recognition approaches relied heavily on hand-crafted features such as Local Binary "
        "Patterns (LBP) or Histogram of Oriented Gradients (HOG) combined with Support Vector Machines (SVM). However, these "
        "methods suffer from limited generalization when exposed to real-world occlusions, lighting fluctuations, and unconstrained "
        "head poses. While modern Deep Learning models achieve state-of-the-art results on benchmark datasets, public benchmark datasets "
        "like FER2013 present severe class imbalance (e.g. Disgust contains only 436 training samples compared to 7,215 Happy samples). "
        "This project is motivated by the need to develop an algorithmic pipeline that directly mitigates class imbalance while maintaining "
        "high inference speed for real-time video deployment.",
        body_style
    ))

    story.append(Paragraph("1.3 Scope of the Completed Project", h2_style))
    story.append(Paragraph(
        "The scope of this project encompasses data preprocessing of the FER2013 dataset (28,709 training and 7,178 testing images), "
        "formulation of mathematical loss functions, design and training of a 4-Stage Deep ConvNet, development of a MediaPipe-driven live "
        "webcam capture interface, and empirical benchmark evaluation. The system is designed for deployment on Windows and Linux (WSL) environments.",
        body_style
    ))

    story.append(Paragraph("1.4 Approach and Assumptions", h2_style))
    story.append(Paragraph(
        "The technical approach assumes that input video frames are captured via a standard 720p webcam. It assumes that at least one primary "
        "human face is visible within the camera field of view. Face detection is delegated to MediaPipe's lightweight single-shot detector, "
        "and cropped regions of interest (ROI) are converted to 48x48 normalized grayscale tensors before feeding into the neural network.",
        body_style
    ))

    story.append(Paragraph("1.5 Summary of Major Outcomes", h2_style))
    story.append(Paragraph(
        "The major outcomes of this project include achieving a benchmark test accuracy of 63.51% and a weighted F1-score of 62.91% on "
        "the FER2013 test set, successfully suppressing prediction flickering via a 10-frame deque buffer, and deploying a single-click "
        "Windows batch launcher (run_webcam.bat) for seamless execution.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================
    # CHAPTER 2: BACKGROUND
    # =========================================================
    story.append(Paragraph("Chapter 2: Background", h1_style))
    story.append(Paragraph(
        "This chapter reviews the theoretical foundation, historical evolution, and state-of-the-art developments in Facial Emotion "
        "Recognition (FER). It analyzes the challenges of the FER2013 benchmark dataset, compares traditional face detection techniques "
        "against modern landmark detectors, and discusses loss function innovations for imbalanced datasets.",
        body_style
    ))

    story.append(Paragraph("2.1 Problem Statement and Context", h2_style))
    story.append(Paragraph(
        "Facial emotion recognition in unconstrained real-world environments is complicated by three major challenges: intra-class variance "
        "(people express the same emotion differently), inter-class similarity (emotions like Fear and Surprise share facial muscle movements), "
        "and dataset class imbalance. Standard cross-entropy loss functions cause neural networks to over-predict majority classes (*Happy*, *Neutral*) "
        "while failing on minority classes (*Disgust*, *Fear*).",
        body_style
    ))

    story.append(Paragraph("2.2 FER2013 Benchmark Analysis", h2_style))
    story.append(Paragraph(
        "The FER2013 dataset, created for the ICML 2013 Workshop on Challenges in Representation Learning, contains 35,887 grayscale images "
        "of 48x48 pixels. Figure 1.1 illustrates the class distribution across the training and testing sets, highlighting the severe class imbalance.",
        body_style
    ))

    if os.path.exists("Report/figures/figure_dataset_distribution.png"):
        story.append(Spacer(1, 5))
        story.append(Image("Report/figures/figure_dataset_distribution.png", width=5.5*inch, height=3.5*inch))
        story.append(Paragraph("Figure 1.1: FER2013 Dataset Class Distribution (Train vs Test Set)", caption_style))

    story.append(Paragraph("2.3 Face Detection: Haar Cascades vs Google MediaPipe", h2_style))
    story.append(Paragraph(
        "Traditional OpenCV implementations relied on Viola-Jones Haar Feature-based Cascade Classifiers. While computationally fast, Haar Cascades "
        "suffer from severe false-positive rates, sensitivity to lighting changes, and complete failure under non-frontal head poses. In contrast, "
        "Google MediaPipe uses a single-shot detector (BlazeFace) optimized for mobile and desktop GPUs, providing stable face bounding boxes "
        "under variable illumination and rotation.",
        body_style
    ))

    story.append(Paragraph("2.4 Loss Function Innovations: Focal Loss vs Cross-Entropy", h2_style))
    story.append(Paragraph(
        "Categorical Cross-Entropy (CCE) loss measures performance where the output is a probability value between 0 and 1:<br/>"
        "<i>CCE = - ∑<sub>c=1</sub><sup>C</sup> y<sub>c</sub> log(ŷ<sub>c</sub>)</i><br/>"
        "To combat class imbalance, Lin et al. introduced Focal Loss, which adds a modulating factor (1 - p<sub>t</sub>)<sup>γ</sup> to down-weight easy examples:<br/>"
        "<i>FL(p<sub>t</sub>) = - α<sub>t</sub> (1 - p<sub>t</sub>)<sup>γ</sup> log(p<sub>t</sub>)</i><br/>"
        "In this project, setting γ = 2.0 and incorporating Label Smoothing (0.1) prevents the network from becoming overconfident on ambiguous samples.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================
    # CHAPTER 3: SPECIFICATION AND DESIGN
    # =========================================================
    story.append(Paragraph("Chapter 3: Specification and Design", h1_style))
    story.append(Paragraph(
        "This chapter outlines the formal specifications, architectural designs, and behavioral diagrams for the real-time facial emotion recognition system.",
        body_style
    ))

    story.append(Paragraph("3.1 System Requirements", h2_style))
    
    table_req_pdf_data = [
        [Paragraph("<b>Category</b>", body_style), Paragraph("<b>Specification Details</b>", body_style), Paragraph("<b>Minimum Requirement</b>", body_style)],
        [Paragraph("Operating System", body_style), Paragraph("Windows 10/11 (64-bit) or Ubuntu Linux 20.04/22.04 LTS (WSL2)", body_style), Paragraph("Windows 10", body_style)],
        [Paragraph("Python Environment", body_style), Paragraph("Python 3.10.x with Virtualenv (venv_win)", body_style), Paragraph("Python 3.10", body_style)],
        [Paragraph("Core ML Libraries", body_style), Paragraph("TensorFlow 2.15.0, MediaPipe 0.10.9, OpenCV 4.8.0, NumPy 1.26.4", body_style), Paragraph("TensorFlow 2.15", body_style)],
        [Paragraph("Hardware Sensors", body_style), Paragraph("Standard USB Webcam / Integrated Laptop Camera (720p @ 30 FPS)", body_style), Paragraph("720p Webcam", body_style)]
    ]
    t_req_pdf = Table(table_req_pdf_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch])
    t_req_pdf.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_req_pdf)
    story.append(Paragraph("Table 3.1: Hardware and Software System Specifications", caption_style))

    story.append(Paragraph("3.2 System Architecture & Use Case Specifications", h2_style))
    story.append(Paragraph(
        "Figure 3.1 illustrates the Use Case diagram showing interactions between the User and the Real-Time Emotion AI System boundary. "
        "Figure 3.2 depicts the high-level System Architecture and data pipeline.",
        body_style
    ))

    if os.path.exists("Report/figures/figure_use_case_diagram.png"):
        story.append(Image("Report/figures/figure_use_case_diagram.png", width=5.5*inch, height=3.3*inch))
        story.append(Paragraph("Figure 3.1: Real-Time Emotion AI Use Case Diagram", caption_style))

    if os.path.exists("Report/figures/figure_system_architecture.png"):
        story.append(Image("Report/figures/figure_system_architecture.png", width=5.5*inch, height=3.0*inch))
        story.append(Paragraph("Figure 3.2: System Architecture & Real-Time Processing Pipeline", caption_style))

    story.append(Paragraph("3.3 Sequence Diagram", h2_style))
    story.append(Paragraph(
        "Figure 3.3 illustrates the message flow sequence between the User, Camera Feed, MediaPipe Detector, 4-Stage CNN Model, and Display UI.",
        body_style
    ))

    if os.path.exists("Report/figures/figure_sequence_diagram.png"):
        story.append(Image("Report/figures/figure_sequence_diagram.png", width=5.5*inch, height=3.2*inch))
        story.append(Paragraph("Figure 3.3: System Sequence Diagram for Real-Time Detection", caption_style))

    story.append(PageBreak())

    # =========================================================
    # CHAPTER 4: METHODOLOGY
    # =========================================================
    story.append(Paragraph("Chapter 4: Methodology", h1_style))
    story.append(Paragraph(
        "This chapter details the data preprocessing pipeline, mathematical loss formulation, deep neural network architecture design, "
        "and temporal prediction smoothing buffer implemented for live deployment.",
        body_style
    ))

    story.append(Paragraph("4.1 Upgraded 4-Stage Deep ConvNet Architecture", h2_style))
    story.append(Paragraph(
        "The core emotion classifier is an upgraded 4-Stage Convolutional Neural Network. Table 4.1 lists layer configurations, filter sizes, "
        "activation functions, and regularizers.",
        body_style
    ))

    table_arch_pdf_data = [
        [Paragraph("<b>Stage / Block</b>", body_style), Paragraph("<b>Layer Operations</b>", body_style), Paragraph("<b>Output Shape</b>", body_style), Paragraph("<b>Regularization</b>", body_style)],
        [Paragraph("Input & Block 1", body_style), Paragraph("Conv2D(64, 3x3) x 2 + BatchNorm + MaxPool(2x2)", body_style), Paragraph("(24, 24, 64)", body_style), Paragraph("L2(1e-4), Dropout(0.25)", body_style)],
        [Paragraph("Block 2", body_style), Paragraph("Conv2D(128, 3x3) x 2 + BatchNorm + MaxPool(2x2)", body_style), Paragraph("(12, 12, 128)", body_style), Paragraph("L2(1e-4), Dropout(0.30)", body_style)],
        [Paragraph("Block 3", body_style), Paragraph("Conv2D(256, 3x3) x 2 + BatchNorm + MaxPool(2x2)", body_style), Paragraph("(6, 6, 256)", body_style), Paragraph("L2(1e-4), Dropout(0.35)", body_style)],
        [Paragraph("Block 4", body_style), Paragraph("Conv2D(512, 3x3) x 2 + BatchNorm + MaxPool(2x2)", body_style), Paragraph("(3, 3, 512)", body_style), Paragraph("L2(1e-4), Dropout(0.40)", body_style)],
        [Paragraph("Classifier Head", body_style), Paragraph("GlobalAveragePooling2D + Dense(256) + Dense(7)", body_style), Paragraph("(7,)", body_style), Paragraph("L2(1e-4), Dropout(0.50)", body_style)]
    ]
    t_arch_pdf = Table(table_arch_pdf_data, colWidths=[1.2*inch, 2.3*inch, 1.0*inch, 1.0*inch])
    t_arch_pdf.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_arch_pdf)
    story.append(Paragraph("Table 4.1: Upgraded 4-Stage Deep ConvNet Architecture Details", caption_style))

    story.append(Paragraph("4.2 Real-Time Temporal Prediction Smoothing Buffer", h2_style))
    story.append(Paragraph(
        "During live webcam processing, frame-by-frame raw neural network predictions suffer from high-frequency flickering due to minor lighting "
        "and head movements. To solve this, a 10-frame double-ended queue (collections.deque(maxlen=10)) acts as a sliding temporal buffer. "
        "The system computes the majority vote using Counter(emotion_buffer).most_common(1)[0][0], producing stable emotion overlays.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================
    # CHAPTER 5: RESULTS AND EVALUATION
    # =========================================================
    story.append(Paragraph("Chapter 5: Results and Evaluation", h1_style))
    story.append(Paragraph(
        "This chapter presents the empirical evaluation results of the trained model across 7,178 unseen test images from the FER2013 test set.",
        body_style
    ))

    story.append(Paragraph("5.1 Overall Classification Performance", h2_style))
    story.append(Paragraph(
        "Table 5.1 compares the experimental performance of the proposed 4-Stage ConvNet against the baseline transfer learning model (EfficientNetB0).",
        body_style
    ))

    table_res_pdf_data = [
        [Paragraph("<b>Model Architecture</b>", body_style), Paragraph("<b>Input Format</b>", body_style), Paragraph("<b>Test Loss</b>", body_style), Paragraph("<b>Test Accuracy</b>", body_style)],
        [Paragraph("Upgraded 4-Stage ConvNet (Proposed)", body_style), Paragraph("48x48 Grayscale", body_style), Paragraph("1.0011", body_style), Paragraph("<b>63.51%</b>", body_style)],
        [Paragraph("EfficientNetB0 (Transfer Learning)", body_style), Paragraph("96x96 RGB", body_style), Paragraph("1.4788", body_style), Paragraph("43.90%", body_style)]
    ]
    t_res_pdf = Table(table_res_pdf_data, colWidths=[2.2*inch, 1.2*inch, 1.0*inch, 1.1*inch])
    t_res_pdf.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_res_pdf)
    story.append(Paragraph("Table 5.1: Overall Classification Performance Comparison", caption_style))

    story.append(Paragraph("5.2 Classification Report & Per-Class Metrics", h2_style))
    story.append(Paragraph(
        "Table 5.2 breaks down Precision, Recall, F1-Score, and Support for each emotion class. Figure 5.1 shows the confusion matrix heatmap, "
        "and Figure 5.2 illustrates F1-scores per class.",
        body_style
    ))

    table_cls_pdf_data = [
        [Paragraph("<b>Emotion Class</b>", body_style), Paragraph("<b>Precision</b>", body_style), Paragraph("<b>Recall</b>", body_style), Paragraph("<b>F1-Score</b>", body_style), Paragraph("<b>Support</b>", body_style)],
        [Paragraph("Angry", body_style), Paragraph("53.71%", body_style), Paragraph("60.44%", body_style), Paragraph("56.88%", body_style), Paragraph("958", body_style)],
        [Paragraph("Disgust", body_style), Paragraph("81.82%", body_style), Paragraph("40.54%", body_style), Paragraph("54.22%", body_style), Paragraph("111", body_style)],
        [Paragraph("Fear", body_style), Paragraph("50.79%", body_style), Paragraph("34.67%", body_style), Paragraph("41.21%", body_style), Paragraph("1,024", body_style)],
        [Paragraph("Happy", body_style), Paragraph("82.51%", body_style), Paragraph("86.13%", body_style), Paragraph("84.28%", body_style), Paragraph("1,774", body_style)],
        [Paragraph("Sad", body_style), Paragraph("55.46%", body_style), Paragraph("67.96%", body_style), Paragraph("61.08%", body_style), Paragraph("1,233", body_style)],
        [Paragraph("Surprise", body_style), Paragraph("50.72%", body_style), Paragraph("47.71%", body_style), Paragraph("49.17%", body_style), Paragraph("1,247", body_style)],
        [Paragraph("Neutral", body_style), Paragraph("76.42%", body_style), Paragraph("74.49%", body_style), Paragraph("75.44%", body_style), Paragraph("831", body_style)],
        [Paragraph("<b>Weighted Average</b>", body_style), Paragraph("<b>63.26%</b>", body_style), Paragraph("<b>63.51%</b>", body_style), Paragraph("<b>62.91%</b>", body_style), Paragraph("<b>7,178</b>", body_style)]
    ]
    t_cls_pdf = Table(table_cls_pdf_data, colWidths=[1.3*inch, 1.0*inch, 1.0*inch, 1.0*inch, 1.2*inch])
    t_cls_pdf.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_cls_pdf)
    story.append(Paragraph("Table 5.2: Detailed Classification Report per Emotion Class", caption_style))

    if os.path.exists("Report/figures/figure_confusion_matrix.png"):
        story.append(Spacer(1, 5))
        story.append(Image("Report/figures/figure_confusion_matrix.png", width=5.0*inch, height=4.2*inch))
        story.append(Paragraph("Figure 5.1: Grayscale Confusion Matrix Heatmap on 7,178 Test Images", caption_style))

    if os.path.exists("Report/figures/figure_f1_scores.png"):
        story.append(Spacer(1, 5))
        story.append(Image("Report/figures/figure_f1_scores.png", width=5.0*inch, height=3.0*inch))
        story.append(Paragraph("Figure 5.2: Per-Class F1-Score Performance Comparison", caption_style))

    story.append(PageBreak())

    # =========================================================
    # CHAPTER 6: FUTURE WORK
    # =========================================================
    story.append(Paragraph("Chapter 6: Future Work", h1_style))
    story.append(Paragraph(
        "While the system achieves strong performance, several opportunities for future enhancement exist:",
        body_style
    ))
    story.append(Paragraph("• Pretrained Face Encoders: Transfer learning from models pretrained on face datasets (VGGFace2, AffectNet) instead of ImageNet.", bullet_style))
    story.append(Paragraph("• Vision Transformers (ViT): Utilizing self-attention mechanisms to capture fine-grained facial muscle micro-expressions.", bullet_style))
    story.append(Paragraph("• Multimodal Emotion AI: Combining facial expression recognition with speech audio emotion analysis.", bullet_style))

    story.append(Spacer(1, 15))

    # =========================================================
    # CHAPTER 7: CONCLUSIONS
    # =========================================================
    story.append(Paragraph("Chapter 7: Conclusions", h1_style))
    story.append(Paragraph(
        "This project successfully designed, implemented, evaluated, and deployed a real-time facial emotion recognition system. "
        "By integrating Google MediaPipe face detection, a 4-Stage Deep ConvNet, Categorical Focal Loss, Label Smoothing, and a 10-frame "
        "temporal smoothing buffer, the system achieved a benchmark test accuracy of 63.51% on 7,178 unseen test images. The system meets "
        "all stated requirements, providing a validated framework for real-time Affective Computing applications.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================
    # REFERENCES (IEEE Format)
    # =========================================================
    story.append(Paragraph("References", h1_style))
    story.append(Paragraph("<i>(Note: All references strictly adhere to IEEE Standards)</i>", body_style))
    story.append(Spacer(1, 5))
    
    refs_pdf = [
        '[1] I. J. Goodfellow et al., "Challenges in representation learning: A report on three machine learning contests," in <i>International Conference on Neural Information Processing</i>, Springer, 2013, pp. 117–124.',
        '[2] T. Y. Lin, P. Goyal, R. Girshick, K. He, and P. Dollár, "Focal loss for dense object detection," in <i>Proceedings of the IEEE International Conference on Computer Vision (ICCV)</i>, 2017, pp. 2980–2988.',
        '[3] C. Lugaresi et al., "MediaPipe: A framework for building perception pipelines," <i>arXiv preprint arXiv:1906.08172</i>, 2019.',
        '[4] P. Viola and M. Jones, "Rapid object detection using a boosted cascade of simple features," in <i>Proceedings of the IEEE Computer Society Conference on Computer Vision and Pattern Recognition (CVPR)</i>, vol. 1, 2001, pp. I-I.',
        '[5] K. Simonyan and A. Zisserman, "Very deep convolutional networks for large-scale image recognition," <i>arXiv preprint arXiv:1409.1556</i>, 2014.',
        '[6] M. Tan and Q. V. Le, "EfficientNet: Rethinking model scaling for convolutional neural networks," in <i>International Conference on Machine Learning (ICML)</i>, PMLR, 2019, pp. 6105–6114.',
        '[7] C. Szegedy et al., "Rethinking the inception architecture for computer vision," in <i>Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)</i>, 2016, pp. 2818–2826.'
    ]
    for r in refs_pdf:
        story.append(Paragraph(r, ParagraphStyle('Ref', parent=body_style, leftIndent=20, firstLineIndent=-20, spaceAfter=6)))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Saved PDF Report: {pdf_filename}")

if __name__ == "__main__":
    create_report_pdf()
