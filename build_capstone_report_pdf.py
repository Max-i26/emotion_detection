"""
Capstone Project Report Builder - Complete Fixed Version
Student: Harol Maxilan | Index: 22CDS0439
Supervisor: Mr. Dimuthu Lakshan | HOD: Dr. UAP Ishanka
Date: 28/09/2026
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas as canvas_module

W, H = A4  # 595.27, 841.89 points
LM = 35 * mm   # left margin
RM = 30 * mm   # right margin
TM = 30 * mm   # top margin
BM = 30 * mm   # bottom margin
BODY_W = W - LM - RM  # usable text width

DOTS = "." * 80  # dot leader string


# ─────────────────────────────────────────────────────────────────────────────
# PAGE CANVAS WITH HEADER / FOOTER
# ─────────────────────────────────────────────────────────────────────────────
class ReportCanvas(canvas_module.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        for i, state in enumerate(self._saved_page_states):
            self.__dict__.update(state)
            if i > 0:          # Skip cover page (page 1)
                self._draw_page_furniture(i + 1)
            canvas_module.Canvas.showPage(self)
        canvas_module.Canvas.save(self)

    def _draw_page_furniture(self, page_num):
        self.saveState()
        self.setFont("Times-Roman", 9)
        lx = LM
        rx = W - RM
        # Header
        hy = H - TM + 8 * mm
        self.drawString(lx, hy,      "Department of Data Science")
        self.drawString(lx, hy - 11, "Faculty of Computing, SUSL")
        self.drawRightString(rx, hy - 5, "Project Report")
        self.setLineWidth(0.5)
        self.line(lx, hy - 17, rx, hy - 17)
        # Footer
        fy = BM - 8 * mm
        self.line(lx, fy + 14, rx, fy + 14)
        # Page numbering: preliminary pages i-vi, body pages from 1
        if page_num <= 6:
            nums = {2: "i", 3: "ii", 4: "iii", 5: "iv", 6: "v"}
            label = f"[{nums.get(page_num, str(page_num - 1))}]"
        else:
            label = f"[{page_num - 6}]"
        self.drawCentredString((lx + rx) / 2, fy, label)
        self.restoreState()


# ─────────────────────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────────────────────
def make_styles():
    s = {}

    base = ParagraphStyle('base',
        fontName='Times-Roman', fontSize=11, leading=14.5,
        textColor=black, alignment=TA_JUSTIFY,
        spaceAfter=6, spaceBefore=0)

    s['body'] = base

    s['body_left'] = ParagraphStyle('body_left', parent=base,
        alignment=TA_LEFT)

    s['body_center'] = ParagraphStyle('body_center', parent=base,
        alignment=TA_CENTER)

    s['h1'] = ParagraphStyle('h1', parent=base,
        fontName='Times-Bold', fontSize=16, leading=20,
        spaceBefore=18, spaceAfter=10, alignment=TA_LEFT)

    s['h2'] = ParagraphStyle('h2', parent=base,
        fontName='Times-Bold', fontSize=13, leading=17,
        spaceBefore=12, spaceAfter=6, alignment=TA_LEFT)

    s['h3'] = ParagraphStyle('h3', parent=base,
        fontName='Times-Bold', fontSize=11, leading=14,
        spaceBefore=8, spaceAfter=4, alignment=TA_LEFT)

    s['caption'] = ParagraphStyle('caption', parent=base,
        fontName='Times-Bold', fontSize=9.5, leading=12,
        alignment=TA_CENTER, spaceBefore=4, spaceAfter=14)

    s['bullet'] = ParagraphStyle('bullet', parent=base,
        leftIndent=16, firstLineIndent=-10, spaceAfter=4,
        alignment=TA_JUSTIFY)

    s['ref'] = ParagraphStyle('ref', parent=base,
        leftIndent=24, firstLineIndent=-24, spaceAfter=5,
        alignment=TA_JUSTIFY)

    s['toc_bold'] = ParagraphStyle('toc_bold', parent=base,
        fontName='Times-Bold', fontSize=11, leading=13,
        alignment=TA_LEFT, spaceAfter=2)

    s['toc_normal'] = ParagraphStyle('toc_normal', parent=base,
        fontName='Times-Roman', fontSize=11, leading=13,
        alignment=TA_LEFT, spaceAfter=2)

    s['cover_title'] = ParagraphStyle('cover_title', parent=base,
        fontName='Times-Bold', fontSize=22, leading=28,
        alignment=TA_CENTER, spaceAfter=6)

    s['cover_body'] = ParagraphStyle('cover_body', parent=base,
        fontName='Times-Roman', fontSize=10.5, leading=14,
        alignment=TA_CENTER, spaceAfter=4)

    s['cover_bold'] = ParagraphStyle('cover_bold', parent=base,
        fontName='Times-Bold', fontSize=11, leading=14,
        alignment=TA_CENTER, spaceAfter=4)

    s['appx_field'] = ParagraphStyle('appx_field', parent=base,
        fontName='Times-Roman', fontSize=11, leading=22,
        alignment=TA_LEFT, spaceAfter=0)

    return s


# ─────────────────────────────────────────────────────────────────────────────
# TOC HELPER  — two-column table: text | page num, left-aligned, no justify
# ─────────────────────────────────────────────────────────────────────────────
def toc_row(title, page, bold=False, indent=0, s=None):
    fn = 'Times-Bold' if bold else 'Times-Roman'
    left_style = ParagraphStyle('tl', fontName=fn, fontSize=11, leading=13,
                                 alignment=TA_LEFT, leftIndent=indent)
    right_style = ParagraphStyle('tr', fontName=fn, fontSize=11, leading=13,
                                  alignment=TA_RIGHT)
    # Build dot leader manually
    dots = "." * 55
    left_cell = Paragraph(f"{title}", left_style)
    right_cell = Paragraph(page, right_style)
    row = [[left_cell, Paragraph(dots, ParagraphStyle('dots', fontName='Times-Roman', fontSize=9, leading=13, alignment=TA_CENTER)), right_cell]]
    t = Table(row, colWidths=[BODY_W * 0.60, BODY_W * 0.28, BODY_W * 0.12])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    return t


# ─────────────────────────────────────────────────────────────────────────────
# APPENDIX A helper — two-column: label | dotted line
# ─────────────────────────────────────────────────────────────────────────────
def appx_a_field(label, filled="", s=None):
    """One row: label on left, dotted line on right"""
    label_p = Paragraph(label, ParagraphStyle('al', fontName='Times-Roman', fontSize=11, leading=22, alignment=TA_LEFT))
    dot_p = Paragraph(filled if filled else "…………………………………………", ParagraphStyle('ad', fontName='Times-Roman', fontSize=11, leading=22, alignment=TA_LEFT))
    row = [[label_p, dot_p]]
    t = Table(row, colWidths=[BODY_W * 0.42, BODY_W * 0.58])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    return t


# ─────────────────────────────────────────────────────────────────────────────
# TABLE HELPER
# ─────────────────────────────────────────────────────────────────────────────
def make_table(data, col_widths, header_row=True):
    t = Table(data, colWidths=col_widths)
    style = [
        ('GRID', (0, 0), (-1, -1), 0.5, black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]
    if header_row:
        style.append(('BACKGROUND', (0, 0), (-1, 0), '#e0e0e0'))
    t.setStyle(TableStyle(style))
    return t


# ─────────────────────────────────────────────────────────────────────────────
# MAIN REPORT BUILDER
# ─────────────────────────────────────────────────────────────────────────────
def build_report():
    pdf_path = "Report/Capstone_Project_Report.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=LM, rightMargin=RM,
        topMargin=TM + 8 * mm,   # extra for header
        bottomMargin=BM + 8 * mm  # extra for footer
    )
    S = make_styles()
    story = []

    def bp(s=None):
        story.append(PageBreak())

    def sp(h=6):
        story.append(Spacer(1, h))

    def h1(text):
        story.append(Paragraph(text, S['h1']))

    def h2(text):
        story.append(Paragraph(text, S['h2']))

    def h3(text):
        story.append(Paragraph(text, S['h3']))

    def body(text):
        story.append(Paragraph(text, S['body']))

    def body_left(text):
        story.append(Paragraph(text, S['body_left']))

    def caption(text):
        story.append(Paragraph(text, S['caption']))

    def bullet(text):
        story.append(Paragraph(f"• {text}", S['bullet']))

    def hr():
        story.append(HRFlowable(width=BODY_W, thickness=0.8, color=black, spaceBefore=4, spaceAfter=4))

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE 1 – COVER PAGE
    # ─────────────────────────────────────────────────────────────────────────
    story.append(Paragraph("Sabaragamuwa University of Sri Lanka", S['cover_title']))
    story.append(Spacer(1, 4))
    hr()
    story.append(Spacer(1, 8))

    if os.path.exists("Report/Screenshot 2026-08-29 095328.png"):
        story.append(Image("Report/Screenshot 2026-08-29 095328.png",
                           width=1.9 * inch, height=1.9 * inch,
                           hAlign='CENTER'))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "REAL-TIME FACIAL EMOTION RECOGNITION USING MEDIAPIPE<br/>"
        "AND DEEP CONVOLUTIONAL NEURAL NETWORKS WITH FOCAL LOSS",
        ParagraphStyle('ctitle2', fontName='Times-Bold', fontSize=14, leading=18,
                       alignment=TA_CENTER, spaceAfter=4, textColor=black)))
    sp(6)

    story.append(Paragraph(
        "<i>A Project Report submitted to the Faculty of Computing, Sabaragamuwa University of "
        "Sri Lanka, in partial fulfillment of the requirements for the Degree of "
        "Bachelor of Science Honours in Data Science.</i>",
        ParagraphStyle('csub', fontName='Times-Italic', fontSize=10.5, leading=14,
                       alignment=TA_CENTER, spaceAfter=10, textColor=black)))
    sp(14)

    # Cover info block
    cover_info = [
        ["Student Name",   "Harol Maxilan"],
        ["Index Number",   "22CDS0439"],
        ["Supervisor",     "Mr. Dimuthu Lakshan"],
    ]
    for label, val in cover_info:
        row_t = Table(
            [[Paragraph(f"<b>{label}</b>", S['body_left']),
              Paragraph(f"<b>:   {val}</b>", S['body_left'])]],
            colWidths=[BODY_W * 0.38, BODY_W * 0.62]
        )
        row_t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('LINEBELOW', (0,0), (-1,-1), 0.4, black),
        ]))
        story.append(row_t)
        sp(2)

    sp(18)
    story.append(Paragraph(
        "<b>DEPARTMENT OF DATA SCIENCE<br/>FACULTY OF COMPUTING</b>",
        ParagraphStyle('cdept', fontName='Times-Bold', fontSize=11.5, leading=16,
                       alignment=TA_CENTER, spaceAfter=6, textColor=black)))
    story.append(Paragraph(
        "September 2026",
        ParagraphStyle('cdate', fontName='Times-Roman', fontSize=11,
                       alignment=TA_CENTER, spaceAfter=8, textColor=black)))
    hr()
    bp()

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE 2 – APPENDIX A: DECLARATION
    # ─────────────────────────────────────────────────────────────────────────
    story.append(Paragraph("<b>Appendix A – Declaration</b>",
                           ParagraphStyle('appxtitle', fontName='Times-Bold', fontSize=14,
                                          leading=18, alignment=TA_CENTER,
                                          spaceAfter=20, textColor=black)))
    body(
        "I declare that this report does not incorporate, without acknowledgment, any "
        "material previously submitted for a Degree or a Diploma in any University, and to "
        "the best of our knowledge and belief, it does not contain any material previously "
        "published or written by another person or ourself except where due reference is "
        "made in the text. Also, I hereby grant Sabaragamuwa University of Sri Lanka the "
        "non-exclusive right to reproduce and distribute my report, in whole or in part, in "
        "print, electronic, or other media. I retain the right to use this content in whole "
        "or in part in future works (such as articles or books)."
    )
    sp(30)

    # Appendix A fields — label left, dotted line right (matches template image)
    for label, filled in [
        ("Index Number",        "22CDS0439"),
        ("Name of Student",     "Harol Maxilan"),
        ("Date",                "28/09/2026"),
        ("Signature of Student","…………………………………………"),
    ]:
        story.append(appx_a_field(label, filled, S))
        sp(4)

    bp()

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE 3 – APPENDIX B: CERTIFICATE OF APPROVAL
    # ─────────────────────────────────────────────────────────────────────────
    story.append(Paragraph("<b>Appendix B – Certificate of Approval</b>",
                           ParagraphStyle('appxtitle', fontName='Times-Bold', fontSize=14,
                                          leading=18, alignment=TA_CENTER,
                                          spaceAfter=14, textColor=black)))
    body(
        "We hereby declare that this report is the student's own work and effort, and that all "
        "other sources of information used have been acknowledged. This report has been "
        "submitted with our approval."
    )
    sp(18)

    # Internal Supervisor block
    def appx_b_person(name_label, name_value, sig_label):
        story.append(Paragraph(f"{name_label}", S['body_left']))
        story.append(Paragraph(f"<b>{name_value}</b>", S['body_left']))
        sp(18)
        sig_row = Table(
            [[Paragraph("…………………………………………", S['body_left']),
              Paragraph("…………………………………………", S['body_left'])]],
            colWidths=[BODY_W * 0.50, BODY_W * 0.50]
        )
        sig_row.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(sig_row)
        sig_lbl_row = Table(
            [[Paragraph("", S['body_left']),
              Paragraph(sig_label, S['body_left'])]],
            colWidths=[BODY_W * 0.50, BODY_W * 0.50]
        )
        sig_lbl_row.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(sig_lbl_row)
        sp(4)
        story.append(Paragraph("Date:  …………………………………", S['body_left']))
        sp(18)

    appx_b_person("Name of Internal Supervisor:", "Mr. Dimuthu Lakshan", "Signature of Internal Supervisor")
    appx_b_person("Name of Internal Co-Supervisor:", "N/A", "Signature of Internal Co-Supervisor")

    # Head of Department block
    story.append(Paragraph("Name of Head of the Department:", S['body_left']))
    story.append(Paragraph("<b>Dr. UAP Ishanka</b>", S['body_left']))
    sp(18)
    sig_row_hod = Table(
        [[Paragraph("…………………………………………", S['body_left']),
          Paragraph("…………………………………………", S['body_left'])]],
        colWidths=[BODY_W * 0.50, BODY_W * 0.50]
    )
    sig_row_hod.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(sig_row_hod)
    sig_lbl_hod = Table(
        [[Paragraph("", S['body_left']),
          Paragraph("Signature of Head of the Department", S['body_left'])]],
        colWidths=[BODY_W * 0.50, BODY_W * 0.50]
    )
    sig_lbl_hod.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(sig_lbl_hod)
    sp(4)
    story.append(Paragraph("Date:  …………………………………", S['body_left']))
    bp()

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE 4 – ACKNOWLEDGMENTS
    # ─────────────────────────────────────────────────────────────────────────
    h1("Acknowledgments")
    body(
        "The successful completion of this capstone project requires the contribution and "
        "support of several individuals. I wish to express my deepest gratitude to my "
        "internal supervisor, Mr. Dimuthu Lakshan, for the invaluable guidance, constructive "
        "criticism, and continuous encouragement provided throughout the course of this "
        "research. Your expertise and dedication were crucial in shaping this project from its "
        "inception to its final submission."
    )
    body(
        "I am profoundly grateful to Dr. UAP Ishanka, Head of the Department of Data Science, "
        "and to all the academic and non-academic staff of the Faculty of Computing, "
        "Sabaragamuwa University of Sri Lanka, for providing the necessary computational "
        "facilities, academic resources, and a highly supportive learning environment."
    )
    body(
        "I also wish to acknowledge the creators of the FER2013 dataset and the open-source "
        "contributions from the TensorFlow, MediaPipe, and OpenCV communities, whose tools "
        "formed the backbone of the technical implementation in this project."
    )
    body(
        "Finally, I acknowledge the unwavering support of my family and colleagues, whose "
        "encouragement helped sustain my motivation and focus during this intensive period "
        "of research and development."
    )
    bp()

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE 5 – ABSTRACT
    # ─────────────────────────────────────────────────────────────────────────
    h1("Abstract")
    body(
        "This capstone project addresses a significant challenge in automated Computer Vision "
        "and Affective Computing: the real-time, robust recognition of human facial expressions "
        "under variable lighting, head poses, and severe dataset class imbalance. The purpose "
        "of this study is to design, train, and deploy an end-to-end facial emotion recognition "
        "system capable of classifying live webcam frames into seven discrete emotional "
        "categories: Angry, Disgust, Fear, Happy, Sad, Surprise, and Neutral."
    )
    body(
        "The methodology employs Google MediaPipe BlazeFace for high-accuracy face bounding box "
        "detection, a customised 4-Stage Deep Convolutional Neural Network (CNN) incorporating "
        "Batch Normalization and L2 regularisation, and a novel Categorical Focal Loss "
        "formulation (γ = 2.0) combined with Label Smoothing (ε = 0.1) to mitigate severe "
        "minority-class underrepresentation in the FER2013 benchmark dataset (particularly "
        "for Disgust with only 436 training samples versus 7,215 Happy samples)."
    )
    body(
        "Key results indicate that the proposed system achieves a benchmark test accuracy of "
        "63.51% and a weighted F1-score of 62.91% across 7,178 unseen FER2013 test images, "
        "closely approaching the established human baseline accuracy of approximately 65%. "
        "The system demonstrates real-time inference capability through a 10-frame temporal "
        "prediction smoothing buffer that eliminates frame-to-frame prediction flickering "
        "during live webcam deployment."
    )
    body(
        "Based on these findings, the primary recommendation involves deploying the model "
        "within interactive human-computer interaction frameworks. Future enhancement "
        "directions include pretrained face-specific encoders (VGGFace2, AffectNet), Vision "
        "Transformer architectures, and multimodal fusion with speech audio emotion analysis. "
        "The conclusion is that the proposed solution effectively meets all stated objectives, "
        "offering a robust and validated framework for automated Emotion AI applications."
    )
    bp()

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE 6 – TABLE OF CONTENTS
    # ─────────────────────────────────────────────────────────────────────────
    h1("Table of Contents")
    sp(6)

    toc_entries = [
        ("Declaration (Appendix A)",                          "i",   True,  0),
        ("Certificate of Approval (Appendix B)",              "i",   True,  0),
        ("Acknowledgments",                                   "ii",  True,  0),
        ("Abstract",                                          "iii", True,  0),
        ("Table of Contents",                                 "iv",  True,  0),
        ("List of Figures",                                   "v",   True,  0),
        ("List of Tables",                                    "v",   True,  0),
        ("Chapter 1: Introduction",                           "1",   True,  0),
        ("1.1  Major Goals and Objectives",                   "1",   False, 12),
        ("1.2  Motivation",                                   "2",   False, 12),
        ("1.3  Scope of the Completed Project",               "2",   False, 12),
        ("1.4  Approach and Assumptions",                     "3",   False, 12),
        ("1.5  Summary of Major Outcomes",                    "3",   False, 12),
        ("Chapter 2: Background",                             "4",   True,  0),
        ("2.1  Problem Statement and Context",                "4",   False, 12),
        ("2.2  Evolution of Facial Emotion Recognition",      "5",   False, 12),
        ("2.3  FER2013 Benchmark Analysis",                   "5",   False, 12),
        ("2.4  Face Detection: Haar Cascades vs MediaPipe",  "6",   False, 12),
        ("2.5  Loss Function Innovations",                    "7",   False, 12),
        ("Chapter 3: Specification and Design",               "8",   True,  0),
        ("3.1  System Requirements",                          "8",   False, 12),
        ("3.2  Use Case Diagram & Specifications",            "9",   False, 12),
        ("3.3  System Architecture",                          "9",   False, 12),
        ("3.4  Sequence Diagram",                             "10",  False, 12),
        ("Chapter 4: Methodology",                            "11",  True,  0),
        ("4.1  Development Approach",                         "11",  False, 12),
        ("4.2  Dataset Description and Analysis",             "11",  False, 12),
        ("4.3  Data Preprocessing Pipeline",                  "12",  False, 12),
        ("4.4  Data Augmentation Strategy",                   "12",  False, 12),
        ("4.5  Class Imbalance Mitigation",                   "13",  False, 12),
        ("4.6  Focal Loss with Label Smoothing",              "13",  False, 12),
        ("4.7  Model Architecture Design",                    "14",  False, 12),
        ("4.8  Training Configuration and Hyperparameters",   "15",  False, 12),
        ("4.9  Real-Time Inference Pipeline",                 "15",  False, 12),
        ("Chapter 5: Results and Evaluation",                 "16",  True,  0),
        ("5.1  Experimental Setup",                           "16",  False, 12),
        ("5.2  Overall Classification Performance",           "16",  False, 12),
        ("5.3  Per-Class Classification Report",              "17",  False, 12),
        ("5.4  Confusion Matrix Analysis",                    "17",  False, 12),
        ("5.5  Real-Time Latency and FPS Performance",        "18",  False, 12),
        ("Chapter 6: Future Work",                            "19",  True,  0),
        ("Chapter 7: Conclusions",                            "19",  True,  0),
        ("References",                                        "20",  True,  0),
        ("Appendices",                                        "21",  True,  0),
    ]

    for title, page, bold, indent in toc_entries:
        story.append(toc_row(title, page, bold, indent, S))

    bp()

    # ─────────────────────────────────────────────────────────────────────────
    # LIST OF FIGURES & TABLES
    # ─────────────────────────────────────────────────────────────────────────
    h1("List of Figures")
    sp(4)
    for fig, page in [
        ("Figure 2.1: FER2013 Dataset Class Distribution (Train vs Test Set)", "5"),
        ("Figure 3.1: Real-Time Emotion AI Use Case Diagram",                  "9"),
        ("Figure 3.2: System Architecture and Real-Time Processing Pipeline",  "9"),
        ("Figure 3.3: System Sequence Diagram for Real-Time Detection",        "10"),
        ("Figure 5.1: Grayscale Confusion Matrix Heatmap (7,178 Test Images)", "17"),
        ("Figure 5.2: Per-Class F1-Score Performance Comparison",              "17"),
    ]:
        story.append(toc_row(fig, page, bold=False, indent=0, s=S))

    sp(12)
    h1("List of Tables")
    sp(4)
    for tab, page in [
        ("Table 3.1: Hardware and Software System Specifications",          "8"),
        ("Table 4.1: Upgraded 4-Stage ConvNet Architecture Details",        "14"),
        ("Table 5.1: Overall Classification Performance Comparison",        "16"),
        ("Table 5.2: Detailed Classification Report per Emotion Class",     "17"),
    ]:
        story.append(toc_row(tab, page, bold=False, indent=0, s=S))

    bp()

    # ─────────────────────────────────────────────────────────────────────────
    # CHAPTER 1: INTRODUCTION
    # ─────────────────────────────────────────────────────────────────────────
    h1("Chapter 1: Introduction")
    body(
        "Facial expressions constitute one of the primary non-verbal communication channels "
        "used by humans to convey emotions, intentions, and psychological states. Automated "
        "Facial Emotion Recognition (FER) has emerged as a pivotal domain within Artificial "
        "Intelligence and Computer Vision, with transformative applications in adaptive "
        "learning systems, mental health diagnostics, driver drowsiness monitoring, customer "
        "experience feedback, and human-robot interaction. The ability to interpret facial "
        "affect in real-time from live video streams presents both significant technical "
        "challenges and substantial socioeconomic opportunities."
    )

    h2("1.1  Major Goals and Objectives")
    body("The primary goal of this capstone project is to develop, evaluate, and deploy a "
         "robust, end-to-end real-time facial emotion recognition system that operates "
         "efficiently on consumer-grade hardware. The specific objectives are:")
    for o in [
        "To construct an optimised 4-Stage Deep Convolutional Neural Network (CNN) capable "
        "of accurately classifying 7 discrete FER2013 emotion categories.",
        "To address severe dataset class imbalance in FER2013 by formulating a Categorical "
        "Focal Loss function (γ = 2.0) combined with Label Smoothing (ε = 0.1) and dynamic "
        "class weighting.",
        "To integrate Google MediaPipe BlazeFace for robust face bounding box extraction "
        "under varying illumination and head rotations.",
        "To implement a 10-frame temporal prediction smoothing buffer (majority vote) to "
        "eliminate high-frequency prediction flickering during live webcam inference.",
        "To conduct rigorous experimental evaluation on 7,178 test images analysing accuracy, "
        "precision, recall, F1-scores, and confusion matrices.",
    ]:
        bullet(o)

    h2("1.2  Motivation")
    body(
        "Traditional facial expression recognition approaches relied on hand-crafted feature "
        "extraction such as Local Binary Patterns (LBP) or Histogram of Oriented Gradients "
        "(HOG) combined with Support Vector Machines (SVM). These methods suffer from "
        "limited generalisation under real-world occlusions, lighting fluctuations, and "
        "unconstrained head poses. Modern Deep Learning approaches have achieved "
        "state-of-the-art results, but the widely used FER2013 benchmark dataset presents "
        "severe class imbalance: Disgust contains only 436 training samples versus 7,215 "
        "Happy samples, causing standard cross-entropy trained networks to over-predict "
        "majority classes. This project is motivated by the need to develop an algorithmic "
        "pipeline that directly mitigates class imbalance while maintaining high inference "
        "speed for real-time deployment."
    )

    h2("1.3  Scope of the Completed Project")
    body(
        "The scope of this project encompasses: data preprocessing of the FER2013 dataset "
        "(28,709 training and 7,178 test images), mathematical formulation of Focal Loss and "
        "Label Smoothing, design and training of a 4-Stage Deep ConvNet, development of a "
        "MediaPipe-driven live webcam capture interface with temporal smoothing, and empirical "
        "benchmark evaluation. The system is designed for deployment on both Windows (via "
        "venv_win) and Linux/WSL (via GPU-accelerated venv) environments."
    )

    h2("1.4  Approach and Assumptions")
    body(
        "The technical approach assumes that input video frames are captured via a standard "
        "720p webcam and that at least one primary human face is visible within the camera "
        "field of view. Face detection is delegated to MediaPipe's lightweight BlazeFace "
        "single-shot detector. Cropped face regions of interest (ROI) are converted to "
        "48×48 pixel normalised grayscale tensors [0, 1] before feeding into the neural "
        "network classifier. The system is evaluated under natural indoor lighting conditions."
    )

    h2("1.5  Summary of Major Outcomes")
    body(
        "The major outcomes of this project include: (1) achieving a benchmark test accuracy "
        "of 63.51% and weighted F1-score of 62.91% on the FER2013 test set; (2) successfully "
        "suppressing prediction flickering via a 10-frame deque temporal buffer; (3) deploying "
        "a single-click Windows batch launcher (run_webcam.bat) for seamless execution; and "
        "(4) producing a comprehensive evaluation report including per-class precision, recall, "
        "F1-scores, and a confusion matrix heatmap."
    )
    bp()

    # ─────────────────────────────────────────────────────────────────────────
    # CHAPTER 2: BACKGROUND
    # ─────────────────────────────────────────────────────────────────────────
    h1("Chapter 2: Background")
    body(
        "This chapter reviews the theoretical foundation, historical evolution, and "
        "state-of-the-art developments in Facial Emotion Recognition. It analyses challenges "
        "of the FER2013 dataset, compares traditional and modern face detection techniques, "
        "and discusses loss function innovations for class-imbalanced datasets."
    )

    h2("2.1  Problem Statement and Context")
    body(
        "Automated recognition of human facial affect in unconstrained real-world environments "
        "is challenged by three compounding factors. First, intra-class variance: different "
        "individuals express the same emotion with distinctly different intensities and muscle "
        "activation patterns. Second, inter-class similarity: emotions such as Fear and "
        "Surprise, or Sad and Neutral, share overlapping facial muscle movements (Action "
        "Units). Third, dataset class imbalance: FER2013's Disgust class contains 18.4x fewer "
        "samples than Happy, causing standard cross-entropy models to produce systematically "
        "biased classification boundaries favouring majority classes."
    )

    h2("2.2  Evolution of Facial Emotion Recognition")
    body(
        "Early FER systems (1990s–2010s) relied on geometric-based or appearance-based "
        "hand-crafted features (LBP, HOG, Gabor wavelets) combined with classical "
        "classifiers (SVM, k-NN, Random Forests). The introduction of deep learning "
        "fundamentally transformed FER: Goodfellow et al. (2013) established FER2013 as "
        "a benchmark via the ICML Challenges in Representation Learning competition. "
        "Modern architectures including VGGNet, ResNet, and EfficientNet achieve top-1 "
        "accuracies between 63–73% on FER2013. The human baseline accuracy for FER2013 "
        "is approximately 65%, indicating the inherent difficulty of the dataset due to "
        "label noise and subjective annotation."
    )

    h2("2.3  FER2013 Benchmark Analysis")
    body(
        "The FER2013 dataset contains 35,887 grayscale images of 48×48 pixels, partitioned "
        "into 28,709 training images and 7,178 test images across seven emotion categories. "
        "Figure 2.1 illustrates the severe class imbalance, with Happy and Neutral dominating "
        "training distribution while Disgust represents less than 1.5% of all samples."
    )
    if os.path.exists("Report/figures/figure_dataset_distribution.png"):
        sp(4)
        story.append(Image("Report/figures/figure_dataset_distribution.png",
                           width=BODY_W, height=BODY_W * 0.63, hAlign='CENTER'))
        caption("Figure 2.1: FER2013 Dataset Class Distribution (Train vs Test Set)")

    h2("2.4  Face Detection: Haar Cascades vs Google MediaPipe")
    body(
        "Traditional OpenCV implementations relied on Viola-Jones Haar Feature-based Cascade "
        "Classifiers, which operate via sliding window detection across image pyramids. While "
        "computationally fast on frontal faces, Haar Cascades suffer from elevated false "
        "positive rates, pronounced sensitivity to lighting gradients, and failure under "
        "non-frontal head poses exceeding ±30°. In contrast, Google MediaPipe's BlazeFace "
        "employs a single-shot multi-scale detector trained on large-scale face datasets, "
        "providing stable bounding boxes under variable illumination, moderate head rotations, "
        "and partial occlusions at 30 FPS on standard hardware."
    )

    h2("2.5  Loss Function Innovations: Focal Loss vs Cross-Entropy")
    body(
        "Standard Categorical Cross-Entropy (CCE) loss uniformly penalises all misclassified "
        "samples regardless of prediction confidence. In imbalanced datasets, this causes the "
        "gradient signal to be dominated by the easily classified majority class (Happy), "
        "suppressing minority class learning:"
    )
    body("CCE = −∑ y_c · log(ŷ_c)  for all classes c = 1 … C")
    body(
        "Lin et al. (2017) introduced Focal Loss, which adds a modulating factor "
        "(1 − p_t)^γ to dynamically downweight well-classified examples, focusing "
        "training gradient on hard and underrepresented examples:"
    )
    body("FL(p_t) = −α_t (1 − p_t)^γ · log(p_t)")
    body(
        "In this project, γ = 2.0 is applied with Label Smoothing (ε = 0.1), which "
        "softens hard one-hot targets [1, 0, 0 …] to [1 − ε + ε/K, ε/K, ε/K …], "
        "mitigating mislabelled noise in FER2013 and preventing overconfident softmax outputs."
    )
    bp()

    # ─────────────────────────────────────────────────────────────────────────
    # CHAPTER 3: SPECIFICATION AND DESIGN
    # ─────────────────────────────────────────────────────────────────────────
    h1("Chapter 3: Specification and Design")
    body(
        "This chapter presents the formal specifications, architectural designs, use case "
        "modelling, and behavioral diagrams for the real-time facial emotion recognition system."
    )

    h2("3.1  System Requirements")
    body("Table 3.1 specifies the hardware and software requirements for full system deployment.")
    sp(4)
    req_data = [
        [Paragraph("<b>Category</b>", S['body_left']),
         Paragraph("<b>Details</b>", S['body_left']),
         Paragraph("<b>Minimum</b>", S['body_left'])],
        [Paragraph("Operating System", S['body_left']),
         Paragraph("Windows 10/11 (64-bit) or Ubuntu 20.04 LTS via WSL2", S['body_left']),
         Paragraph("Windows 10", S['body_left'])],
        [Paragraph("Python", S['body_left']),
         Paragraph("Python 3.10.x with virtualenv (venv_win)", S['body_left']),
         Paragraph("Python 3.10", S['body_left'])],
        [Paragraph("ML Libraries", S['body_left']),
         Paragraph("TensorFlow 2.15.0, MediaPipe 0.10.9, OpenCV 4.8.0, NumPy 1.26.4", S['body_left']),
         Paragraph("TF 2.15", S['body_left'])],
        [Paragraph("Camera", S['body_left']),
         Paragraph("USB Webcam / Integrated Camera (720p @ 30 FPS)", S['body_left']),
         Paragraph("720p Webcam", S['body_left'])],
    ]
    story.append(make_table(req_data, [BODY_W*0.18, BODY_W*0.54, BODY_W*0.28]))
    caption("Table 3.1: Hardware and Software System Specifications")

    h2("3.2  Use Case Diagram and Specifications")
    body(
        "Figure 3.1 illustrates the Use Case diagram identifying interactions between the "
        "User and the Real-Time Emotion AI System. Five primary use cases are identified: "
        "UC-1 Live Video Capture, UC-2 Face Detection, UC-3 Preprocessing, "
        "UC-4 Emotion Classification, and UC-5 Temporal Prediction Smoothing."
    )
    if os.path.exists("Report/figures/figure_use_case_diagram.png"):
        sp(4)
        story.append(Image("Report/figures/figure_use_case_diagram.png",
                           width=BODY_W, height=BODY_W * 0.60, hAlign='CENTER'))
        caption("Figure 3.1: Real-Time Emotion AI Use Case Diagram")

    h2("3.3  System Architecture")
    body(
        "Figure 3.2 depicts the high-level system architecture showing the five-stage "
        "processing pipeline: webcam input → MediaPipe face detection → ROI preprocessing "
        "→ 4-Stage CNN classification → temporal smoothing and display overlay."
    )
    if os.path.exists("Report/figures/figure_system_architecture.png"):
        sp(4)
        story.append(Image("Report/figures/figure_system_architecture.png",
                           width=BODY_W, height=BODY_W * 0.52, hAlign='CENTER'))
        caption("Figure 3.2: System Architecture and Real-Time Processing Pipeline")

    h2("3.4  Sequence Diagram")
    body(
        "Figure 3.3 illustrates the sequential message flow between system components: "
        "User triggers the application, Camera Feed provides RGB frames, MediaPipe detects "
        "face bounding boxes, the 4-Stage CNN computes softmax probabilities, the deque "
        "buffer performs majority vote, and the Display UI renders the annotation overlay."
    )
    if os.path.exists("Report/figures/figure_sequence_diagram.png"):
        sp(4)
        story.append(Image("Report/figures/figure_sequence_diagram.png",
                           width=BODY_W, height=BODY_W * 0.62, hAlign='CENTER'))
        caption("Figure 3.3: System Sequence Diagram for Real-Time Detection")
    bp()

    # ─────────────────────────────────────────────────────────────────────────
    # CHAPTER 4: METHODOLOGY
    # ─────────────────────────────────────────────────────────────────────────
    h1("Chapter 4: Methodology")
    body(
        "This chapter provides a detailed account of the development approach, dataset "
        "characteristics, preprocessing pipeline, data augmentation strategy, class "
        "imbalance mitigation, loss function formulation, network architecture design "
        "decisions, training configuration, and the real-time inference pipeline deployed "
        "in this project."
    )

    h2("4.1  Development Approach")
    body(
        "An iterative, agile-inspired development methodology was adopted for this project. "
        "The work was structured across four iterative cycles: (1) Dataset exploration and "
        "baseline model establishment; (2) Architecture upgrade and Focal Loss integration; "
        "(3) MediaPipe integration and real-time pipeline development; and (4) Evaluation, "
        "refinement, and deployment. Each cycle incorporated feedback from benchmark evaluation "
        "results to guide subsequent architectural and training decisions. Version control was "
        "maintained via Git throughout the development lifecycle."
    )

    h2("4.2  Dataset Description and Analysis")
    body(
        "The FER2013 (Facial Emotion Recognition 2013) dataset was used exclusively for "
        "training and evaluation. It was sourced from the ICML 2013 Challenges in "
        "Representation Learning workshop. The dataset comprises 35,887 grayscale facial "
        "images, each of dimensions 48×48 pixels, partitioned into 28,709 training and "
        "7,178 test images. Images were sourced from internet search engines using emotion "
        "keyword queries and were automatically annotated, introducing significant labelling "
        "noise and subjectivity, contributing to the dataset's high difficulty."
    )
    body(
        "Class distribution analysis revealed extreme imbalance: the Disgust class contains "
        "only 436 training samples (1.52% of training data), while Happy contains 7,215 "
        "samples (25.13%). This 16.5:1 imbalance ratio necessitated specialised loss "
        "function design and class weighting strategies."
    )

    h2("4.3  Data Preprocessing Pipeline")
    body(
        "All image loading was implemented using TensorFlow's ImageDataGenerator with "
        "directory-based class labelling. The preprocessing pipeline applied the following "
        "transformations in sequence:"
    )
    for step in [
        "Grayscale conversion (color_mode='grayscale'): Images loaded as single-channel, "
        "consistent with the original FER2013 grayscale encoding.",
        "Pixel normalisation: Each pixel value divided by 255.0, mapping the integer range "
        "[0, 255] to floating-point [0.0, 1.0].",
        "Tensor reshaping: Each image reshaped to (48, 48, 1) — height, width, channels — "
        "matching the CNN input specification.",
        "Stratified 85%/15% train/validation split: Applied via validation_split=0.15 in "
        "ImageDataGenerator to maintain class proportion in both splits.",
    ]:
        bullet(step)

    h2("4.4  Data Augmentation Strategy")
    body(
        "On-the-fly augmentation was applied exclusively to training data to artificially "
        "expand the effective dataset size and improve generalisation. Augmentation parameters "
        "were carefully tuned to preserve the semantic content of facial expressions:"
    )
    aug_data = [
        [Paragraph("<b>Augmentation Technique</b>", S['body_left']),
         Paragraph("<b>Parameter</b>", S['body_left']),
         Paragraph("<b>Rationale</b>", S['body_left'])],
        [Paragraph("Random Rotation", S['body_left']),
         Paragraph("±20°", S['body_left']),
         Paragraph("Simulates head tilts common in natural poses", S['body_left'])],
        [Paragraph("Width / Height Shift", S['body_left']),
         Paragraph("±15%", S['body_left']),
         Paragraph("Simulates off-centre face positioning in frame", S['body_left'])],
        [Paragraph("Zoom Range", S['body_left']),
         Paragraph("±15%", S['body_left']),
         Paragraph("Simulates variable distance from camera", S['body_left'])],
        [Paragraph("Brightness Range", S['body_left']),
         Paragraph("[0.8, 1.2]", S['body_left']),
         Paragraph("Simulates variable indoor/outdoor lighting", S['body_left'])],
        [Paragraph("Horizontal Flip", S['body_left']),
         Paragraph("Enabled", S['body_left']),
         Paragraph("Accounts for bilateral facial symmetry", S['body_left'])],
        [Paragraph("Shear Range", S['body_left']),
         Paragraph("0.15", S['body_left']),
         Paragraph("Introduces perspective variation", S['body_left'])],
    ]
    story.append(make_table(aug_data, [BODY_W*0.28, BODY_W*0.18, BODY_W*0.54]))
    caption("Data augmentation parameters applied during training")

    h2("4.5  Class Imbalance Mitigation")
    body(
        "Class imbalance was addressed through two complementary mechanisms:"
    )
    bullet(
        "Balanced Class Weights: Scikit-learn's compute_class_weight(class_weight='balanced') "
        "function was used to compute per-class weight multipliers inversely proportional to "
        "class frequency. These weights were passed as the class_weight argument to model.fit(), "
        "increasing the effective loss contribution of minority classes (e.g., Disgust "
        "weight ≈ 4.8) during backpropagation."
    )
    bullet(
        "Categorical Focal Loss: The Focal Loss formulation (described in Section 4.6) "
        "additionally downweights easy well-classified examples from majority classes, "
        "complementing the static class weight approach with dynamic, per-sample weighting."
    )

    h2("4.6  Focal Loss with Label Smoothing Formulation")
    body(
        "The custom Categorical Focal Loss was implemented as a TensorFlow/Keras loss "
        "function incorporating both Focal Loss modulation and Label Smoothing regularisation:"
    )
    body(
        "<b>Step 1 – Label Smoothing:</b> Hard one-hot targets y are smoothed by parameter "
        "ε = 0.1, distributing a fraction of probability mass uniformly across all K=7 classes:"
    )
    body("ỹ_c = y_c · (1 − ε) + ε / K")
    body(
        "<b>Step 2 – Clipping:</b> Predicted softmax probabilities ŷ are clipped to [10⁻⁷, "
        "1 − 10⁻⁷] to prevent numerical instability in log computation."
    )
    body(
        "<b>Step 3 – Focal Weighting:</b> The modulating factor (1 − ŷ_c)^γ is applied, "
        "where γ = 2.0. When ŷ_c → 1 (easy, confident correct prediction), the factor "
        "approaches 0, heavily downweighting that sample's gradient contribution:"
    )
    body("FL(ŷ_c) = − ỹ_c · (1 − ŷ_c)^γ · log(ŷ_c)")
    body(
        "<b>Step 4 – Reduction:</b> Loss values are summed across all K class dimensions "
        "and averaged across the batch dimension."
    )

    h2("4.7  Upgraded 4-Stage ConvNet Architecture")
    body(
        "The emotion classifier was redesigned from a 3-block baseline CNN to a 4-Stage "
        "deep architecture. The design rationale follows a progressive feature abstraction "
        "hierarchy, with each successive block operating on increasingly compact feature "
        "maps while doubling filter depth. Key architectural decisions include:"
    )
    for decision in [
        "Double Conv layers per block (VGGNet-inspired): Two consecutive Conv2D layers "
        "before pooling increase receptive field without premature spatial reduction.",
        "Batch Normalisation after each Conv2D: Normalises layer activations, stabilises "
        "gradient flow, and acts as an implicit regulariser, reducing dependency on Dropout.",
        "Global Average Pooling instead of Flatten: GAP computes the spatial average of "
        "each feature map, producing a 512-dimensional vector while drastically reducing "
        "parameters compared to Flatten, improving generalisation.",
        "L2 Regularisation (λ = 1e-4): Applied to all Conv2D and Dense kernel weights "
        "to penalise large weights and prevent co-adaptation of feature detectors.",
        "Progressive Dropout (0.25 → 0.30 → 0.35 → 0.40 → 0.50): Dropout rates increase "
        "with depth as later layers capture more abstract, overfitting-prone representations.",
    ]:
        bullet(decision)
    sp(4)
    arch_data = [
        [Paragraph("<b>Block</b>", S['body_left']),
         Paragraph("<b>Layers</b>", S['body_left']),
         Paragraph("<b>Output Shape</b>", S['body_left']),
         Paragraph("<b>Dropout</b>", S['body_left'])],
        [Paragraph("Block 1", S['body_left']),
         Paragraph("Conv2D(64)×2 + BN + MaxPool(2×2)", S['body_left']),
         Paragraph("24 × 24 × 64", S['body_left']),
         Paragraph("0.25", S['body_left'])],
        [Paragraph("Block 2", S['body_left']),
         Paragraph("Conv2D(128)×2 + BN + MaxPool(2×2)", S['body_left']),
         Paragraph("12 × 12 × 128", S['body_left']),
         Paragraph("0.30", S['body_left'])],
        [Paragraph("Block 3", S['body_left']),
         Paragraph("Conv2D(256)×2 + BN + MaxPool(2×2)", S['body_left']),
         Paragraph("6 × 6 × 256", S['body_left']),
         Paragraph("0.35", S['body_left'])],
        [Paragraph("Block 4", S['body_left']),
         Paragraph("Conv2D(512)×2 + BN + MaxPool(2×2)", S['body_left']),
         Paragraph("3 × 3 × 512", S['body_left']),
         Paragraph("0.40", S['body_left'])],
        [Paragraph("Head", S['body_left']),
         Paragraph("GAP + Dense(256) + BN + Dense(7, Softmax)", S['body_left']),
         Paragraph("(7,)", S['body_left']),
         Paragraph("0.50", S['body_left'])],
    ]
    story.append(make_table(arch_data, [BODY_W*0.14, BODY_W*0.46, BODY_W*0.22, BODY_W*0.18]))
    caption("Table 4.1: Upgraded 4-Stage ConvNet Architecture Details")

    h2("4.8  Training Configuration and Hyperparameters")
    body("The following training configuration was used:")
    for cfg in [
        "Optimiser: Adam (Adaptive Moment Estimation), initial learning rate = 1×10⁻³",
        "Batch size: 32 samples per gradient update step",
        "Maximum epochs: 60 with Early Stopping (patience = 12 epochs on val_accuracy)",
        "ReduceLROnPlateau: Learning rate halved when val_loss stagnates for 4 epochs, "
        "minimum lr = 1×10⁻⁷",
        "ModelCheckpoint: Best model weights saved based on peak validation accuracy",
        "Training duration: ~3–4 hours on NVIDIA GeForce RTX 2050 (4GB VRAM) via WSL2",
    ]:
        bullet(cfg)

    h2("4.9  Real-Time Inference Pipeline")
    body(
        "The live inference system integrates five components into a continuous video "
        "processing loop:"
    )
    for step in [
        "Frame Capture: OpenCV VideoCapture(0) reads 720p BGR frames at 30 FPS.",
        "Colour Conversion: BGR frame converted to RGB for MediaPipe compatibility.",
        "Face Detection: MediaPipe FaceDetection (model_selection=0, min_confidence=0.6) "
        "returns relative bounding box coordinates, converted to absolute pixel coordinates.",
        "ROI Preprocessing: Extracted face crop converted to grayscale, resized to 48×48, "
        "normalised to [0, 1], and reshaped to (1, 48, 48, 1) batch tensor.",
        "Temporal Smoothing: Raw argmax predictions stored in a collections.deque(maxlen=10) "
        "buffer. Counter(buffer).most_common(1)[0][0] computes the majority vote emotion "
        "label, which is rendered as a bounding box annotation on the display frame.",
    ]:
        bullet(step)
    bp()

    # ─────────────────────────────────────────────────────────────────────────
    # CHAPTER 5: RESULTS AND EVALUATION
    # ─────────────────────────────────────────────────────────────────────────
    h1("Chapter 5: Results and Evaluation")
    body(
        "This chapter presents quantitative evaluation results of the proposed 4-Stage "
        "ConvNet model across 7,178 unseen test images from the FER2013 test set. All "
        "evaluations were conducted on the full test partition with no data augmentation."
    )

    h2("5.1  Experimental Setup")
    body(
        "Evaluation was performed using evaluate_all.py, which loads trained model weights "
        "via model.load_weights() into the rebuilt architecture (avoiding Keras 3.x "
        "deserialization incompatibility), then evaluates on the FER2013 test set. "
        "Scikit-learn's classification_report() and confusion_matrix() functions were used "
        "to compute all per-class metrics."
    )

    h2("5.2  Overall Classification Performance")
    body("Table 5.1 compares performance of the proposed model against the baseline EfficientNetB0 transfer learning approach.")
    sp(4)
    res_data = [
        [Paragraph("<b>Model</b>", S['body_left']),
         Paragraph("<b>Input</b>", S['body_left']),
         Paragraph("<b>Test Loss</b>", S['body_left']),
         Paragraph("<b>Test Accuracy</b>", S['body_left'])],
        [Paragraph("<b>Upgraded 4-Stage ConvNet (Proposed)</b>", S['body_left']),
         Paragraph("48×48 Grayscale", S['body_left']),
         Paragraph("1.0011", S['body_left']),
         Paragraph("<b>63.51%</b>", S['body_left'])],
        [Paragraph("EfficientNetB0 Transfer Learning", S['body_left']),
         Paragraph("96×96 RGB", S['body_left']),
         Paragraph("1.4788", S['body_left']),
         Paragraph("43.90%", S['body_left'])],
    ]
    story.append(make_table(res_data, [BODY_W*0.38, BODY_W*0.22, BODY_W*0.18, BODY_W*0.22]))
    caption("Table 5.1: Overall Classification Performance Comparison")

    h2("5.3  Per-Class Classification Report")
    body("Table 5.2 presents precision, recall, F1-score, and support values per emotion class.")
    sp(4)
    cls_data = [
        [Paragraph("<b>Emotion</b>", S['body_left']),
         Paragraph("<b>Precision</b>", S['body_left']),
         Paragraph("<b>Recall</b>", S['body_left']),
         Paragraph("<b>F1-Score</b>", S['body_left']),
         Paragraph("<b>Support</b>", S['body_left'])],
        *[[Paragraph(e, S['body_left']), Paragraph(p, S['body_left']),
           Paragraph(r, S['body_left']), Paragraph(f, S['body_left']),
           Paragraph(sup, S['body_left'])]
          for e, p, r, f, sup in [
              ("Angry",   "53.71%", "60.44%", "56.88%", "958"),
              ("Disgust", "81.82%", "40.54%", "54.22%", "111"),
              ("Fear",    "50.79%", "34.67%", "41.21%", "1,024"),
              ("Happy",   "82.51%", "86.13%", "84.28%", "1,774"),
              ("Sad",     "55.46%", "67.96%", "61.08%", "1,233"),
              ("Surprise","50.72%", "47.71%", "49.17%", "1,247"),
              ("Neutral", "76.42%", "74.49%", "75.44%", "831"),
          ]],
        [Paragraph("<b>Weighted Avg</b>", S['body_left']),
         Paragraph("<b>63.26%</b>", S['body_left']),
         Paragraph("<b>63.51%</b>", S['body_left']),
         Paragraph("<b>62.91%</b>", S['body_left']),
         Paragraph("<b>7,178</b>", S['body_left'])],
    ]
    story.append(make_table(cls_data, [BODY_W*0.20, BODY_W*0.18, BODY_W*0.18, BODY_W*0.18, BODY_W*0.26]))
    caption("Table 5.2: Detailed Classification Report per Emotion Class")

    h2("5.4  Confusion Matrix Analysis")
    body(
        "Figure 5.1 presents the grayscale confusion matrix heatmap. Strong diagonal entries "
        "are observed for Happy (1,528/1,774 correct = 86.13%) and Neutral (619/831 = 74.49%). "
        "The highest confusion is between Fear–Surprise and Fear–Sad, reflecting the inter-class "
        "similarity problem. Disgust's low recall (40.54%) reflects the class imbalance challenge "
        "despite Focal Loss application."
    )
    if os.path.exists("Report/figures/figure_confusion_matrix.png"):
        sp(4)
        story.append(Image("Report/figures/figure_confusion_matrix.png",
                           width=BODY_W * 0.88, height=BODY_W * 0.75, hAlign='CENTER'))
        caption("Figure 5.1: Grayscale Confusion Matrix Heatmap on 7,178 Test Images")

    body(
        "Figure 5.2 shows the per-class F1-Score comparison, confirming that Happy and Neutral "
        "achieve the highest performance (84.28% and 75.44% respectively) while Fear achieves "
        "the lowest F1-Score (41.21%) due to high inter-class confusion with Surprise and Sad."
    )
    if os.path.exists("Report/figures/figure_f1_scores.png"):
        sp(4)
        story.append(Image("Report/figures/figure_f1_scores.png",
                           width=BODY_W * 0.85, height=BODY_W * 0.52, hAlign='CENTER'))
        caption("Figure 5.2: Per-Class F1-Score Performance Comparison")

    h2("5.5  Real-Time Latency and FPS Performance")
    body(
        "During live webcam deployment on the Windows environment (Intel Core i5, 16GB RAM, "
        "NVIDIA GeForce RTX 2050), the system sustains approximately 28–30 FPS processing "
        "throughput. MediaPipe face detection latency is approximately 3–5 ms per frame. "
        "CNN inference latency is approximately 12–18 ms per face crop on CPU (TensorFlow "
        "Intel-optimised). The 10-frame temporal smoothing buffer introduces a negligible "
        "latency of approximately 333 ms (10 frames × 1/30s) for stable emotion display."
    )
    bp()

    # ─────────────────────────────────────────────────────────────────────────
    # CHAPTER 6: FUTURE WORK
    # ─────────────────────────────────────────────────────────────────────────
    h1("Chapter 6: Future Work")
    body(
        "While the proposed system achieves performance approaching the human baseline, "
        "several limitations and enhancement opportunities have been identified:"
    )
    for fw in [
        "<b>Face-Specific Pretrained Encoders:</b> Replacing ImageNet-pretrained backbones "
        "with encoders pretrained on large-scale face datasets such as VGGFace2 (3.31M "
        "images) or AffectNet (1M images) would provide substantially more semantically "
        "relevant feature representations for facial Action Units.",
        "<b>Vision Transformer (ViT) Architectures:</b> Self-attention mechanisms in "
        "Vision Transformers can capture global facial structure relationships and "
        "micro-expression patterns that local convolutional filters miss.",
        "<b>Mixup and CutMix Data Augmentation:</b> Generating synthetic training samples "
        "by linearly interpolating between minority and majority class face images would "
        "directly address class imbalance at the data level.",
        "<b>Multimodal Emotion AI:</b> Fusing facial expression features with speech "
        "audio emotion analysis (mel-spectrogram CNNs or wav2vec models) and physiological "
        "signals (heart rate, EEG) would improve robustness.",
        "<b>AffectNet Pre-training:</b> Fine-tuning on AffectNet (8 emotion classes, "
        "natural face images) before FER2013 fine-tuning would provide superior weight "
        "initialisation, particularly for minority classes.",
    ]:
        bullet(fw)

    # ─────────────────────────────────────────────────────────────────────────
    # CHAPTER 7: CONCLUSIONS
    # ─────────────────────────────────────────────────────────────────────────
    h1("Chapter 7: Conclusions")
    body(
        "This project successfully designed, implemented, evaluated, and deployed a complete "
        "real-time facial emotion recognition system addressing the dual challenges of dataset "
        "class imbalance and live video inference performance."
    )
    body(
        "The core contributions of this work are: (1) formulation of a Categorical Focal "
        "Loss (γ = 2.0) with Label Smoothing (ε = 0.1) specifically addressing FER2013's "
        "severe class imbalance; (2) an upgraded 4-Stage Deep ConvNet architecture with "
        "double convolutional layers, Batch Normalization, L2 regularisation, and Global "
        "Average Pooling achieving 63.51% test accuracy; (3) integration of Google MediaPipe "
        "BlazeFace for robust real-time face detection; and (4) a 10-frame temporal "
        "smoothing buffer eliminating prediction flickering during live deployment."
    )
    body(
        "The system achieves 63.51% test accuracy and 62.91% weighted F1-score on 7,178 "
        "FER2013 test images, closely approaching the human annotation baseline of "
        "approximately 65%. The system meets all stated project objectives and provides "
        "a robust, validated, and deployable framework for real-time Affective Computing "
        "applications, with clear pathways for future enhancement through face-specific "
        "transfer learning and multimodal fusion."
    )
    bp()

    # ─────────────────────────────────────────────────────────────────────────
    # REFERENCES (IEEE Format)
    # ─────────────────────────────────────────────────────────────────────────
    h1("References")
    sp(4)
    refs = [
        '[1] I. J. Goodfellow, D. Erhan, P. L. Carrier, A. Courville, M. Mirza, B. Hamner, '
        'W. Cukierski, Y. Tang, D. Thaler, D. H. Lee, Y. Zhou, C. Ramaiah, F. Feng, R. Li, '
        'X. Wang, D. Athanasakis, J. Shawe-Taylor, M. Milakov, J. Park, R. Ionescu, '
        'M. Popescu, C. Grozea, J. Bergstra, J. Xie, L. Romaszko, B. Xu, Z. Chuang, and '
        'Y. Bengio, "Challenges in representation learning: A report on three machine '
        'learning contests," in <i>Proc. Int. Conf. Neural Inf. Process. (ICONIP)</i>, '
        'Springer, 2013, pp. 117–124.',

        '[2] T.-Y. Lin, P. Goyal, R. Girshick, K. He, and P. Dollár, "Focal loss for dense '
        'object detection," in <i>Proc. IEEE Int. Conf. Computer Vision (ICCV)</i>, '
        'Venice, Italy, 2017, pp. 2980–2988.',

        '[3] C. Lugaresi, J. Tang, H. Nash, C. McClanahan, E. Uboweja, M. Hays, F. Zhang, '
        'C.-L. Chang, M. G. Yong, J. Lee, W.-T. Chang, W. Hua, M. Georg, and M. Grundmann, '
        '"MediaPipe: A framework for building perception pipelines," <i>arXiv preprint '
        'arXiv:1906.08172</i>, Jun. 2019.',

        '[4] P. Viola and M. J. Jones, "Robust real-time face detection," '
        '<i>Int. J. Computer Vision</i>, vol. 57, no. 2, pp. 137–154, May 2004.',

        '[5] K. Simonyan and A. Zisserman, "Very deep convolutional networks for '
        'large-scale image recognition," in <i>Proc. Int. Conf. Learning Representations '
        '(ICLR)</i>, 2015.',

        '[6] M. Tan and Q. V. Le, "EfficientNet: Rethinking model scaling for '
        'convolutional neural networks," in <i>Proc. Int. Conf. Machine Learning (ICML)</i>, '
        'vol. 97, PMLR, 2019, pp. 6105–6114.',

        '[7] S. Ioffe and C. Szegedy, "Batch normalization: Accelerating deep network '
        'training by reducing internal covariate shift," in <i>Proc. Int. Conf. Machine '
        'Learning (ICML)</i>, vol. 37, PMLR, 2015, pp. 448–456.',

        '[8] N. Srivastava, G. Hinton, A. Krizhevsky, I. Sutskever, and R. Salakhutdinov, '
        '"Dropout: A simple way to prevent neural networks from overfitting," '
        '<i>J. Machine Learning Research</i>, vol. 15, no. 1, pp. 1929–1958, 2014.',
    ]
    for r in refs:
        story.append(Paragraph(r, S['ref']))
        sp(2)

    bp()

    # ─────────────────────────────────────────────────────────────────────────
    # APPENDICES
    # ─────────────────────────────────────────────────────────────────────────
    h1("Appendices")
    h2("Appendix C: Source Code Repository")
    body(
        "The complete source code for this project is available on GitHub at: "
        "<b>https://github.com/Max-i26/emotion_detection</b>"
    )
    body("Key source files include:")
    for f in [
        "train.py — Upgraded 4-Stage ConvNet training pipeline with Focal Loss",
        "live_detect_pro.py — Primary real-time MediaPipe + CNN emotion detector",
        "evaluate_all.py — Comprehensive test set evaluation with classification report",
        "generate_report_assets.py — Figure generation scripts for this report",
        "run_webcam.bat — Single-click Windows launcher",
    ]:
        bullet(f)

    h2("Appendix D: Performance Metrics JSON")
    body(
        "Full evaluation results including per-class precision, recall, F1-score, "
        "support values, and the raw confusion matrix are saved in machine-readable "
        "JSON format in performance_metrics.json within the repository root."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # BUILD
    # ─────────────────────────────────────────────────────────────────────────
    doc.build(story, canvasmaker=ReportCanvas)
    print(f"[OK] Saved: {pdf_path}")


if __name__ == "__main__":
    build_report()
