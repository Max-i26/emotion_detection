import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os

def set_cell_border(cell, **kwargs):
    """
    Set cell borders for python-docx table cells.
    usage: set_cell_border(cell, top={"sz": 12, "val": "single", "color": "000000"})
    """
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = tcPr.first_child_found_in("w:tcBorders")
    if tcBorders is None:
        tcBorders = OxmlElement('w:tcBorders')
        tcPr.append(tcBorders)

    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = 'w:{}'.format(edge)
            element = tcBorders.find(qn(tag))
            if element is None:
                element = OxmlElement(tag)
                tcBorders.append(element)
            for key in ["sz", "val", "color", "space", "shadow"]:
                if key in edge_data:
                    element.set(qn('w:{}'.format(key)), str(edge_data[key]))

def create_report_docx():
    doc = Document()
    
    # ---------------------------------------------------------
    # Page Setup: A4, 35mm Left (1.38 in), 30mm Right/Top/Bottom (1.18 in)
    # ---------------------------------------------------------
    section = doc.sections[0]
    section.page_width = Inches(8.27)   # A4 Width
    section.page_height = Inches(11.69) # A4 Height
    section.left_margin = Inches(1.38)  # 35mm
    section.right_margin = Inches(1.18) # 30mm
    section.top_margin = Inches(1.18)   # 30mm
    section.bottom_margin = Inches(1.18)# 30mm
    
    # Configure Normal Style: Times New Roman, 12pt, Black, 1.15 line spacing
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0, 0, 0)
    
    p_format = style.paragraph_format
    p_format.line_spacing = 1.15
    p_format.space_after = Pt(6)
    p_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    # Helper to add headings with strict Times New Roman, Black, bold formatting
    def add_custom_heading(text, level):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)
        p.paragraph_format.keep_with_next = True
        
        if level == 1:
            run.font.size = Pt(18)
            p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(12)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif level == 2:
            run.font.size = Pt(14)
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif level == 3:
            run.font.size = Pt(12)
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        return p

    def add_caption(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(12)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        run.bold = True
        return p

    # =========================================================
    # 1. COVER PAGE / TITLE PAGE
    # =========================================================
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_top.add_run("Sabaragamuwa University of Sri Lanka")
    r.font.size = Pt(22)
    r.bold = True

    # Horizontal divider line
    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line_border = parse_xml(r'<w:pBdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                              r'<w:bottom w:val="single" w:sz="12" w:space="1" w:color="000000"/>'
                              r'</w:pBdr>')
    p_line._p.get_or_add_pPr().append(p_line_border)

    # University Logo
    if os.path.exists("Report/Screenshot 2026-08-29 095328.png"):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(12)
        p_logo.paragraph_format.space_after = Pt(12)
        run_logo = p_logo.add_run()
        run_logo.add_picture("Report/Screenshot 2026-08-29 095328.png", width=Inches(2.2))

    p_type = doc.add_paragraph()
    p_type.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_type = p_type.add_run("[Project Report]")
    r_type.font.size = Pt(18)
    r_type.bold = True

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(8)
    p_title.paragraph_format.space_after = Pt(12)
    r_title_label = p_title.add_run("Project Title: ")
    r_title_label.bold = True
    r_title_label.font.size = Pt(13)
    r_title_val = p_title.add_run("REAL-TIME FACIAL EMOTION RECOGNITION USING MEDIAPIPE AND DEEP CONVOLUTIONAL NEURAL NETWORKS WITH FOCAL LOSS")
    r_title_val.bold = True
    r_title_val.font.size = Pt(13)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(24)
    r_sub = p_sub.add_run("A Project Report submitted to the Faculty of Computing, Sabaragamuwa University of Sri Lanka, in partial fulfillment of the requirements for the Degree of Bachelor of Science Honours in Data Science.")
    r_sub.font.size = Pt(11)
    r_sub.italic = True

    # Cover Page Table
    table_cp = doc.add_table(rows=3, cols=2)
    table_cp.alignment = WD_TABLE_ALIGNMENT.CENTER
    cp_data = [
        ("Student Name", "[INSERT NAME]"),
        ("Index Number", "[INSERT INDEX NUMBER]"),
        ("Supervisor Name", "Mr. Dimuthu Lakshan")
    ]
    for i, (label, val) in enumerate(cp_data):
        row = table_cp.rows[i]
        cell_lbl, cell_val = row.cells[0], row.cells[1]
        cell_lbl.width = Inches(2.2)
        cell_val.width = Inches(3.8)
        
        p0 = cell_lbl.paragraphs[0]
        p0.paragraph_format.line_spacing = 1.15
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.size = Pt(11)
        
        p1 = cell_val.paragraphs[0]
        p1.paragraph_format.line_spacing = 1.15
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(val)
        r1.bold = True
        r1.font.size = Pt(11)
        
        # add table borders
        set_cell_border(cell_lbl, bottom={"sz": 4, "val": "single", "color": "000000"})
        set_cell_border(cell_val, bottom={"sz": 4, "val": "single", "color": "000000"})

    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_before = Pt(24)
    p_dept.paragraph_format.space_after = Pt(2)
    r_dept = p_dept.add_run("DEPARTMENT OF DATA SCIENCE\nFACULTY OF COMPUTING")
    r_dept.bold = True
    r_dept.font.size = Pt(12)

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_date.paragraph_format.space_before = Pt(12)
    r_date = p_date.add_run("[September 2026]")
    r_date.font.size = Pt(11)

    # Bottom line
    p_bline = doc.add_paragraph()
    p_bline.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_bline._p.get_or_add_pPr().append(p_line_border)

    doc.add_page_break()

    # =========================================================
    # PRELIMINARY PAGES SETUP (Headers / Footers)
    # =========================================================
    sec_body = doc.add_section()
    sec_body.header.is_linked_to_previous = False
    
    # Header format
    hdr = sec_body.header
    p_hdr = hdr.paragraphs[0]
    p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_hdr_l = p_hdr.add_run("Department of Data Science\nFaculty of Computing, SUSL\t\tProject Report")
    r_hdr_l.font.name = 'Times New Roman'
    r_hdr_l.font.size = Pt(9.5)
    r_hdr_l.italic = True
    p_hdr._p.get_or_add_pPr().append(p_line_border)

    # =========================================================
    # 2. DECLARATION (Appendix A)
    # =========================================================
    add_custom_heading("Declaration (Appendix A)", 1)
    
    p_dec = doc.add_paragraph(
        "I declare that this thesis does not incorporate, without acknowledgment, any material previously submitted "
        "for a Degree or a Diploma in any University, and to the best of our knowledge and belief, it does not contain "
        "any material previously published or written by another person or ourself except where due reference is made in "
        "the text. Also, I hereby grant to Sabaragamuwa University of Sri Lanka the non-exclusive right to reproduce "
        "and distribute my report, in whole or in part in print, electronic or other medium. I retain the right to use "
        "this content in whole or part in future works (such as articles or books)."
    )
    p_dec.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    doc.add_paragraph() # spacing
    
    table_dec = doc.add_table(rows=2, cols=4)
    table_dec.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_dec = ["Date", "Student Index Number", "Student Name", "Signature"]
    for j, h_text in enumerate(headers_dec):
        cell = table_dec.cell(0, j)
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.bold = True
        r.font.size = Pt(10.5)
        cell.width = Inches(1.4)
        
    vals_dec = ["[Date]", "[INSERT INDEX NUMBER]", "[INSERT NAME]", "_________________"]
    for j, v_text in enumerate(vals_dec):
        cell = table_dec.cell(1, j)
        p = cell.paragraphs[0]
        r = p.add_run(v_text)
        r.font.size = Pt(10)
        cell.width = Inches(1.4)
        set_cell_border(cell, bottom={"sz": 4, "val": "single", "color": "000000"})

    doc.add_paragraph()
    doc.add_paragraph()

    # =========================================================
    # 3. CERTIFICATE OF APPROVAL (Appendix B)
    # =========================================================
    add_custom_heading("Certificate of Approval (Appendix B)", 1)
    
    p_cert = doc.add_paragraph(
        "We hereby declare that this thesis is from the student's own work and effort, and all other sources "
        "of information used have been acknowledged. This report has been submitted with our approval."
    )
    p_cert.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    doc.add_paragraph()
    
    table_cert = doc.add_table(rows=3, cols=3)
    table_cert.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Header row
    h_cert = ["Details", "Signature", "Date"]
    for j, h_text in enumerate(h_cert):
        cell = table_cert.cell(0, j)
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.bold = True
        r.font.size = Pt(10.5)
        
    row1 = table_cert.rows[1]
    row1.cells[0].paragraphs[0].add_run("Internal Supervisor Name:\nMr. Dimuthu Lakshan").bold = True
    row1.cells[1].paragraphs[0].add_run("_______________________")
    row1.cells[2].paragraphs[0].add_run("[Date]")
    
    row2 = table_cert.rows[2]
    row2.cells[0].paragraphs[0].add_run("Head of Department (Signature):\nDr. UAP Ishanka").bold = True
    row2.cells[1].paragraphs[0].add_run("_______________________")
    row2.cells[2].paragraphs[0].add_run("[Date]")
    
    for r_idx in range(3):
        for c_idx in range(3):
            cell = table_cert.cell(r_idx, c_idx)
            set_cell_border(cell, top={"sz": 4, "val": "single", "color": "000000"},
                                  bottom={"sz": 4, "val": "single", "color": "000000"},
                                  left={"sz": 4, "val": "single", "color": "000000"},
                                  right={"sz": 4, "val": "single", "color": "000000"})

    doc.add_page_break()

    # =========================================================
    # 4. ACKNOWLEDGMENTS
    # =========================================================
    add_custom_heading("Acknowledgments", 1)
    
    doc.add_paragraph(
        "The successful completion of this capstone project requires the contribution and support of several "
        "individuals. I wish to express my deepest gratitude to my internal supervisor, Mr. Dimuthu Lakshan, for the "
        "invaluable guidance, constructive criticism, and continuous encouragement provided throughout the course of "
        "this research. Your expertise and dedication were crucial in shaping this project from its inception to its final submission."
    )
    doc.add_paragraph(
        "I am profoundly grateful to Dr. UAP Ishanka, Head of the Department of Data Science, and to all the academic and "
        "non-academic staff of the Faculty of Computing, Sabaragamuwa University of Sri Lanka, for providing the necessary "
        "computational facilities, academic resources, and a highly supportive learning environment."
    )
    doc.add_paragraph(
        "Finally, I acknowledge the unwavering support of my family and colleagues, whose encouragement helped sustain "
        "my motivation and focus during this intensive period of research and development."
    )

    doc.add_page_break()

    # =========================================================
    # 5. ABSTRACT
    # =========================================================
    add_custom_heading("Abstract", 1)
    
    doc.add_paragraph(
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
        "effectively meets the stated objectives, offering a robust and validated framework for automated emotion AI."
    )

    doc.add_page_break()

    # =========================================================
    # 6. TABLE OF CONTENTS, LIST OF FIGURES, LIST OF TABLES
    # =========================================================
    add_custom_heading("Table of Contents", 1)
    
    toc_items = [
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
    
    for item, p_num in toc_items:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(2)
        r1 = p.add_run(item)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(11)
        if item.startswith("Chapter") or item in ["Declaration (Appendix A)", "Certificate of Approval (Appendix B)", "Acknowledgments", "Abstract", "Table of Contents", "List of Figures", "List of Tables", "References", "Appendices"]:
            r1.bold = True
        
        # Dot leader alignment
        r2 = p.add_run(f"\t{p_num}")
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(11)

    doc.add_page_break()

    # List of Figures & Tables
    add_custom_heading("List of Figures", 1)
    lof_items = [
        ("Figure 1.1: FER2013 Dataset Class Distribution (Train vs Test Set)", "5"),
        ("Figure 3.1: Real-Time Emotion AI Use Case Diagram", "9"),
        ("Figure 3.2: System Architecture & Real-Time Processing Pipeline", "9"),
        ("Figure 3.3: System Sequence Diagram for Real-Time Detection", "10"),
        ("Figure 5.1: Grayscale Confusion Matrix Heatmap on 7,178 Test Images", "17"),
        ("Figure 5.2: Per-Class F1-Score Performance Comparison", "17")
    ]
    for fig_title, p_num in lof_items:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(f"{fig_title}\t{p_num}")
        r.font.size = Pt(11)

    doc.add_paragraph()
    add_custom_heading("List of Tables", 1)
    lot_items = [
        ("Table 3.1: Hardware and Software System Specifications", "8"),
        ("Table 4.1: Upgraded 4-Stage Deep ConvNet Architecture Details", "13"),
        ("Table 5.1: Overall Classification Performance Comparison", "15"),
        ("Table 5.2: Detailed Classification Report per Emotion Class", "16")
    ]
    for tab_title, p_num in lot_items:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(f"{tab_title}\t{p_num}")
        r.font.size = Pt(11)

    doc.add_page_break()

    # =========================================================
    # CHAPTER 1: INTRODUCTION
    # =========================================================
    add_custom_heading("Chapter 1: Introduction", 1)
    
    doc.add_paragraph(
        "Facial expressions constitute one of the primary non-verbal communication channels used by humans to express "
        "emotions, intentions, and psychological states. In recent years, automated Facial Emotion Recognition (FER) "
        "has emerged as a pivotal domain within Artificial Intelligence, Data Science, and Computer Vision. The capability "
        "to automatically detect and interpret facial affect in real-time has transformative applications in adaptive "
        "learning systems, mental health diagnostics, driver drowsiness monitoring, intelligent customer experience feedback, "
        "and human-robot interaction."
    )
    
    add_custom_heading("1.1 Major Goals and Objectives", 2)
    doc.add_paragraph(
        "The primary goal of this capstone project is to develop, evaluate, and deploy a robust, end-to-end real-time "
        "facial emotion recognition system that operates efficiently on consumer-grade hardware. The specific objectives are:"
    )
    objectives = [
        "To construct an optimized Deep Convolutional Neural Network (CNN) architecture capable of accurately classifying 7 discrete emotion categories (Angry, Disgust, Fear, Happy, Sad, Surprise, Neutral).",
        "To address severe dataset class imbalance in FER2013 by formulating a Categorical Focal Loss function combined with Label Smoothing (0.1) and dynamic class weighting.",
        "To integrate Google MediaPipe Face Detection for robust face bounding box extraction under varying illumination and head rotations.",
        "To implement a temporal prediction smoothing buffer (10-frame majority vote) to eliminate high-frequency prediction flickering during live webcam inference.",
        "To conduct a rigorous experimental evaluation using 7,178 test images to analyze test loss, accuracy, precision, recall, F1-scores, and confusion matrices."
    ]
    for obj in objectives:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        p.add_run(obj)

    add_custom_heading("1.2 Motivation", 2)
    doc.add_paragraph(
        "Traditional facial expression recognition approaches relied heavily on hand-crafted features such as Local Binary "
        "Patterns (LBP) or Histogram of Oriented Gradients (HOG) combined with Support Vector Machines (SVM). However, these "
        "methods suffer from limited generalization when exposed to real-world occlusions, lighting fluctuations, and unconstrained "
        "head poses. While modern Deep Learning models achieve state-of-the-art results on benchmark datasets, public benchmark datasets "
        "like FER2013 present severe class imbalance (e.g. Disgust contains only 436 training samples compared to 7,215 Happy samples). "
        "This project is motivated by the need to develop an algorithmic pipeline that directly mitigates class imbalance while maintaining "
        "high inference speed for real-time video deployment."
    )

    add_custom_heading("1.3 Scope of the Completed Project", 2)
    doc.add_paragraph(
        "The scope of this project encompasses data preprocessing of the FER2013 dataset (28,709 training and 7,178 testing images), "
        "formulation of mathematical loss functions, design and training of a 4-Stage Deep ConvNet, development of a MediaPipe-driven live "
        "webcam capture interface, and empirical benchmark evaluation. The system is designed for deployment on Windows and Linux (WSL) environments."
    )

    add_custom_heading("1.4 Approach and Assumptions", 2)
    doc.add_paragraph(
        "The technical approach assumes that input video frames are captured via a standard 720p webcam. It assumes that at least one primary "
        "human face is visible within the camera field of view. Face detection is delegated to MediaPipe's lightweight single-shot detector, "
        "and cropped regions of interest (ROI) are converted to 48x48 normalized grayscale tensors before feeding into the neural network."
    )

    add_custom_heading("1.5 Concise Summary of Major Outcomes", 2)
    doc.add_paragraph(
        "The major outcomes of this project include achieving a benchmark test accuracy of 63.51% and a weighted F1-score of 62.91% on "
        "the FER2013 test set, successfully suppressing prediction flickering via a 10-frame deque buffer, and deploying a single-click "
        "Windows batch launcher (run_webcam.bat) for seamless execution."
    )

    doc.add_page_break()

    # =========================================================
    # CHAPTER 2: BACKGROUND
    # =========================================================
    add_custom_heading("Chapter 2: Background", 1)
    
    doc.add_paragraph(
        "This chapter reviews the theoretical foundation, historical evolution, and state-of-the-art developments in Facial Emotion "
        "Recognition (FER). It analyzes the challenges of the FER2013 benchmark dataset, compares traditional face detection techniques "
        "against modern landmark detectors, and discusses loss function innovations for imbalanced datasets."
    )

    add_custom_heading("2.1 Problem Statement and Context", 2)
    doc.add_paragraph(
        "Facial emotion recognition in unconstrained real-world environments is complicated by three major challenges: intra-class variance "
        "(people express the same emotion differently), inter-class similarity (emotions like Fear and Surprise share facial muscle movements), "
        "and dataset class imbalance. Standard cross-entropy loss functions cause neural networks to over-predict majority classes (*Happy*, *Neutral*) "
        "while failing on minority classes (*Disgust*, *Fear*)."
    )

    add_custom_heading("2.2 FER2013 Benchmark Analysis", 2)
    doc.add_paragraph(
        "The FER2013 dataset, created for the ICML 2013 Workshop on Challenges in Representation Learning, contains 35,887 grayscale images "
        "of 48x48 pixels. Figure 1.1 illustrates the class distribution across the training and testing sets, highlighting the severe class imbalance."
    )
    
    if os.path.exists("Report/figures/figure_dataset_distribution.png"):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture("Report/figures/figure_dataset_distribution.png", width=Inches(5.5))
        add_caption("Figure 1.1: FER2013 Dataset Class Distribution (Train vs Test Set)")

    add_custom_heading("2.3 Face Detection: Haar Cascades vs Google MediaPipe", 2)
    doc.add_paragraph(
        "Traditional OpenCV implementations relied on Viola-Jones Haar Feature-based Cascade Classifiers. While computationally fast, Haar Cascades "
        "suffer from severe false-positive rates, sensitivity to lighting changes, and complete failure under non-frontal head poses. In contrast, "
        "Google MediaPipe uses a single-shot detector (BlazeFace) optimized for mobile and desktop GPUs, providing stable face bounding boxes "
        "under variable illumination and rotation."
    )

    add_custom_heading("2.4 Loss Function Innovations: Focal Loss vs Cross-Entropy", 2)
    doc.add_paragraph(
        "Categorical Cross-Entropy (CCE) loss measures performance where the output is a probability value between 0 and 1:\n"
        "CCE = - \\sum_{c=1}^{C} y_c \\log(\\hat{y}_c)\n"
        "To combat class imbalance, Lin et al. introduced Focal Loss, which adds a modulating factor (1 - p_t)^\\gamma to down-weight easy examples:\n"
        "FL(p_t) = - \\alpha_t (1 - p_t)^\\gamma \\log(p_t)\n"
        "In this project, setting \\gamma = 2.0$ and incorporating Label Smoothing (0.1) prevents the network from becoming overconfident on ambiguous samples."
    )

    doc.add_page_break()

    # =========================================================
    # CHAPTER 3: SPECIFICATION AND DESIGN
    # =========================================================
    add_custom_heading("Chapter 3: Specification and Design", 1)
    
    doc.add_paragraph(
        "This chapter outlines the formal specifications, architectural designs, and behavioral diagrams for the real-time facial emotion recognition system."
    )

    add_custom_heading("3.1 System Requirements", 2)
    
    table_req = doc.add_table(rows=5, cols=3)
    table_req.alignment = WD_TABLE_ALIGNMENT.CENTER
    req_headers = ["Category", "Specification Details", "Minimum Requirement"]
    for j, h in enumerate(req_headers):
        cell = table_req.cell(0, j)
        p = cell.paragraphs[0]
        p.add_run(h).bold = True
        cell.width = Inches(2.0 if j!=0 else 1.5)
        
    req_data = [
        ("Operating System", "Windows 10/11 (64-bit) or Ubuntu Linux 20.04/22.04 LTS (WSL2)", "Windows 10"),
        ("Python Environment", "Python 3.10.x with Virtualenv (venv_win)", "Python 3.10"),
        ("Core ML Libraries", "TensorFlow 2.15.0, MediaPipe 0.10.9, OpenCV 4.8.0, NumPy 1.26.4", "TensorFlow 2.15"),
        ("Hardware Sensors", "Standard USB Webcam / Integrated Laptop Camera (720p @ 30 FPS)", "720p Webcam")
    ]
    for i, row in enumerate(req_data):
        for j, val in enumerate(row):
            cell = table_req.cell(i+1, j)
            p = cell.paragraphs[0]
            p.add_run(val)
            set_cell_border(cell, top={"sz": 4, "val": "single", "color": "000000"},
                                  bottom={"sz": 4, "val": "single", "color": "000000"},
                                  left={"sz": 4, "val": "single", "color": "000000"},
                                  right={"sz": 4, "val": "single", "color": "000000"})

    add_caption("Table 3.1: Hardware and Software System Specifications")

    add_custom_heading("3.2 System Architecture & Use Case Specifications", 2)
    doc.add_paragraph(
        "Figure 3.1 illustrates the Use Case diagram showing interactions between the User and the Real-Time Emotion AI System boundary. "
        "Figure 3.2 depicts the high-level System Architecture and data pipeline."
    )

    if os.path.exists("Report/figures/figure_use_case_diagram.png"):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture("Report/figures/figure_use_case_diagram.png", width=Inches(5.5))
        add_caption("Figure 3.1: Real-Time Emotion AI Use Case Diagram")

    if os.path.exists("Report/figures/figure_system_architecture.png"):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture("Report/figures/figure_system_architecture.png", width=Inches(5.8))
        add_caption("Figure 3.2: System Architecture & Real-Time Processing Pipeline")

    add_custom_heading("3.3 Sequence Diagram", 2)
    doc.add_paragraph(
        "Figure 3.3 illustrates the message flow sequence between the User, Camera Feed, MediaPipe Detector, 4-Stage CNN Model, and Display UI."
    )

    if os.path.exists("Report/figures/figure_sequence_diagram.png"):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture("Report/figures/figure_sequence_diagram.png", width=Inches(5.8))
        add_caption("Figure 3.3: System Sequence Diagram for Real-Time Detection")

    doc.add_page_break()

    # =========================================================
    # CHAPTER 4: METHODOLOGY
    # =========================================================
    add_custom_heading("Chapter 4: Methodology", 1)
    
    doc.add_paragraph(
        "This chapter details the data preprocessing pipeline, mathematical loss formulation, deep neural network architecture design, "
        "and temporal prediction smoothing buffer implemented for live deployment."
    )

    add_custom_heading("4.1 Upgraded 4-Stage Deep ConvNet Architecture", 2)
    doc.add_paragraph(
        "The core emotion classifier is an upgraded 4-Stage Convolutional Neural Network. Table 4.1 lists layer configurations, filter sizes, "
        "activation functions, and regularizers."
    )

    table_arch = doc.add_table(rows=6, cols=4)
    table_arch.alignment = WD_TABLE_ALIGNMENT.CENTER
    arch_headers = ["Stage / Block", "Layer Operations", "Output Shape", "Regularization"]
    for j, h in enumerate(arch_headers):
        cell = table_arch.cell(0, j)
        p = cell.paragraphs[0]
        p.add_run(h).bold = True
        cell.width = Inches(1.5)
        
    arch_data = [
        ("Input & Block 1", "Conv2D(64, 3x3) x 2 + BatchNorm + MaxPool(2x2)", "(24, 24, 64)", "L2(1e-4), Dropout(0.25)"),
        ("Block 2", "Conv2D(128, 3x3) x 2 + BatchNorm + MaxPool(2x2)", "(12, 12, 128)", "L2(1e-4), Dropout(0.30)"),
        ("Block 3", "Conv2D(256, 3x3) x 2 + BatchNorm + MaxPool(2x2)", "(6, 6, 256)", "L2(1e-4), Dropout(0.35)"),
        ("Block 4", "Conv2D(512, 3x3) x 2 + BatchNorm + MaxPool(2x2)", "(3, 3, 512)", "L2(1e-4), Dropout(0.40)"),
        ("Classifier Head", "GlobalAveragePooling2D + Dense(256) + Dense(7)", "(7,)", "L2(1e-4), Dropout(0.50)")
    ]
    for i, row in enumerate(arch_data):
        for j, val in enumerate(row):
            cell = table_arch.cell(i+1, j)
            p = cell.paragraphs[0]
            p.add_run(val)
            set_cell_border(cell, top={"sz": 4, "val": "single", "color": "000000"},
                                  bottom={"sz": 4, "val": "single", "color": "000000"},
                                  left={"sz": 4, "val": "single", "color": "000000"},
                                  right={"sz": 4, "val": "single", "color": "000000"})

    add_caption("Table 4.1: Upgraded 4-Stage Deep ConvNet Architecture Details")

    add_custom_heading("4.2 Real-Time Temporal Prediction Smoothing Buffer", 2)
    doc.add_paragraph(
        "During live webcam processing, frame-by-frame raw neural network predictions suffer from high-frequency flickering due to minor lighting "
        "and head movements. To solve this, a 10-frame double-ended queue (collections.deque(maxlen=10)) acts as a sliding temporal buffer. "
        "The system computes the majority vote using Counter(emotion_buffer).most_common(1)[0][0], producing stable emotion overlays."
    )

    doc.add_page_break()

    # =========================================================
    # CHAPTER 5: RESULTS AND EVALUATION
    # =========================================================
    add_custom_heading("Chapter 5: Results and Evaluation", 1)
    
    doc.add_paragraph(
        "This chapter presents the empirical evaluation results of the trained model across 7,178 unseen test images from the FER2013 test set."
    )

    add_custom_heading("5.1 Overall Classification Performance", 2)
    doc.add_paragraph(
        "Table 5.1 compares the experimental performance of the proposed 4-Stage ConvNet against the baseline transfer learning model (EfficientNetB0)."
    )

    table_res = doc.add_table(rows=3, cols=4)
    table_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    res_headers = ["Model Architecture", "Input Format", "Test Loss", "Test Accuracy"]
    for j, h in enumerate(res_headers):
        cell = table_res.cell(0, j)
        p = cell.paragraphs[0]
        p.add_run(h).bold = True
        cell.width = Inches(1.5)
        
    res_data = [
        ("Upgraded 4-Stage ConvNet (Proposed)", "48x48 Grayscale", "1.0011", "63.51%"),
        ("EfficientNetB0 (Transfer Learning)", "96x96 RGB", "1.4788", "43.90%")
    ]
    for i, row in enumerate(res_data):
        for j, val in enumerate(row):
            cell = table_res.cell(i+1, j)
            p = cell.paragraphs[0]
            p.add_run(val)
            set_cell_border(cell, top={"sz": 4, "val": "single", "color": "000000"},
                                  bottom={"sz": 4, "val": "single", "color": "000000"},
                                  left={"sz": 4, "val": "single", "color": "000000"},
                                  right={"sz": 4, "val": "single", "color": "000000"})

    add_caption("Table 5.1: Overall Classification Performance Comparison")

    add_custom_heading("5.2 Classification Report & Per-Class Metrics", 2)
    doc.add_paragraph(
        "Table 5.2 breaks down Precision, Recall, F1-Score, and Support for each emotion class. Figure 5.1 shows the confusion matrix heatmap, "
        "and Figure 5.2 illustrates F1-scores per class."
    )

    table_cls = doc.add_table(rows=9, cols=5)
    table_cls.alignment = WD_TABLE_ALIGNMENT.CENTER
    cls_headers = ["Emotion Class", "Precision", "Recall", "F1-Score", "Support"]
    for j, h in enumerate(cls_headers):
        cell = table_cls.cell(0, j)
        p = cell.paragraphs[0]
        p.add_run(h).bold = True
        cell.width = Inches(1.2)
        
    cls_data = [
        ("Angry", "53.71%", "60.44%", "56.88%", "958"),
        ("Disgust", "81.82%", "40.54%", "54.22%", "111"),
        ("Fear", "50.79%", "34.67%", "41.21%", "1,024"),
        ("Happy", "82.51%", "86.13%", "84.28%", "1,774"),
        ("Sad", "55.46%", "67.96%", "61.08%", "1,233"),
        ("Surprise", "50.72%", "47.71%", "49.17%", "1,247"),
        ("Neutral", "76.42%", "74.49%", "75.44%", "831"),
        ("Weighted Average", "63.26%", "63.51%", "62.91%", "7,178")
    ]
    for i, row in enumerate(cls_data):
        for j, val in enumerate(row):
            cell = table_cls.cell(i+1, j)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            if i == 7:
                r.bold = True
            set_cell_border(cell, top={"sz": 4, "val": "single", "color": "000000"},
                                  bottom={"sz": 4, "val": "single", "color": "000000"},
                                  left={"sz": 4, "val": "single", "color": "000000"},
                                  right={"sz": 4, "val": "single", "color": "000000"})

    add_caption("Table 5.2: Detailed Classification Report per Emotion Class")

    if os.path.exists("Report/figures/figure_confusion_matrix.png"):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture("Report/figures/figure_confusion_matrix.png", width=Inches(5.0))
        add_caption("Figure 5.1: Grayscale Confusion Matrix Heatmap on 7,178 Test Images")

    if os.path.exists("Report/figures/figure_f1_scores.png"):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture("Report/figures/figure_f1_scores.png", width=Inches(5.0))
        add_caption("Figure 5.2: Per-Class F1-Score Performance Comparison")

    doc.add_page_break()

    # =========================================================
    # CHAPTER 6: FUTURE WORK
    # =========================================================
    add_custom_heading("Chapter 6: Future Work", 1)
    
    doc.add_paragraph(
        "While the system achieves strong performance, several opportunities for future enhancement exist:"
    )
    gaps = [
        "Pretrained Face Encoders: Transfer learning from models pretrained on face datasets (VGGFace2, AffectNet) instead of ImageNet.",
        "Vision Transformers (ViT): Utilizing self-attention mechanisms to capture fine-grained facial muscle micro-expressions.",
        "Multimodal Emotion AI: Combining facial expression recognition with speech audio emotion analysis."
    ]
    for g in gaps:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        p.add_run(g)

    doc.add_paragraph()

    # =========================================================
    # CHAPTER 7: CONCLUSIONS
    # =========================================================
    add_custom_heading("Chapter 7: Conclusions", 1)
    
    doc.add_paragraph(
        "This project successfully designed, implemented, evaluated, and deployed a real-time facial emotion recognition system. "
        "By integrating Google MediaPipe face detection, a 4-Stage Deep ConvNet, Categorical Focal Loss, Label Smoothing, and a 10-frame "
        "temporal smoothing buffer, the system achieved a benchmark test accuracy of 63.51% on 7,178 unseen test images. The system meets "
        "all stated requirements, providing a validated framework for real-time Affective Computing applications."
    )

    doc.add_page_break()

    # =========================================================
    # REFERENCES (IEEE Format)
    # =========================================================
    add_custom_heading("References", 1)
    doc.add_paragraph("(Note: All references strictly adhere to IEEE Standards)").italic = True
    
    refs = [
        '[1] I. J. Goodfellow et al., "Challenges in representation learning: A report on three machine learning contests," in International Conference on Neural Information Processing, Springer, 2013, pp. 117–124.',
        '[2] T. Y. Lin, P. Goyal, R. Girshick, K. He, and P. Dollár, "Focal loss for dense object detection," in Proceedings of the IEEE International Conference on Computer Vision (ICCV), 2017, pp. 2980–2988.',
        '[3] C. Lugaresi et al., "MediaPipe: A framework for building perception pipelines," arXiv preprint arXiv:1906.08172, 2019.',
        '[4] P. Viola and M. Jones, "Rapid object detection using a boosted cascade of simple features," in Proceedings of the IEEE Computer Society Conference on Computer Vision and Pattern Recognition (CVPR), vol. 1, 2001, pp. I-I.',
        '[5] K. Simonyan and A. Zisserman, "Very deep convolutional networks for large-scale image recognition," arXiv preprint arXiv:1409.1556, 2014.',
        '[6] M. Tan and Q. V. Le, "EfficientNet: Rethinking model scaling for convolutional neural networks," in International Conference on Machine Learning (ICML), PMLR, 2019, pp. 6105–6114.',
        '[7] C. Szegedy et al., "Rethinking the inception architecture for computer vision," in Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2016, pp. 2818–2826.'
    ]
    for ref in refs:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.first_line_indent = Inches(-0.4)
        p.paragraph_format.space_after = Pt(4)
        p.add_run(ref)

    # Save Word document
    output_docx = "Report/Capstone_Project_Report.docx"
    doc.save(output_docx)
    print(f"[OK] Saved Word Report: {output_docx}")

if __name__ == "__main__":
    create_report_docx()
