"""
build_capstone_report_pdf.py  –  Comprehensive Rebuild v4
Student : Harol Maxilan | Index: 22CDS0439
Supervisor: Mr. Dimuthu Lakshan | HOD: Dr. UAP Ishanka
Date: 28/09/2026

Comprehensive updates addressing all reviewer points:
1. Exact mathematical consistency between Confusion Matrix, Table 5.4, Fig 5.2/5.3, and text
2. Correct FER2013 class counts (Sad=1247, Surprise=831, Neutral=1233, total=7178 test)
3. Corrected class-frequency weights (Disgust=9.41, Happy=0.57); numbered equations; full label-smoothing loss
4. Exact architecture parameters from model.summary() (4,826,055 total; trainable=4,821,703; non-trainable=4,352)
5. Dataset clarifications (combined Public+Private test=7178, human baseline 65±5%, 85/15 train/val split)
6. Aligned training history (best epoch 40, stop at 52) and clarified ablation study in percentage points
7. Precise real-time timing (18-27ms inference, 28-30 FPS throughput, 333ms window, 0.7-1.1s plurality shift)
8. UML and figures updated (renumbered sequentially, proper UML semantics, no repeated internal titles)
9. Automated 2-pass dynamic page numbering: preliminary = Roman (i-ix), Chapter 1 = 1 Arabic, clean non-wrapping TOC
10. Spelling, wording, singular declaration, and proper citations (Shan, Ojala, Szegedy, Bazarevsky, Cao, etc.)
11. GitHub repository and Google Drive demonstration video links integrated throughout
12. Full-colour university logo preserved on cover page
"""
import os, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import black, white, Color
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable, KeepTogether, Flowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as pdfcanvas

# ─────────────────────────────────────────────────────────────────────────────
# FONTS  – Register Windows TTF for full Unicode support
# ─────────────────────────────────────────────────────────────────────────────
FONT_DIR = r"C:\Windows\Fonts"
_FONTS = {
    "MyRoman":      ("times.ttf",   "Times New Roman"),
    "MyBold":       ("timesbd.ttf", "Times New Roman Bold"),
    "MyItalic":     ("timesi.ttf",  "Times New Roman Italic"),
    "MyBoldItalic": ("timesbi.ttf", "Times New Roman Bold Italic"),
}
for fname, (ttf_file, _) in _FONTS.items():
    path = os.path.join(FONT_DIR, ttf_file)
    if os.path.exists(path):
        pdfmetrics.registerFont(TTFont(fname, path))
    else:
        print(f"[WARN] Font not found: {path} – falling back to Times-Roman")

ROMAN   = "MyRoman"
BOLD    = "MyBold"
ITALIC  = "MyItalic"

# ─────────────────────────────────────────────────────────────────────────────
# PAGE GEOMETRY
# ─────────────────────────────────────────────────────────────────────────────
W, H   = A4
LM     = 38 * mm
RM     = 28 * mm
TM     = 28 * mm
BM     = 25 * mm
BW     = W - LM - RM          # body width ≈ 144 mm

GITHUB_URL = "https://github.com/Max-i26/emotion_detection"
DEMO_URL   = "https://drive.google.com/file/d/1TY1k3__QjDsKLtXpS4G2z7KJP_DZ8bSV/view?usp=sharing"

# ─────────────────────────────────────────────────────────────────────────────
# TWO-PASS PAGE TRACKING & NUMBERED CANVAS
# ─────────────────────────────────────────────────────────────────────────────
PAGE_TRACKER = {}
CHAPTER1_PAGE = [11]  # Default estimate for Pass 1, updated dynamically in Pass 2

class BookmarkFlowable(Flowable):
    """Zero-height marker that records the exact physical page of any element."""
    def __init__(self, key):
        super().__init__()
        self.key = key
        self.width = 0
        self.height = 0
    def wrap(self, availWidth, availHeight):
        return 0, 0
    def draw(self):
        PAGE_TRACKER[self.key] = self.canv._pageNumber
        if self.key == "ch1":
            CHAPTER1_PAGE[0] = self.canv._pageNumber

def to_roman(n):
    roman_map = [
        (10, 'x'), (9, 'ix'), (5, 'v'), (4, 'iv'), (1, 'i')
    ]
    result = []
    for val, numeral in roman_map:
        while n >= val:
            result.append(numeral)
            n -= val
    return ''.join(result)

class ReportCanvas(pdfcanvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        ch1_pg = CHAPTER1_PAGE[0]
        for i, state in enumerate(self._saved_page_states):
            self.__dict__.update(state)
            pg = i + 1
            self._draw_page_furniture(pg, ch1_pg)
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)

    def _draw_page_furniture(self, pg, ch1_pg):
        if pg == 1:
            return  # Cover page: no headers or footers
        self.saveState()
        lx = LM; rx = W - RM
        # Header
        hy = H - TM + 6 * mm
        self.setFont(ROMAN, 8.5)
        self.drawString(lx, hy, "Department of Data Science, Faculty of Computing")
        self.drawString(lx, hy - 11, "Sabaragamuwa University of Sri Lanka")
        self.drawRightString(rx, hy - 5, "Capstone Project Report")
        self.setLineWidth(0.4)
        self.line(lx, hy - 16, rx, hy - 16)

        # Footer
        fy = BM - 5 * mm
        self.line(lx, fy + 12, rx, fy + 12)
        if pg < ch1_pg:
            # Preliminary page: Roman numeral (cover=1 unnumbered, page 2 = 'i')
            label = to_roman(pg - 1)
        else:
            # Body page: Arabic numeral starting from 1
            label = str(pg - ch1_pg + 1)
        self.setFont(ROMAN, 9)
        self.drawCentredString((lx + rx) / 2, fy, label)
        self.restoreState()

# ─────────────────────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────────────────────
def get_styles():
    base = dict(fontName=ROMAN, fontSize=11, leading=15.5,
                textColor=black, alignment=TA_JUSTIFY,
                spaceAfter=7, spaceBefore=0)
    def ps(name, **kw):
        d = {**base, **kw}
        return ParagraphStyle(name, **d)

    return {
        'body':        ps('body'),
        'body_left':   ps('body_left', alignment=TA_LEFT),
        'body_center': ps('body_center', alignment=TA_CENTER),
        'body_right':  ps('body_right', alignment=TA_RIGHT),
        'italic':      ps('italic', fontName=ITALIC),
        'h_chap':      ps('h_chap', fontName=BOLD, fontSize=16, leading=21,
                           spaceBefore=0, spaceAfter=14, alignment=TA_LEFT, keepWithNext=True),
        'h2':          ps('h2', fontName=BOLD, fontSize=13, leading=17,
                           spaceBefore=14, spaceAfter=8, alignment=TA_LEFT, keepWithNext=True),
        'h3':          ps('h3', fontName=BOLD, fontSize=11.5, leading=15,
                           spaceBefore=10, spaceAfter=5, alignment=TA_LEFT, keepWithNext=True),
        'h4':          ps('h4', fontName=BOLD, fontSize=11, leading=14,
                           spaceBefore=8, spaceAfter=4, alignment=TA_LEFT, keepWithNext=True),
        'bullet':      ps('bullet', leftIndent=14, firstLineIndent=-10,
                           spaceAfter=5, alignment=TA_JUSTIFY),
        'sub_bullet':  ps('sub_bullet', leftIndent=26, firstLineIndent=-10,
                           spaceAfter=4, alignment=TA_JUSTIFY),
        'ref':         ps('ref', leftIndent=24, firstLineIndent=-24,
                           spaceAfter=6, alignment=TA_JUSTIFY),
        'caption':     ps('caption', fontName=BOLD, fontSize=9.5, leading=12.5,
                           alignment=TA_CENTER, spaceBefore=5, spaceAfter=12, keepWithNext=False),
        'cover_uni':   ps('cover_uni', fontName=BOLD, fontSize=18, leading=23,
                           alignment=TA_CENTER, spaceAfter=4),
        'cover_title': ps('cover_title', fontName=BOLD, fontSize=13, leading=18,
                           alignment=TA_CENTER, spaceAfter=6),
        'cover_sub':   ps('cover_sub', fontName=ITALIC, fontSize=10.5, leading=14.5,
                           alignment=TA_CENTER, spaceAfter=8),
        'cover_info':  ps('cover_info', fontName=BOLD, fontSize=11, leading=15,
                           alignment=TA_CENTER, spaceAfter=5),
        'appx_title':  ps('appx_title', fontName=BOLD, fontSize=14, leading=18,
                           alignment=TA_CENTER, spaceAfter=18, spaceBefore=0, keepWithNext=True),
    }

_S = get_styles()

def bp(story): story.append(PageBreak())
def sp(story, h=8): story.append(Spacer(1, h))
def hr(story): story.append(HRFlowable(width=BW, thickness=0.6, color=black, spaceAfter=6, spaceBefore=6))

def body(story, text): story.append(Paragraph(text, _S['body']))
def body_left(story, text): story.append(Paragraph(text, _S['body_left']))
def h_chap(story, text, key=None):
    if key: story.append(BookmarkFlowable(key))
    story.append(Paragraph(text, _S['h_chap']))
def h2(story, text, key=None):
    if key: story.append(BookmarkFlowable(key))
    story.append(Paragraph(text, _S['h2']))
def h3(story, text): story.append(Paragraph(text, _S['h3']))
def h4(story, text): story.append(Paragraph(text, _S['h4']))
def bullet(story, text): story.append(Paragraph(f"\u2022\u2003{text}", _S['bullet']))
def sub_bullet(story, text): story.append(Paragraph(f"\u2013\u2002{text}", _S['sub_bullet']))
def caption(story, text): story.append(Paragraph(text, _S['caption']))

def PL(text): return Paragraph(text, _S['body_left'])

def fig(story, path, w_frac=1.0, h_frac=None, cap_text="", key=None):
    if key: story.append(BookmarkFlowable(key))
    elements = []
    if os.path.exists(path):
        img_w = BW * w_frac
        img_h = img_w * (h_frac if h_frac else 0.60)
        elements.append(Image(path, width=img_w, height=img_h, hAlign='CENTER'))
    else:
        elements.append(Paragraph(f"[Figure not found: {path}]", _S['italic']))
    if cap_text:
        elements.append(Paragraph(cap_text, _S['caption']))
    story.append(KeepTogether(elements))

def plain_table(data, col_ws, header=True):
    t = Table(data, colWidths=col_ws)
    ts = [
        ('GRID',         (0,0), (-1,-1), 0.5, black),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',   (0,0), (-1,-1), 4),
        ('BOTTOMPADDING',(0,0), (-1,-1), 4),
        ('LEFTPADDING',  (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('FONTNAME',     (0,0), (-1,-1), ROMAN),
        ('FONTSIZE',     (0,0), (-1,-1), 9.5),
    ]
    if header:
        ts += [
            ('BACKGROUND', (0,0), (-1,0), Color(0.88,0.88,0.88)),
            ('FONTNAME',   (0,0), (-1,0), BOLD),
        ]
    t.setStyle(TableStyle(ts))
    return t

def clean_toc_row(title, page_str, bold=False, indent=0):
    """
    Renders a clean TOC entry with non-wrapping dot leaders.
    Col 1: Title (left indent for subsections)
    Col 2: Leader dots (fixed width, exactly 18 dots so they never wrap)
    Col 3: Page number (right-aligned)
    """
    fn = BOLD if bold else ROMAN
    st_t = ParagraphStyle('__tt', fontName=fn, fontSize=10.5, leading=13.5,
                          alignment=TA_LEFT, leftIndent=indent)
    st_p = ParagraphStyle('__tp', fontName=fn, fontSize=10.5, leading=13.5, alignment=TA_RIGHT)
    dots_text = ". " * 16
    st_d = ParagraphStyle('__td', fontName=ROMAN, fontSize=8, leading=13.5, alignment=TA_CENTER)

    # Total width is BW. ColWidths: BW - 48mm, 32mm, 16mm
    row = [[Paragraph(title, st_t), Paragraph(dots_text, st_d), Paragraph(page_str, st_p)]]
    t = Table(row, colWidths=[BW - 48*mm, 32*mm, 16*mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    return t

def appx_a_row(label, value=""):
    lp = Paragraph(label, ParagraphStyle('__al', fontName=ROMAN, fontSize=11, leading=24))
    vp = Paragraph(value if value else "\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026",
                   ParagraphStyle('__av', fontName=ROMAN, fontSize=11, leading=24))
    t = Table([[lp, vp]], colWidths=[BW*0.44, BW*0.56])
    t.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'BOTTOM'),
        ('TOPPADDING',(0,0),(-1,-1),3),
        ('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('LEFTPADDING',(0,0),(-1,-1),0),
        ('RIGHTPADDING',(0,0),(-1,-1),0)
    ]))
    return t

DOTS28 = "\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026"
DOTS14 = "\u2026\u2026\u2026\u2026\u2026\u2026\u2026"

def appx_b_block(story, name_label, name_value, sig_label):
    body_left(story, name_label)
    story.append(Paragraph(f"<b>{name_value}</b>", _S['body_left']))
    sp(story, 18)
    row1 = Table([[PL(DOTS28), PL(DOTS28)]], colWidths=[BW*0.48, BW*0.52])
    row1.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'BOTTOM'),
        ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0),
        ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0)]))
    story.append(row1)
    row2 = Table([[PL(""), Paragraph(sig_label, _S['body_left'])]], colWidths=[BW*0.48, BW*0.52])
    row2.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0)]))
    story.append(row2)
    body_left(story, f"Date:  {DOTS14}")
    sp(story, 16)

def resolve_page(key, fallback_arabic, fallback_prelim=None):
    """Translates tracked physical page to formatted page number string."""
    ch1_pg = CHAPTER1_PAGE[0]
    if key in PAGE_TRACKER:
        phys = PAGE_TRACKER[key]
        if phys < ch1_pg:
            return to_roman(phys - 1)
        else:
            return str(phys - ch1_pg + 1)
    if fallback_prelim is not None:
        return fallback_prelim
    return str(fallback_arabic)

# ═════════════════════════════════════════════════════════════════════════════
# STORY BUILDER (Takes pass number 1 or 2)
# ═════════════════════════════════════════════════════════════════════════════
def generate_story():
    story = []

    # ─────────────────────────────────────────────────────────────────────────
    # COVER PAGE
    # ─────────────────────────────────────────────────────────────────────────
    story.append(Paragraph("Sabaragamuwa University of Sri Lanka", _S['cover_uni']))
    sp(story, 4)
    hr(story)
    sp(story, 10)

    # University Logo (Full Color preserved)
    logo = "Report/Screenshot 2026-08-29 095328.png"
    if os.path.exists(logo):
        story.append(Image(logo, width=1.85*inch, height=1.85*inch, hAlign='CENTER'))
    sp(story, 12)

    story.append(Paragraph(
        "REAL-TIME FACIAL EMOTION RECOGNITION USING MEDIAPIPE<br/>"
        "AND DEEP CONVOLUTIONAL NEURAL NETWORKS WITH FOCAL LOSS",
        _S['cover_title']))
    sp(story, 8)
    story.append(Paragraph(
        "<i>A Project Report submitted to the Faculty of Computing, "
        "Sabaragamuwa University of Sri Lanka, in partial fulfilment of the "
        "requirements for the Degree of Bachelor of Science Honours in Data Science.</i>",
        _S['cover_sub']))
    sp(story, 16)

    for lbl, val in [
        ("Student Name", "Harol Maxilan"),
        ("Index Number", "22CDS0439"),
        ("Internal Supervisor", "Mr. Dimuthu Lakshan"),
        ("Head of Department", "Dr. UAP Ishanka"),
        ("Date of Submission", "28 September 2026"),
        ("Source Code Repository", f"<font color='#0000AA'><u>{GITHUB_URL}</u></font>"),
        ("Demonstration Video", f"<font color='#0000AA'><u>{DEMO_URL}</u></font>"),
    ]:
        cw = [BW*0.38, BW*0.62]
        ct = Table([[Paragraph(f"<b>{lbl}</b>", _S['body_left']),
                     Paragraph(f"<b>: {val}</b>", _S['body_left'])]], colWidths=cw)
        ct.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2),
            ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),
            ('LINEBELOW',(0,0),(-1,-1),0.4,black),
        ]))
        story.append(ct); sp(story, 2)

    sp(story, 16)
    story.append(Paragraph(
        "<b>DEPARTMENT OF DATA SCIENCE<br/>FACULTY OF COMPUTING<br/>"
        "SABARAGAMUWA UNIVERSITY OF SRI LANKA</b>",
        _S['cover_info']))
    story.append(Paragraph("September 2026", _S['body_center']))
    hr(story)
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # APPENDIX A — DECLARATION (Singular, proper academic wording)
    # ─────────────────────────────────────────────────────────────────────────
    story.append(BookmarkFlowable("appx_a"))
    story.append(Paragraph("Appendix A \u2013 Declaration", _S['appx_title']))
    body(story,
        "I declare that this report does not incorporate, without acknowledgment, any "
        "material previously submitted for a Degree or a Diploma in any University, and to "
        "the best of my knowledge and belief, it does not contain any material previously "
        "published or written by another person, except where due reference is "
        "made in the text. Also, I hereby grant Sabaragamuwa University of Sri Lanka the "
        "non-exclusive right to reproduce and distribute my report, in whole or in part, in "
        "print, electronic, or other media. I retain the right to use this content in whole "
        "or in part in future works (such as articles or books).")
    sp(story, 36)
    for lbl, val in [
        ("Index Number",        "22CDS0439"),
        ("Name of Student",     "Harol Maxilan"),
        ("Date",                "28/09/2026"),
        ("Signature of Student", DOTS14),
    ]:
        story.append(appx_a_row(lbl, val))
        sp(story, 6)
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # APPENDIX B — CERTIFICATE OF APPROVAL
    # ─────────────────────────────────────────────────────────────────────────
    story.append(BookmarkFlowable("appx_b"))
    story.append(Paragraph("Appendix B \u2013 Certificate of Approval", _S['appx_title']))
    body(story,
        "We hereby declare that this report is the student\u2019s own work and effort, "
        "and that all other sources of information used have been duly acknowledged. "
        "This report has been submitted with our approval.")
    sp(story, 22)
    appx_b_block(story, "Name of Internal Supervisor:", "Mr. Dimuthu Lakshan", "Signature of Internal Supervisor")
    appx_b_block(story, "Name of Head of Department:", "Dr. UAP Ishanka", "Signature of Head of Department")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # ACKNOWLEDGMENTS
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Acknowledgments", key="ack")
    body(story,
        "The successful completion of this capstone project owes a great deal to the "
        "guidance, encouragement, and support of several individuals and institutions, "
        "without whom this work would not have been possible.")
    body(story,
        "I wish to express my deepest gratitude to my internal supervisor, "
        "<b>Mr. Dimuthu Lakshan</b>, for his invaluable guidance, constructive criticism, "
        "and sustained encouragement throughout the entire research lifecycle. His domain "
        "expertise in machine learning and computer vision was pivotal in shaping both the "
        "research direction and the technical rigour of this project.")
    body(story,
        "I am profoundly grateful to <b>Dr. UAP Ishanka</b>, Head of the Department of Data "
        "Science, for providing access to the university's computational resources and for "
        "fostering an intellectually stimulating academic environment within the Faculty of "
        "Computing at Sabaragamuwa University of Sri Lanka.")
    body(story,
        "I also wish to acknowledge the broader open-source community, including the "
        "developers of TensorFlow, Google MediaPipe, and OpenCV, whose freely available "
        "tools formed the technological backbone of this project's implementation. The "
        "original creators of the FER2013 dataset, particularly Goodfellow et al. [1], "
        "deserve recognition for providing a publicly accessible benchmark that continues "
        "to drive progress in affective computing research.")
    body(story,
        "I am grateful to my fellow students in the Department of Data Science for their "
        "collegial support and stimulating technical discussions throughout the programme. "
        "Finally, I acknowledge the unrelenting patience and encouragement of my family, "
        "whose support sustained my motivation throughout the demanding period of "
        "research and report preparation.")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # ABSTRACT
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Abstract", key="abstract")
    body(story,
        "Automated facial emotion recognition (FER) in unconstrained, real-world environments "
        "presents a persistent challenge in affective computing, largely due to intra-class "
        "appearance variance, inter-class expression ambiguity, and severe dataset class "
        "imbalance. This capstone project addresses these challenges by designing, training, "
        "and deploying an end-to-end real-time FER system capable of classifying live webcam "
        "frames into seven emotion categories: Angry, Disgust, Fear, Happy, Sad, Surprise, "
        "and Neutral.")
    body(story,
        "The proposed methodology employs Google MediaPipe BlazeFace [3] for robust face bounding "
        "box localisation, and a purpose-built four-stage Deep Convolutional Neural Network "
        "(CNN) consisting of 4,826,055 parameters incorporating Batch Normalisation [7], "
        "L2 weight regularisation, Global Average Pooling, and progressive Dropout. To address the "
        "severe 16.5\u00d7 class imbalance inherent in the FER2013 benchmark [1] \u2014 where the "
        "Disgust class contains only 436 training samples compared to 7,215 Happy samples \u2014 "
        "a Categorical Focal Loss formulation (gamma = 2.0) is combined with Label Smoothing "
        "(epsilon = 0.1) and static balanced class-frequency weighting.")
    body(story,
        "Empirical evaluation on 7,178 unseen FER2013 test images (comprising the combined "
        "PublicTest and PrivateTest partitions) demonstrates that the proposed system achieves "
        "a test accuracy of 63.51%, a weighted F1-score of 63.10%, and a macro F1-score of 59.45%, "
        "operating within 1.49 percentage points of the human evaluator benchmark of 65 \u00b1 5% "
        "reported by Goodfellow et al. [1]. A 10-frame temporal prediction window (333 ms at 30 FPS) "
        "based on plurality voting substantially reduces high-frequency prediction flickering during "
        "live deployment. An ablation study confirms that each proposed component contributes "
        "incrementally to overall performance (+6.17 percentage points over baseline).")
    body(story,
        "The complete system operates at 28\u201330 frames per second on consumer laptop CPU hardware "
        "(11th-generation Intel Core i5). The complete source code is publicly accessible at "
        f"<b>{GITHUB_URL}</b>, and a recorded video demonstration is available at <b>{DEMO_URL}</b>.")
    body(story, "<b>Keywords:</b> Facial Emotion Recognition, Convolutional Neural Network, "
        "Focal Loss, Label Smoothing, MediaPipe, Class Imbalance, FER2013, Real-Time Vision.")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # TABLE OF CONTENTS
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Table of Contents", key="toc")
    sp(story, 6)
    toc_entries = [
        ("Declaration (Appendix A)",                                resolve_page("appx_a", 2, "i"),    True,  0),
        ("Certificate of Approval (Appendix B)",                    resolve_page("appx_b", 3, "ii"),   True,  0),
        ("Acknowledgments",                                         resolve_page("ack", 4, "iii"),     True,  0),
        ("Abstract",                                                resolve_page("abstract", 5, "iv"), True,  0),
        ("Table of Contents",                                       resolve_page("toc", 6, "v"),       True,  0),
        ("List of Figures",                                         resolve_page("lof", 7, "vi"),      True,  0),
        ("List of Tables",                                          resolve_page("lot", 8, "vii"),     True,  0),
        ("Glossary of Abbreviations",                               resolve_page("gloss", 9, "viii"),  True,  0),
        ("Chapter 1: Introduction",                                 resolve_page("ch1", 1),            True,  0),
        ("1.1  Background and Context",                             resolve_page("sec_1_1", 1),        False, 12),
        ("1.2  Problem Statement",                                  resolve_page("sec_1_2", 2),        False, 12),
        ("1.3  Goals and Objectives",                               resolve_page("sec_1_3", 2),        False, 12),
        ("1.4  Motivation",                                         resolve_page("sec_1_4", 3),        False, 12),
        ("1.5  Scope of the Completed Project",                     resolve_page("sec_1_5", 3),        False, 12),
        ("1.6  Research Contributions",                             resolve_page("sec_1_6", 4),        False, 12),
        ("1.7  Software Repository and Demonstration Links",        resolve_page("sec_1_7", 4),        False, 12),
        ("1.8  Report Organisation",                                resolve_page("sec_1_8", 5),        False, 12),
        ("Chapter 2: Literature Review",                            resolve_page("ch2", 6),            True,  0),
        ("2.1  Psychological Foundations of Emotion Recognition",   resolve_page("sec_2_1", 6),        False, 12),
        ("2.2  Classical Computer Vision Approaches",               resolve_page("sec_2_2", 6),        False, 12),
        ("2.3  Deep Learning Architectures for FER",                resolve_page("sec_2_3", 7),        False, 12),
        ("2.4  FER2013 Benchmark Dataset Characteristics",          resolve_page("sec_2_4", 8),        False, 12),
        ("2.5  The Challenge of Class Imbalance in FER",            resolve_page("sec_2_5", 9),        False, 12),
        ("2.6  Loss Functions for Imbalanced Classification",       resolve_page("sec_2_6", 10),       False, 12),
        ("2.7  Real-Time Face Detection Pipelines",                 resolve_page("sec_2_7", 11),       False, 12),
        ("2.8  Research Gap and Technical Motivation",              resolve_page("sec_2_8", 12),       False, 12),
        ("Chapter 3: System Specification and Design",              resolve_page("ch3", 13),           True,  0),
        ("3.1  Software Requirements Specification",                 resolve_page("sec_3_1", 13),       False, 12),
        ("3.2  Hardware and Software Specifications",               resolve_page("sec_3_2", 14),       False, 12),
        ("3.3  Use Case Modeling",                                  resolve_page("sec_3_3", 14),       False, 12),
        ("3.4  Five-Stage Pipeline Architecture",                   resolve_page("sec_3_4", 16),       False, 12),
        ("3.5  Interaction Design: UML Sequence Diagram",           resolve_page("sec_3_5", 17),       False, 12),
        ("3.6  Data Flow and Storage Specifications",               resolve_page("sec_3_6", 18),       False, 12),
        ("Chapter 4: Methodology",                                  resolve_page("ch4", 19),           True,  0),
        ("4.1  Dataset Composition and Stratification",             resolve_page("sec_4_1", 19),       False, 12),
        ("4.2  Data Preprocessing Pipeline",                        resolve_page("sec_4_2", 20),       False, 12),
        ("4.3  Data Augmentation Strategy",                         resolve_page("sec_4_3", 21),       False, 12),
        ("4.4  Static Balanced Class Weighting",                    resolve_page("sec_4_4", 22),       False, 12),
        ("4.5  Loss Formulation: Focal Loss with Label Smoothing",  resolve_page("sec_4_5", 23),       False, 12),
        ("4.6  4-Stage Deep ConvNet Architecture",                  resolve_page("sec_4_6", 24),       False, 12),
        ("4.7  Regularisation Stack",                               resolve_page("sec_4_7", 25),       False, 12),
        ("4.8  Training Protocol and Hyperparameters",              resolve_page("sec_4_8", 26),       False, 12),
        ("4.9  Training Convergence Analysis",                      resolve_page("sec_4_9", 27),       False, 12),
        ("4.10 Real-Time Inference Engine",                         resolve_page("sec_4_10", 27),      False, 12),
        ("4.11 Temporal Prediction Smoothing Protocol",             resolve_page("sec_4_11", 28),      False, 12),
        ("Chapter 5: Results and Evaluation",                       resolve_page("ch5", 29),           True,  0),
        ("5.1  Experimental Setup and Protocol",                    resolve_page("sec_5_1", 29),       False, 12),
        ("5.2  Overall Classification Performance",                 resolve_page("sec_5_2", 29),       False, 12),
        ("5.3  Ablation Study Results",                             resolve_page("sec_5_3", 30),       False, 12),
        ("5.4  State-of-the-Art Benchmark Comparison",              resolve_page("sec_5_4", 32),       False, 12),
        ("5.5  Per-Class Classification Report",                    resolve_page("sec_5_5", 33),       False, 12),
        ("5.6  Confusion Matrix Analysis",                          resolve_page("sec_5_6", 34),       False, 12),
        ("5.7  Per-Class F1-Score Breakdown",                       resolve_page("sec_5_7", 35),       False, 12),
        ("5.8  Real-Time Operational Testing Protocol",             resolve_page("sec_5_8", 36),       False, 12),
        ("5.9  System Latency and Plurality Window Dynamics",       resolve_page("sec_5_9", 37),       False, 12),
        ("Chapter 6: Limitations and Ethical Considerations",       resolve_page("ch6", 38),           True,  0),
        ("6.1  Technical Limitations",                              resolve_page("sec_6_1", 38),       False, 12),
        ("6.2  Dataset and Generalisation Limitations",             resolve_page("sec_6_2", 39),       False, 12),
        ("6.3  Ethical Considerations and Consent",                 resolve_page("sec_6_3", 40),       False, 12),
        ("6.4  Privacy Framework and GDPR Analysis",                resolve_page("sec_6_4", 41),       False, 12),
        ("6.5  Demographic Fairness and Bias Mitigation",           resolve_page("sec_6_5", 41),       False, 12),
        ("Chapter 7: Future Work",                                  resolve_page("ch7", 43),           True,  0),
        ("Chapter 8: Conclusions",                                  resolve_page("ch8", 45),           True,  0),
        ("References",                                              resolve_page("refs", 47),          True,  0),
        ("Appendices",                                              resolve_page("appx", 50),          True,  0),
        ("Appendix C: Source Code Repository and Demo",             resolve_page("appx_c", 50),        False, 12),
        ("Appendix D: Training Hyperparameter Reference",           resolve_page("appx_d", 51),        False, 12),
        ("Appendix E: Performance Metrics Reference",               resolve_page("appx_e", 52),        False, 12),
    ]
    for title, pg, bld, ind in toc_entries:
        story.append(clean_toc_row(title, pg, bld, ind))
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # LIST OF FIGURES & LIST OF TABLES
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "List of Figures", key="lof")
    sp(story, 4)
    figs_lof = [
        ("Figure 2.1: FER2013 Dataset Class Distribution \u2014 Train vs Test Partitions", resolve_page("fig_dist", 8)),
        ("Figure 3.1: Use Case Diagram \u2014 Real-Time Facial Emotion Recognition System", resolve_page("fig_uc", 14)),
        ("Figure 3.2: Five-Stage Real-Time Pipeline Architecture and Data Flow",           resolve_page("fig_arch", 16)),
        ("Figure 3.3: UML Sequence Diagram \u2014 Real-Time Emotion Detection Pipeline",   resolve_page("fig_seq", 17)),
        ("Figure 4.1: Training and Validation Accuracy (a) and Focal Loss (b) Curves",      resolve_page("fig_train", 27)),
        ("Figure 5.1: Ablation Study \u2014 Performance Comparison Across Model Configs",   resolve_page("fig_abl", 30)),
        ("Figure 5.2: Confusion Matrix Heatmap on 7,178 Unseen FER2013 Test Images",       resolve_page("fig_cm", 34)),
        ("Figure 5.3: Per-Class F1-Score Breakdown (Proposed 4-Stage CNN with Focal Loss)", resolve_page("fig_f1", 35)),
    ]
    for f_title, f_pg in figs_lof:
        story.append(clean_toc_row(f_title, f_pg, False, 0))

    sp(story, 16)
    h_chap(story, "List of Tables", key="lot")
    sp(story, 4)
    tabs_lot = [
        ("Table 2.1: FACS Action Unit Mapping for Canonical Facial Emotions",       resolve_page("tab_facs", 7)),
        ("Table 3.1: Hardware and Software System Specifications",                  resolve_page("tab_hw", 14)),
        ("Table 3.2: Use Case Specifications",                                      resolve_page("tab_uc", 15)),
        ("Table 4.1: Data Augmentation Hyperparameters and Ranges",                 resolve_page("tab_aug", 21)),
        ("Table 4.2: Upgraded 4-Stage ConvNet Layer Specifications and Parameters", resolve_page("tab_arch", 24)),
        ("Table 5.1: Overall Classification Performance on FER2013 Test Set",       resolve_page("tab_overall", 29)),
        ("Table 5.2: Focal Loss Ablation Study Results",                            resolve_page("tab_abl", 30)),
        ("Table 5.3: State-of-the-Art FER2013 Benchmark Comparison",               resolve_page("tab_sota", 32)),
        ("Table 5.4: Detailed Per-Class Classification Report (Derived from Matrix)",resolve_page("tab_cls", 33)),
        ("Table 5.5: Real-Time Operational Testing Protocol and Pass/Fail Results", resolve_page("tab_rt", 36)),
        ("Table 5.6: Row-Normalized Confusion Matrix for Morphological Error Breakdown", resolve_page("tab_norm_cm", 37)),
        ("Table 6.1: Ethical Risk Assessment Matrix and Algorithmic Mitigation Policies", resolve_page("tab_ethics", 42)),
        ("Table C.1: Source Code File Inventory and Structural Roles",              resolve_page("tab_appx_c", 50)),
        ("Table D.1: Comprehensive Training Hyperparameter Configuration",          resolve_page("tab_appx_d", 51)),
        ("Table E.1: Verified Model Performance Metrics Reference",                 resolve_page("tab_appx_e", 52)),
    ]
    for t_title, t_pg in tabs_lot:
        story.append(clean_toc_row(t_title, t_pg, False, 0))
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # GLOSSARY OF ABBREVIATIONS
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Glossary of Abbreviations", key="gloss")
    sp(story, 6)
    abbrevs = [
        ("AU",      "Action Unit \u2014 a discrete facial muscle movement defined by the Facial Action Coding System (FACS)"),
        ("BN",      "Batch Normalisation \u2014 a technique that normalises layer inputs across mini-batch samples"),
        ("CCE",     "Categorical Cross-Entropy \u2014 standard multi-class classification loss function"),
        ("CNN",     "Convolutional Neural Network \u2014 a deep neural network employing learnable convolution filters"),
        ("DNN",     "Deep Neural Network \u2014 an artificial neural network containing multiple hidden representation layers"),
        ("FER",     "Facial Emotion Recognition \u2014 automated computer vision classification of human facial expressions"),
        ("FER2013", "Facial Expression Recognition 2013 \u2014 a widely evaluated 35,887-image benchmark dataset"),
        ("FL",      "Focal Loss \u2014 a loss function that dynamically downweights well-classified easy samples"),
        ("FPS",     "Frames Per Second \u2014 metric quantifying real-time processing throughput"),
        ("GAP",     "Global Average Pooling \u2014 spatial reduction of feature maps into a single average per channel"),
        ("GPU",     "Graphics Processing Unit \u2014 massively parallel processor used for accelerated neural training"),
        ("HOG",     "Histogram of Oriented Gradients \u2014 classical edge-orientation gradient descriptor"),
        ("LBP",     "Local Binary Pattern \u2014 classical visual texture descriptor based on local intensity thresholds"),
        ("LS",      "Label Smoothing \u2014 regularisation technique softening one-hot targets to prevent overconfidence"),
        ("ML",      "Machine Learning \u2014 automated acquisition of predictive models from empirical training data"),
        ("ROI",     "Region of Interest \u2014 cropped image bounding box containing the localized human face"),
        ("SOTA",    "State-of-the-Art \u2014 the highest demonstrated level of performance on an academic benchmark"),
        ("SUSL",    "Sabaragamuwa University of Sri Lanka"),
        ("SVM",     "Support Vector Machine \u2014 classical margin-maximising linear and non-linear classifier"),
        ("TF",      "TensorFlow \u2014 Google\u2019s open-source machine learning and deep learning framework"),
        ("UML",     "Unified Modelling Language \u2014 industry standard visual notation for software architecture"),
        ("ViT",     "Vision Transformer \u2014 neural architecture applying self-attention over image patch sequences"),
        ("WSL2",    "Windows Subsystem for Linux 2 \u2014 virtualization layer running native Linux environments on Windows"),
    ]
    ab_data = [[Paragraph(f"<b>{a}</b>", _S['body_left']), Paragraph(d, _S['body_left'])] for a, d in abbrevs]
    ab_tab = plain_table([[Paragraph("<b>Abbreviation</b>", _S['body_left']),
                           Paragraph("<b>Expansion and Academic Definition</b>", _S['body_left'])]] + ab_data,
                         [BW*0.18, BW*0.82], header=True)
    story.append(KeepTogether(ab_tab))
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # CHAPTER 1: INTRODUCTION
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Chapter 1: Introduction", key="ch1")

    h2(story, "1.1  Background and Context", key="sec_1_1")
    body(story,
        "Facial expressions represent the most immediate, nuanced, and cross-culturally universal "
        "modality of human non-verbal communication [12]. The capability to automatically detect and "
        "interpret affective states from digital video streams has emerged as a cornerstone of next-generation "
        "human-computer interaction. Transformative use cases span intelligent tutoring systems in e-learning "
        "that adapt pedagogical difficulty when learners exhibit frustration or confusion, automotive driver "
        "monitoring systems that detect fatigue or road rage, telemedicine platforms assessing affective "
        "blunting in mood disorders, and digital wellbeing tools.")
    body(story,
        "The scientific domain of Affective Computing, formalised by Picard [11], seeks to bridge the "
        "gap between human emotional expression and computational intelligence. In computer vision, "
        "Facial Emotion Recognition (FER) has transitioned from handcrafted texture descriptors (such as "
        "Local Binary Patterns [14] and Histograms of Oriented Gradients [13]) to end-to-end Deep "
        "Convolutional Neural Networks (CNNs). This paradigm shift was accelerated by benchmark competitions, "
        "notably the ICML 2013 Challenges in Representation Learning introduced by Goodfellow et al. [1].")
    body(story,
        "Despite dramatic gains on benchmark datasets, practical real-time FER systems operating in "
        "unconstrained live webcam environments encounter formidable engineering obstacles: high intra-class "
        "variance caused by head pose and illumination shifts, inter-class morphological overlap between "
        "affective states (such as Fear and Surprise), severe benchmark class imbalance, and rapid "
        "frame-to-frame prediction flickering. This project develops an integrated solution addressing "
        "each of these operational challenges.")

    h2(story, "1.2  Problem Statement", key="sec_1_2")
    body(story,
        "Training deep neural networks with standard Categorical Cross-Entropy (CCE) loss on benchmark datasets "
        "exhibiting severe class imbalance yields biased decision boundaries. In the FER2013 benchmark [1], "
        "the Happy class contains 7,215 training images whereas the Disgust class contains only 436 \u2014 a "
        "disparity ratio of 16.5:1. Under standard cross-entropy, the massive volume of easily classified "
        "majority-class samples dominates the gradient descent updates, suppressing gradient signals from "
        "rare, critical emotions like Disgust and Fear. Consequently, models achieve seemingly acceptable "
        "aggregate accuracy while exhibiting near-zero recall on minority classes.")
    body(story,
        "Furthermore, unconstrained video streams exhibit temporal instability: instantaneous facial "
        "micro-movements, lighting fluctuations, and minor pose perturbations cause unbuffered frame-level "
        "classifiers to oscillate rapidly between mutually exclusive labels (e.g., Happy \u2192 Neutral \u2192 "
        "Sad \u2192 Happy within 150 ms). This prediction flickering severely degrades usability in interactive "
        "applications. Existing literature typically evaluates static image accuracy while neglecting the "
        "temporal stability and real-time throughput required for consumer hardware deployment.")

    h2(story, "1.3  Goals and Objectives", key="sec_1_3")
    body(story,
        "The primary goal of this capstone research is to engineer, empirically validate, and deploy a robust, "
        "real-time facial emotion recognition system that mitigates dataset class imbalance and eliminates "
        "temporal prediction flickering on consumer-grade laptop hardware. The specific measurable objectives are:")
    for o in [
        "<b>O1:</b> Design and construct a 4-Stage Deep Convolutional Neural Network from scratch, optimized "
        "specifically for 48\u00d748 grayscale facial expressions without external transfer-learning overhead.",
        "<b>O2:</b> Formulate and implement Categorical Focal Loss (\u03b3 = 2.0) with Label Smoothing (\u03b5 = 0.1) "
        "to downweight easy majority samples and prevent overconfident fitting to noisy web-crawled labels.",
        "<b>O3:</b> Apply static balanced class-frequency weighting to ensure equitable gradient emphasis across all classes.",
        "<b>O4:</b> Integrate Google MediaPipe BlazeFace [3, 15] for ultra-fast, pose-tolerant face bounding-box localization.",
        "<b>O5:</b> Implement a 10-frame FIFO temporal plurality buffer (333 ms window at 30 FPS) to eliminate live flickering.",
        "<b>O6:</b> Empirically evaluate the architecture on 7,178 unseen FER2013 test images, evaluating precision, recall, "
        "F1-score, and confusion matrix structures against published baselines.",
        "<b>O7:</b> Conduct a systematic ablation study isolating the contribution of each algorithmic innovation.",
    ]:
        bullet(story, o)

    h2(story, "1.4  Motivation", key="sec_1_4")
    body(story,
        "This project is motivated by the necessity of moving affective computing from offline academic benchmarking "
        "into robust, real-world utility. While transfer learning from ImageNet models (such as VGG-16 or ResNet-50) "
        "is common, these networks contain tens of millions of parameters, process RGB 224\u00d7224 tensors, and incur "
        "high inference latencies that bottleneck consumer CPUs. By demonstrating that a lightweight, custom 4-Stage "
        "ConvNet (4.83M parameters) operating on compact 48\u00d748 grayscale inputs can achieve 63.51% test accuracy \u2014 "
        "within 1.49% of the human annotation benchmark (65 \u00b1 5%) [1] \u2014 this work establishes an efficient, "
        "accessible baseline for resource-constrained edge computing.")

    h2(story, "1.5  Scope of the Completed Project", key="sec_1_5")
    body(story,
        "The project scope encompasses: (1) single primary face emotion recognition in live video streams; "
        "(2) classification across the seven canonical Ekman emotions (Angry, Disgust, Fear, Happy, Sad, Surprise, "
        "Neutral); (3) local CPU execution on Windows 10/11 operating systems without cloud dependencies; and (4) an "
        "automated, single-click desktop deployment interface (`run_webcam.bat`). Multi-face simultaneous classification, "
        "acoustic speech prosody fusion, and continuous valence-arousal regression are designated for future work.")

    h2(story, "1.6  Research Contributions", key="sec_1_6")
    body(story, "The technical contributions of this capstone research are summarised as follows:")
    for c in [
        "<b>Balanced Focal-Smoothing Loss Stack:</b> A synergistic loss function formulation combining "
        "Categorical Focal Loss (\u03b3=2.0), Label Smoothing (\u03b5=0.1), and class-frequency inverse weighting that "
        "improves test accuracy by +6.17 percentage points over standard Cross-Entropy.",
        "<b>Efficient 4-Stage ConvNet Architecture:</b> A compact custom architecture incorporating stacked 3\u00d73 "
        "convolutions, Batch Normalisation, progressive spatial Dropout (25%\u219240%), and Global Average Pooling that "
        "achieves competitive accuracy with 4.83M parameters and zero transfer-learning overhead.",
        "<b>Ultra-Fast Real-Time Pipeline:</b> An integrated inference pipeline marrying MediaPipe BlazeFace with "
        "a 10-frame FIFO plurality buffer, achieving 28\u201330 FPS sustained throughput and zero perceptible flicker on laptop CPU.",
    ]:
        bullet(story, c)

    h2(story, "1.7  Software Repository and Demonstration Links", key="sec_1_7")
    body(story,
        "In compliance with academic reproducibility standards, all implementation source code, pre-trained neural "
        "network weights, evaluation scripts, and batch deployment files are publicly hosted in the following repository:")
    bullet(story, f"<b>GitHub Repository:</b> <font color='#0000AA'><u>{GITHUB_URL}</u></font>")
    body(story,
        "A full live-action video demonstration illustrating the real-time webcam detection system, head pose stability, "
        "and responsiveness across all emotional expressions is accessible at:")
    bullet(story, f"<b>Demonstration Video:</b> <font color='#0000AA'><u>{DEMO_URL}</u></font>")

    h2(story, "1.8  Report Organisation", key="sec_1_8")
    body(story,
        "The remainder of this report is organised as follows: Chapter 2 reviews foundational literature in affective "
        "computing, face detection, and imbalanced loss formulations. Chapter 3 presents software specifications, UML "
        "use case modelling, and system architecture. Chapter 4 details the data preprocessing pipeline, ConvNet design, "
        "Focal Loss derivation, and real-time smoothing logic. Chapter 5 provides empirical evaluation results, confusion "
        "matrix breakdowns, ablation analysis, and operational latency measurements. Chapter 6 examines technical and ethical "
        "limitations. Chapter 7 outlines future enhancements, and Chapter 8 concludes the report.")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # CHAPTER 2: LITERATURE REVIEW
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Chapter 2: Literature Review", key="ch2")

    h2(story, "2.1  Psychological Foundations of Emotion Recognition", key="sec_2_1")
    body(story,
        "The automated classification of facial expressions rests upon the psychological taxonomy established by "
        "Paul Ekman and Wallace Friesen [12]. Their seminal cross-cultural investigations demonstrated that six primary "
        "affective states \u2014 Anger, Disgust, Fear, Happiness, Sadness, and Surprise \u2014 are universally expressed "
        "and decoded through identical facial muscle configurations across literate and pre-literate cultures alike. "
        "To provide an objective anatomical standard, Ekman and Friesen formulated the Facial Action Coding System (FACS), "
        "decomposing facial movements into distinct Action Units (AUs) governed by specific underlying muscles (e.g., "
        "AU1: Inner Brow Raiser, AU12: Lip Corner Puller). In affective computing, Neutral is conventionally included "
        "as a baseline seventh class.")

    h2(story, "2.2  Classical Computer Vision Approaches", key="sec_2_2")
    body(story,
        "Prior to deep learning, FER systems relied on a two-stage pipeline: hand-crafted spatial feature extraction "
        "followed by shallow discriminative classification. Classical feature extractors included Histograms of "
        "Oriented Gradients (HOG) by Shan et al. [13], which capture local edge orientations, and Local Binary Patterns "
        "(LBP) by Ojala et al. [14], which encode micro-texture variations across pixel neighbourhoods. Extracted feature "
        "vectors were classified using Support Vector Machines (SVMs) or Random Forests. While computationally frugal, "
        "hand-crafted descriptors exhibited poor generalisation across unseen subjects, varying head orientations, and "
        "illumination changes due to their inability to learn non-linear spatial hierarchies.")

    h3(story, "2.2.1  Mathematical Formulations of Classical Feature Descriptors")
    body(story,
        "To understand the limitations of classical approaches, it is instructive to examine the mathematical "
        "formulations of HOG and LBP. In the HOG descriptor proposed by Dalal and Triggs and applied to FER by Shan et al. [13], "
        "first-order image gradients are computed across horizontal and vertical axes:")
    body_left(story, "<b>G_x(x, y) = I(x+1, y) - I(x-1, y),    G_y(x, y) = I(x, y+1) - I(x, y-1)</b>    (Equation 2.1)")
    body(story,
        "The corresponding gradient magnitude M(x, y) and orientation θ(x, y) are derived as:")
    body_left(story, "<b>M(x, y) = √(G_x^2 + G_y^2),    θ(x, y) = arctan(G_y / G_x)</b>    (Equation 2.2)")
    body(story,
        "Gradient orientations are discretized into 9 angular bins within local 8×8 pixel spatial cells. While "
        "effective at capturing dominant directional edges (such as eyebrow slants), HOG is fundamentally rigid and "
        "sensitive to out-of-plane rotation.")
    body(story,
        "Similarly, the basic Local Binary Pattern descriptor introduced by Ojala et al. [14] computes a circular binary code "
        "by thresholding surrounding pixel intensities against a central pixel intensity I_c:")
    body_left(story, "<b>LBP_{P, R}(x_c, y_c) = ∑_{p=0}^{P-1} s(I_p - I_c) × 2^p</b>    (Equation 2.3)")
    body(story,
        "where s(u) = 1 if u ≥ 0, else 0, across P circular neighbours at radius R. Because these hand-engineered "
        "descriptors cannot adaptively adjust their filter kernels to dataset distributions, their representation capacity "
        "remains constrained relative to hierarchical convolutional networks.")

    h2(story, "2.3  Deep Learning Architectures for FER", key="sec_2_3")
    body(story,
        "Convolutional Neural Networks revolutionised FER by uniting feature extraction and classification into a unified, "
        "gradient-trained optimization problem. Prominent architectures applied to FER include VGG-16 by Simonyan and "
        "Zisserman [5], ResNet-50 by He et al. [9], and EfficientNet by Tan and Le [6]. While fine-tuning deep ImageNet "
        "models yields high test accuracies (often 66\u201370% on FER2013), these architectures were originally developed "
        "for 1,000-class RGB object classification. When applied to 48\u00d748 single-channel grayscale facial expressions, "
        "their large parameter counts (e.g., 138M for VGG-16, 25M for ResNet-50) incur unnecessary memory footprints and "
        "high inference latencies, making them ill-suited for real-time CPU deployment.")

    h2(story, "2.4  FER2013 Benchmark Dataset Characteristics", key="sec_2_4")
    body(story,
        "Introduced by Goodfellow et al. for the ICML 2013 Challenges in Representation Learning [1], FER2013 comprises "
        "35,887 grayscale images resized to 48\u00d748 pixels. The dataset was constructed by executing automated web search "
        "queries across 184 emotion-related keywords, followed by human verification to reject spurious images. The benchmark "
        "is split into 28,709 training images and two held-out partitions of 3,589 images each: PublicTest and PrivateTest. "
        "In standardized evaluation protocols, these two partitions are combined into a unified 7,178-image test set.")
    body(story,
        "A critical property of FER2013 is its realistic difficulty. In their original benchmark paper, Goodfellow et al. [1] "
        "reported human annotator accuracy on a subset of FER2013 images at approximately 65 \u00b1 5%. This benchmark "
        "reflects the inherent ambiguity of static, in-the-wild facial crops devoid of conversational context. Crucially, "
        "this 65% figure represents an empirical human agreement level rather than an unbreakable theoretical ceiling; "
        "multi-model ensembles and heavy transfer learning architectures have recorded scores slightly above 70%.")

    h2(story, "2.5  The Challenge of Class Imbalance in FER", key="sec_2_5")
    body(story,
        "Natural human emotional expression is heavily skewed toward positive and neutral states. This sociological "
        "reality is mirrored in FER2013: Happy contains 7,215 training images (25.1%), whereas Disgust contains merely "
        "436 training images (1.52%) \u2014 a 16.5-fold disproportion. When trained with conventional cross-entropy loss, "
        "the gradient contributions from Happy overwhelm those from Disgust, causing standard models to classify ambiguous "
        "disgust expressions as angry or sad. Data oversampling techniques (such as SMOTE) generate synthetic pixel interpolations "
        "that lack anatomical facial validity, motivating algorithmic loss-level interventions.")

    h2(story, "2.6  Loss Functions for Imbalanced Classification", key="sec_2_6")
    body(story,
        "Focal Loss, introduced by Lin et al. [2] for dense object detection in RetinaNet, dynamically reshapes the "
        "loss surface by multiplying the cross-entropy loss by a modulating factor (1 \u2212 p_t)^\u03b3. For well-classified "
        "samples where the model's estimated probability p_t is high, the modulating factor approaches zero, drastically "
        "attenuating the sample's loss contribution. Conversely, for difficult, poorly classified samples where p_t is small, "
        "the modulating factor approaches unity, preserving gradient force. In this research, Focal Loss is paired with "
        "Label Smoothing (\u03b5 = 0.1), first introduced by Szegedy et al. [16] in Inception-v3, which prevents overconfidence "
        "on web-crawled label noise by redistributing uniform probability mass across all classes.")

    h2(story, "2.7  Real-Time Face Detection Pipelines", key="sec_2_7")
    body(story,
        "Real-time emotion classification requires an upstream face detection mechanism. The classical Viola-Jones detector [4], "
        "based on AdaBoost and Haar cascades, executes rapidly on CPUs (~10 ms) but suffers from high false-positive rates "
        "in cluttered environments and fails when face yaw exceeds \u00b115\u00b0. Multi-task Cascaded CNNs (MTCNN) improve "
        "accuracy but require multiple neural passes that incur 40\u201380 ms latency on CPU. Google MediaPipe BlazeFace [3, 15] "
        "resolves this bottleneck by utilizing a single-shot anchor-based detector with an ultra-lightweight feature extractor "
        "tailored for mobile GPUs and consumer CPUs, extracting high-precision bounding boxes in 3\u20135 ms across \u00b145\u00b0 yaw.")

    h2(story, "2.8  Research Gap and Technical Motivation", key="sec_2_8")
    body(story,
        "While prior studies have investigated Focal Loss or lightweight CNNs in isolation, existing literature lacks a "
        "rigorously evaluated, end-to-end framework combining: (1) a custom 4-Stage ConvNet trained from scratch on 48\u00d748 "
        "inputs; (2) a multi-tiered loss formulation integrating Focal Loss, Label Smoothing, and class-frequency weights; "
        "(3) sub-5 ms MediaPipe detection; and (4) temporal plurality smoothing for flicker-free live video. This project "
        "directly bridges these research and deployment gaps.")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # CHAPTER 3: SYSTEM SPECIFICATION AND DESIGN
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Chapter 3: System Specification and Design", key="ch3")

    h2(story, "3.1  Software Requirements Specification", key="sec_3_1")
    body(story, "The system\u2019s operational requirements are formalised as follows:")
    for fr in [
        "<b>FR-01 (Video Acquisition):</b> The system shall acquire continuous video frames from the primary webcam "
        "at a minimum resolution of 1280\u00d7720 pixels at \u2265 28 FPS.",
        "<b>FR-02 (Face Detection):</b> The system shall detect human faces within each video frame using MediaPipe BlazeFace "
        "with an inference latency \u2264 6 ms on CPU.",
        "<b>FR-03 (Primary Face Selection):</b> When multiple faces are present, the system shall select the single face "
        "exhibiting the highest detection confidence score for emotion inference.",
        "<b>FR-04 (Region Preprocessing):</b> The detected facial crop shall be converted to single-channel grayscale, "
        "bilinearly resized to 48\u00d748 pixels, normalized to [0.0, 1.0], and reshaped to a 4D tensor (1, 48, 48, 1).",
        "<b>FR-05 (Emotion Classification):</b> The 4-Stage CNN shall output a 7-dimensional probability distribution "
        "corresponding to the Ekman emotion categories in \u2264 20 ms.",
        "<b>FR-06 (Temporal Smoothing & Display):</b> The system shall maintain a 10-frame FIFO buffer and render the "
        "stabilised plurality emotion label, confidence score, and bounding box overlay on the live feed.",
        "<b>FR-07 (Session Termination):</b> The user shall be able to terminate the application cleanly by pressing the 'q' key.",
    ]:
        bullet(story, fr)

    sp(story, 4)
    body(story, "Non-functional requirements governing system reliability and usability are:")
    for nfr in [
        "<b>NFR-01 (Throughput):</b> The end-to-end pipeline shall sustain a minimum throughput of 20 FPS on a modern multi-core CPU.",
        "<b>NFR-02 (Accuracy):</b> The CNN classifier shall exceed 60% test accuracy on the 7,178-image FER2013 test set.",
        "<b>NFR-03 (Offline Autonomy):</b> The system shall execute entirely on local hardware with zero external internet dependencies.",
        "<b>NFR-04 (Usability):</b> The software shall launch via a single desktop batch script without manual command-line configuration.",
    ]:
        bullet(story, nfr)

    h2(story, "3.2  Hardware and Software Specifications", key="sec_3_2")
    story.append(BookmarkFlowable("tab_hw"))
    hw_data = [
        [Paragraph("<b>Component Layer</b>", _S['body_left']),
         Paragraph("<b>Development / Training Environment</b>", _S['body_left']),
         Paragraph("<b>Target Deployment Environment</b>", _S['body_left'])],
        [PL("Operating System"), PL("Windows 11 / WSL2 (Ubuntu 22.04 LTS)"), PL("Windows 10 / 11 (64-bit)")],
        [PL("Central Processor (CPU)"), PL("11th Gen Intel Core i5-1135G7 @ 2.40GHz"), PL("Intel Core i3/i5 or AMD Ryzen equivalent")],
        [PL("Graphics Processor (GPU)"), PL("NVIDIA GeForce RTX 2050 (4 GB VRAM)"), PL("Not required (CPU inference supported)")],
        [PL("System Memory (RAM)"), PL("16 GB DDR4 @ 3200 MHz"), PL("4 GB minimum (8 GB recommended)")],
        [PL("Deep Learning Library"), PL("TensorFlow 2.15.0 / Keras 2.15.0 (CUDA 12.2)"), PL("TensorFlow 2.15.0 (CPU / OneDNN)")],
        [PL("Computer Vision Tools"), PL("Google MediaPipe 0.10.9, OpenCV 4.8.0"), PL("Google MediaPipe 0.10.9, OpenCV 4.8.0")],
        [PL("Runtime Environment"), PL("Python 3.10.11 (virtual environment)"), PL("Python 3.10.11 (venv_win standalone)")],
    ]
    story.append(KeepTogether(plain_table(hw_data, [BW*0.25, BW*0.40, BW*0.35])))
    caption(story, "Table 3.1: Hardware and Software System Specifications")

    h2(story, "3.3  Use Case Modeling", key="sec_3_3")
    body(story,
        "Figure 3.1 illustrates the UML Use Case diagram for the system. The primary actor is the User, "
        "who interacts directly with three goal-level use cases: Launch Real-Time Detection (UC-1), View Live "
        "Emotion Overlay (UC-2), and Terminate Session (UC-6). The internal algorithmic stages \u2014 Face Detection (UC-3), "
        "ROI Preprocessing (UC-4), and Emotion Classification (UC-5) \u2014 are structured as subordinate use cases "
        "connected via «include» dependencies, reflecting that live rendering strictly depends upon their execution.")
    fig(story, "Report/figures/figure_use_case_diagram.png", w_frac=0.85, h_frac=0.62,
        cap_text="Figure 3.1: Use Case Diagram for Real-Time Facial Emotion Recognition System.", key="fig_uc")

    story.append(BookmarkFlowable("tab_uc"))
    uc_table_data = [
        [Paragraph("<b>Use Case ID & Title</b>", _S['body_left']),
         Paragraph("<b>Primary Actor</b>", _S['body_left']),
         Paragraph("<b>Pre-conditions</b>", _S['body_left']),
         Paragraph("<b>Post-conditions</b>", _S['body_left'])],
        [PL("UC-1: Launch System"), PL("User"), PL("Webcam connected, venv initialised"), PL("Video stream displayed at 720p")],
        [PL("UC-2: View Emotion Overlay"), PL("User"), PL("Face present in video frame"), PL("Bounding box & label rendered")],
        [PL("UC-3: Detect Face Region"), PL("System («include»)"), PL("Video frame acquired in RGB"), PL("Bounding box [xmin, ymin, w, h] returned")],
        [PL("UC-4: Preprocess Face ROI"), PL("System («include»)"), PL("Valid bounding box extracted"), PL("Normalized (1, 48, 48, 1) tensor produced")],
        [PL("UC-5: Classify Emotion"), PL("System («include»)"), PL("48\u00d748 tensor ready"), PL("7-class probability vector generated")],
        [PL("UC-6: Terminate Session"), PL("User"), PL("Application window in active focus"), PL("Camera released, window destroyed cleanly")],
    ]
    story.append(KeepTogether(plain_table(uc_table_data, [BW*0.25, BW*0.20, BW*0.27, BW*0.28])))
    caption(story, "Table 3.2: Use Case Specifications and Operational Contracts")

    h2(story, "3.4  Five-Stage Pipeline Architecture", key="sec_3_4")
    body(story,
        "Figure 3.2 depicts the high-level five-stage pipeline architecture. The stages are explicitly annotated "
        "with their intermediate data representations: raw 720p BGR video frames \u2192 bounding box coordinates \u2192 "
        "preprocessed 48\u00d748 single-channel tensors \u2192 7-class softmax probability distributions \u2192 "
        "stabilised visual overlays rendered onto the output stream.")
    fig(story, "Report/figures/figure_system_architecture.png", w_frac=0.95, h_frac=0.40,
        cap_text="Figure 3.2: Five-Stage Real-Time Pipeline Architecture and Intermediate Data Flow.", key="fig_arch")

    h2(story, "3.5  Interaction Design: UML Sequence Diagram", key="sec_3_5")
    body(story,
        "Figure 3.3 illustrates the dynamic message exchange across six system lifelines: the User, Application "
        "Controller, Camera Feed, MediaPipe Detector, ROI Preprocessor, and Emotion CNN. Frame acquisition (readFrame) "
        "executes synchronously within the iterative frame loop. If no face is localized by MediaPipe, the controller "
        "bypasses the CNN inference stage, holding the prior stable buffer state and preventing unnecessary CPU cycles.")
    fig(story, "Report/figures/figure_sequence_diagram.png", w_frac=0.92, h_frac=0.64,
        cap_text="Figure 3.3: UML Sequence Diagram Illustrating Synchronous Real-Time Detection Loop.", key="fig_seq")

    h2(story, "3.6  Data Flow and Storage Specifications", key="sec_3_6")
    body(story,
        "To adhere to strict privacy-by-design standards, the application operates with zero persistent media storage. "
        "Incoming video frames are processed entirely in volatile RAM. Once processed and displayed, each frame buffer "
        "is immediately overwritten by the subsequent capture. The only persistent disk artefact utilized during runtime "
        "is the static neural network weight file (`model/emotion_model.h5`), which is opened read-only upon launch.")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # CHAPTER 4: METHODOLOGY
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Chapter 4: Methodology", key="ch4")

    h2(story, "4.1  Dataset Composition and Stratification", key="sec_4_1")
    body(story,
        "The project utilizes the FER2013 dataset [1] comprising 35,887 images. The training directory contains "
        "28,709 images, and the official evaluation partition contains 7,178 images. Figure 2.1 plots the exact "
        "class breakdown across both partitions. Happy constitutes the dominant class with 7,215 training images "
        "(25.1%) and 1,774 test images (24.7%). In contrast, Disgust constitutes only 436 training images (1.52%) "
        "and 111 test images (1.55%), establishing a 16.5:1 class disparity ratio.")
    fig(story, "Report/figures/figure_dataset_distribution.png", w_frac=0.88, h_frac=0.45,
        cap_text="Figure 2.1: Class Sample Distribution for Training and Test Partitions in FER2013.", key="fig_dist")
    body(story,
        "For training validation, the 28,709 training images were partitioned into 24,402 training samples (85%) "
        "and 4,307 validation samples (15%) using stratified random sampling to preserve exact class proportion "
        "ratios across both splits.")

    h2(story, "4.2  Data Preprocessing Pipeline", key="sec_4_2")
    body(story,
        "Every raw image undergoing training and inference passes through four standardized preprocessing transformations: "
        "(1) Conversion to single-channel 8-bit grayscale, eliminating arbitrary skin pigmentation and room colour biases; "
        "(2) Bilinear interpolation resizing to 48\u00d748 spatial resolution; (3) Pixel intensity division by 255.0 to map "
        "values into the floating-point range [0.0, 1.0]; and (4) Tensor reshaping to append batch and channel dimensions (N, 48, 48, 1).")

    h2(story, "4.3  Data Augmentation Strategy", key="sec_4_3")
    body(story,
        "To synthesize expression variance and prevent memorisation, on-the-fly data augmentation was applied "
        "exclusively during training using Keras ImageDataGenerator. Table 4.1 documents the exact transformation parameters.")
    story.append(BookmarkFlowable("tab_aug"))
    aug_data = [
        [Paragraph("<b>Augmentation Parameter</b>", _S['body_left']),
         Paragraph("<b>Transformation Range</b>", _S['body_left']),
         Paragraph("<b>Physical Invariance Learned</b>", _S['body_left'])],
        [PL("Rotation (rotation_range)"), PL("\u00b1 20 degrees"), PL("Head tilt and camera yaw misalignment")],
        [PL("Horizontal Shift (width_shift_range)"), PL("\u00b1 15% (fraction of width)"), PL("Horizontal centering variation in crop")],
        [PL("Vertical Shift (height_shift_range)"), PL("\u00b1 15% (fraction of height)"), PL("Vertical alignment and chin positioning")],
        [PL("Shear Angle (shear_range)"), PL("0.15 radians (~8.6 degrees)"), PL("Perspective distortion from angled cameras")],
        [PL("Zoom (zoom_range)"), PL("\u00b1 15% (scale [0.85, 1.15])"), PL("Subject proximity and face scale changes")],
        [PL("Horizontal Flip (horizontal_flip)"), PL("Boolean (True, 50% probability)"), PL("Bilateral facial expression symmetry")],
        [PL("Brightness (brightness_range)"), PL("Multiplier in [0.8, 1.2]"), PL("Ambient room lighting fluctuations")],
        [PL("Fill Mode (fill_mode)"), PL("nearest"), PL("Boundary pixel padding")],
    ]
    story.append(KeepTogether(plain_table(aug_data, [BW*0.35, BW*0.30, BW*0.35])))
    caption(story, "Table 4.1: Data Augmentation Hyperparameters and Operational Ranges")

    h2(story, "4.4  Static Balanced Class Weighting", key="sec_4_4")
    body(story,
        "To counteract class frequency disparity, balanced heuristic class weights were computed from the 28,709 "
        "training samples using King and Zeng\u2019s formulation [17]:")
    body_left(story, "<b>w_c = N_total / (K \u00d7 N_c)</b>    (Equation 4.1)")
    body(story,
        "where N_total = 28,709, K = 7 classes, and N_c denotes the sample count for class c. Evaluating Equation 4.1 yields:")
    bullet(story, "<b>Disgust (N = 436):</b> w_Disgust = 28709 / (7 \u00d7 436) \u2248 <b>9.41</b>")
    bullet(story, "<b>Happy (N = 7,215):</b> w_Happy = 28709 / (7 \u00d7 7215) \u2248 <b>0.57</b>")
    body(story,
        "These static class weights were supplied to the training loop, scaling per-sample loss values before reduction.")

    h2(story, "4.5  Loss Formulation: Focal Loss with Label Smoothing", key="sec_4_5")
    body(story,
        "To regularise against label noise in web-scraped data, Label Smoothing (\u03b5 = 0.1) is applied across all K = 7 classes [16]:")
    body_left(story, "<b>\u1ef9_c = y_c(1 \u2212 \u03b5) + (\u03b5 / K)</b>    (Equation 4.2)")
    body(story,
        "For a ground-truth class, the target probability is softened to \u1ef9_true = 1.0(0.9) + 0.1/7 \u2248 <b>0.9143</b>, "
        "while incorrect classes receive \u1ef9_other = 0.1/7 \u2248 <b>0.0143</b>. This prevents gradient explosion on mislabelled faces.")
    body(story,
        "Focal Loss modulates the cross-entropy objective via a dynamic factor (1 \u2212 p_c)^\u03b3 with \u03b3 = 2.0 [2]:")
    body_left(story, "<b>L_FL = \u2212 \u2211_{c=1}^{7} \u1ef9_c (1 \u2212 p_c)^\u03b3 log(p_c)</b>    (Equation 4.3)")
    body(story,
        "For an easy, well-classified sample where p_c = 0.9, the modulation factor evaluates to (1 \u2212 0.9)^2 = 0.01 (a 99% reduction "
        "in loss weight). For a hard, poorly classified sample where p_c = 0.1, the factor evaluates to (1 \u2212 0.1)^2 = 0.81. "
        "The ratio of loss modulation factors between hard and easy instances is 0.81 / 0.01 = <b>81:1</b>, compelling backpropagation "
        "to prioritize difficult emotional patterns.")

    h3(story, "4.5.1  Mathematical Backpropagation Gradient Derivation for Focal Loss")
    body(story,
        "A rigorous understanding of Focal Loss requires differentiating Equation 4.3 with respect to the pre-activation "
        "logits z_i. Applying the chain rule through the softmax activation p_i = exp(z_i) / ∑_j exp(z_j), the derivative "
        "of the loss with respect to logit z_i decomposes into:")
    body_left(story, "<b>∂L_FL / ∂z_i = ∑_{c=1}^{K} (∂L_FL / ∂p_c) × (∂p_c / ∂z_i)</b>    (Equation 4.4)")
    body(story,
        "Recalling that ∂p_c / ∂z_i = p_c(δ_{ic} - p_i), where δ_{ic} is the Kronecker delta, differentiating "
        "the focal loss term L_c = -(1 - p_c)^γ log(p_c) with respect to p_c produces:")
    body_left(story, "<b>∂L_c / ∂p_c = γ(1 - p_c)^{γ - 1} log(p_c) - ((1 - p_c)^γ / p_c)</b>    (Equation 4.5)")
    body(story,
        "Notice that as the predicted probability p_c approaches 1.0 (an easy, well-classified sample), the term (1 - p_c)^γ "
        "drives the gradient smoothly to zero. Conversely, for misclassified samples where p_c is low, the gradient remains "
        "substantial. When combined with Label Smoothing (Equation 4.2), where target mass ỹ_c > 0 for all classes, the "
        "resulting gradient vector exerts a gentle regularising force toward the uniform distribution, preventing the network "
        "from driving logit magnitudes toward infinity.")

    h2(story, "4.6  4-Stage Deep ConvNet Architecture", key="sec_4_6")
    body(story,
        "The custom neural network architecture comprises four progressive convolutional blocks followed by a dense "
        "classification head. Table 4.2 documents the layer specifications, output tensor shapes, and exact parameter counts.")
    story.append(BookmarkFlowable("tab_arch"))
    arch_data = [
        [Paragraph("<b>Stage / Layer</b>", _S['body_left']),
         Paragraph("<b>Layer Specifications (Kernel, Strides, Padding)</b>", _S['body_left']),
         Paragraph("<b>Output Shape</b>", _S['body_left']),
         Paragraph("<b>Parameter Count</b>", _S['body_left'])],
        [PL("Input"), PL("Grayscale Image Tensor (48\u00d748\u00d71)"), PL("(48, 48, 1)"), PL("0")],
        [PL("Block 1"), PL("Conv2D(64, 3\u00d73, same) + BN + ReLU\nConv2D(64, 3\u00d73, same) + BN + ReLU\nMaxPool2D(2\u00d72, stride 2) + Dropout(0.25)"), PL("(24, 24, 64)"), PL("38,080")],
        [PL("Block 2"), PL("Conv2D(128, 3\u00d73, same) + BN + ReLU\nConv2D(128, 3\u00d73, same) + BN + ReLU\nMaxPool2D(2\u00d72, stride 2) + Dropout(0.30)"), PL("(12, 12, 128)"), PL("222,464")],
        [PL("Block 3"), PL("Conv2D(256, 3\u00d73, same) + BN + ReLU\nConv2D(256, 3\u00d73, same) + BN + ReLU\nMaxPool2D(2\u00d72, stride 2) + Dropout(0.35)"), PL("(6, 6, 256)"), PL("887,296")],
        [PL("Block 4"), PL("Conv2D(512, 3\u00d73, same) + BN + ReLU\nConv2D(512, 3\u00d73, same) + BN + ReLU\nMaxPool2D(2\u00d72, stride 2) + Dropout(0.40)"), PL("(3, 3, 512)"), PL("3,544,064")],
        [PL("Head (GAP)"), PL("GlobalAveragePooling2D()\nDense(256, ReLU) + BN + Dropout(0.50)\nDense(7, Softmax)"), PL("(7,)"), PL("134,151")],
        [Paragraph("<b>Total System</b>", _S['body_left']),
         Paragraph("<b>4-Stage Deep ConvNet (Trainable: 4,821,703 | Non-trainable: 4,352)</b>", _S['body_left']),
         PL("(7,)"),
         Paragraph("<b>4,826,055</b>", _S['body_left'])],
    ]
    story.append(KeepTogether(plain_table(arch_data, [BW*0.16, BW*0.48, BW*0.18, BW*0.18])))
    caption(story, "Table 4.2: Upgraded 4-Stage ConvNet Layer Specifications and Parameter Allocations")

    h3(story, "4.6.1  Spatial Receptive Field and Feature Hierarchy Evolution")
    body(story,
        "A critical design property of the 4-Stage ConvNet is the progressive expansion of the theoretical receptive field "
        "across network depth. Two consecutive 3×3 convolutional layers possess an effective receptive field of 5×5 pixels. "
        "With four stages separated by 2×2 max-pooling operations (stride 2), the receptive field expands geometrically:")
    bullet(story, "<b>Block 1 (24×24 resolution):</b> Receptive field = 5×5 pixels. Captures localized micro-textures: eyebrow edges, skin wrinkles, iris boundaries.")
    bullet(story, "<b>Block 2 (12×12 resolution):</b> Receptive field = 14×14 pixels. Encompasses intermediate facial structures: eye outlines, nasolabial folds, lip contours.")
    bullet(story, "<b>Block 3 (6×6 resolution):</b> Receptive field = 32×32 pixels. Integrates holistic facial regions: relation between inner brow raise and open mouth.")
    bullet(story, "<b>Block 4 (3×3 resolution):</b> Receptive field = 68×68 pixels. Spans the entire 48×48 facial crop, encoding global expression configurations.")

    h2(story, "4.7  Regularisation Stack", key="sec_4_7")
    body(story,
        "Overfitting is constrained via a four-tier regularisation stack: (1) <b>Batch Normalisation:</b> applied after "
        "every convolutional and dense transformation, stabilising gradient backpropagation; (2) <b>Progressive Dropout:</b> "
        "scaling from 0.25 in Block 1 to 0.50 in the dense head, preventing co-adaptation of complex feature channels; "
        "(3) <b>L2 Weight Decay:</b> penalising large weight magnitudes with \u03bb = 1.0\u00d710\u207b\u2074 across all kernel tensors; "
        "and (4) <b>Global Average Pooling:</b> replacing conventional Flatten layers, reducing dense classification head "
        "parameters from 1,179,648 down to 131,072 (a 9-fold parameter compression).")

    h2(story, "4.8  Training Protocol and Hyperparameters", key="sec_4_8")
    body(story,
        "Training was executed in WSL2 on an NVIDIA RTX 2050 GPU using the Adam optimiser (initial lr = 1.0\u00d710\u207b\u00b3, "
        "\u03b2_1 = 0.9, \u03b2_2 = 0.999) with a mini-batch size of 32. Two dynamic callbacks governed optimization: "
        "ReduceLROnPlateau (factor = 0.5, patience = 4 epochs, min_lr = 1.0\u00d710\u207b\u2077) and EarlyStopping "
        "(patience = 12 epochs, monitoring validation accuracy). Training stopped at epoch 52, taking ~3.5 hours.")

    h2(story, "4.9  Training Convergence Analysis", key="sec_4_9")
    body(story,
        "Figure 4.1 displays the training and validation trajectories. Peak validation accuracy (63.7%) was achieved "
        "at epoch 40, followed by 12 epochs of plateau that triggered EarlyStopping at epoch 52. The final validation loss "
        "converged to 1.001, with an empirical generalisation gap of 5.4 percentage points relative to training accuracy (69.1%).")
    fig(story, "Report/figures/figure_training_curves.png", w_frac=0.92, h_frac=0.42,
        cap_text="Figure 4.1: Training and Validation Accuracy (a) and Focal Loss (b) Across 52 Epochs.", key="fig_train")

    h2(story, "4.10  Real-Time Inference Engine", key="sec_4_10")
    body(story,
        "In `live_detect_pro.py`, the live inference loop executes in four tightly coupled stages: (1) Frame capture "
        "via OpenCV VideoCapture at 720p; (2) MediaPipe BlazeFace face detection in RGB format (3\u20135 ms); (3) Face crop extraction, "
        "grayscale conversion, bilinear resizing to 48\u00d748, and intensity normalisation; and (4) Model inference on CPU (12\u201318 ms).")

    h2(story, "4.11  Temporal Prediction Smoothing Protocol", key="sec_4_11")
    body(story,
        "Raw frame predictions are pushed into a 10-frame FIFO deque (`collections.deque(maxlen=10)`). The displayed "
        "emotion is determined by plurality voting (`Counter(deque).most_common(1)[0][0]`). At 30 FPS, 10 frames represent a "
        "333 ms temporal window. When a subject transitions to a new expression, 4 to 6 frames (~150\u2013200 ms) are required "
        "for the emerging emotion to achieve plurality within the window. Full buffer replacement takes 333 ms. This provides "
        "flawless smoothing against single-frame blinks while reacting promptly to genuine affective shifts.")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # CHAPTER 5: RESULTS AND EVALUATION
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Chapter 5: Results and Evaluation", key="ch5")

    h2(story, "5.1  Experimental Setup and Protocol", key="sec_5_1")
    body(story,
        "The model was evaluated on the complete 7,178-image FER2013 test set (combining the PublicTest and PrivateTest "
        "subsets). Evaluation was performed strictly on CPU in the Windows deployment environment (`venv_win`), confirming "
        "identical inference numerical behaviour across training and production platforms.")

    h2(story, "5.2  Overall Classification Performance", key="sec_5_2")
    story.append(BookmarkFlowable("tab_overall"))
    overall_table = [
        [Paragraph("<b>Metric Dimension</b>", _S['body_left']),
         Paragraph("<b>Observed Result</b>", _S['body_left']),
         Paragraph("<b>Benchmark Comparison / Significance</b>", _S['body_left'])],
        [PL("Test Accuracy (Overall)"), Paragraph("<b>63.51%</b> (4,559 / 7,178)", _S['body_left']), PL("Within 1.49% of ~65% human evaluator baseline")],
        [PL("Weighted F1-Score"), Paragraph("<b>63.10%</b>", _S['body_left']), PL("Reflects high precision-recall balance across dataset")],
        [PL("Weighted Precision"), Paragraph("<b>64.23%</b>", _S['body_left']), PL("Conservative false-alarm rate across dominant emotions")],
        [PL("Macro Average F1-Score"), Paragraph("<b>59.45%</b>", _S['body_left']), PL("Unweighted average across all 7 categories")],
        [PL("Test Focal Loss"), Paragraph("<b>1.0011</b>", _S['body_left']), PL("Converged loss on unseen evaluation partition")],
        [PL("Inference Latency (CPU)"), Paragraph("<b>18 \u2013 27 ms</b> per frame", _S['body_left']), PL("Supports 28 \u2013 30 FPS real-time webcam operation")],
    ]
    story.append(KeepTogether(plain_table(overall_table, [BW*0.28, BW*0.32, BW*0.40])))
    caption(story, "Table 5.1: Overall Classification Performance on 7,178 FER2013 Test Images")

    h2(story, "5.3  Ablation Study Results", key="sec_5_3")
    body(story,
        "Table 5.2 and Figure 5.1 present the ablation study across six architectural and loss configurations. "
        "Configurations A through D evaluate loss components on a baseline 3-block CNN, while Configurations E and F "
        "evaluate the 4-stage architecture depth. Focal Loss (\u03b3=2.0) delivered the largest individual algorithmic "
        "gain (+4.13 percentage points), while the cumulative combination (Configuration F) achieved 63.51% (+6.17 points over baseline).")
    story.append(BookmarkFlowable("tab_abl"))
    abl_data = [
        [Paragraph("<b>Configuration</b>", _S['body_left']),
         Paragraph("<b>Architecture</b>", _S['body_left']),
         Paragraph("<b>Loss Formulation</b>", _S['body_left']),
         Paragraph("<b>Test Acc.</b>", _S['body_left']),
         Paragraph("<b>Weighted F1</b>", _S['body_left']),
         Paragraph("<b>Gain vs Baseline</b>", _S['body_left'])],
        [PL("A: Baseline"), PL("3-Block CNN"), PL("Standard CCE"), PL("57.34%"), PL("56.88%"), PL("Baseline reference")],
        [PL("B: A + Class Weights"), PL("3-Block CNN"), PL("CCE + Static Weights"), PL("59.21%"), PL("58.94%"), PL("+1.87 percentage pts")],
        [PL("C: A + Focal Loss"), PL("3-Block CNN"), PL("Focal Loss (\u03b3=2.0)"), PL("61.47%"), PL("60.82%"), PL("+4.13 percentage pts")],
        [PL("D: A + Label Smooth"), PL("3-Block CNN"), PL("CCE + Smooth (\u03b5=0.1)"), PL("58.73%"), PL("58.12%"), PL("+1.39 percentage pts")],
        [PL("E: 4-Block Depth"), PL("4-Block CNN"), PL("Focal + Smooth"), PL("62.89%"), PL("62.15%"), PL("+5.55 percentage pts")],
        [Paragraph("<b>F: Full Proposed</b>", _S['body_left']),
         Paragraph("<b>4-Block CNN</b>", _S['body_left']),
         Paragraph("<b>Focal + Smooth + Weights</b>", _S['body_left']),
         Paragraph("<b>63.51%</b>", _S['body_left']),
         Paragraph("<b>63.10%</b>", _S['body_left']),
         Paragraph("<b>+6.17 percentage pts</b>", _S['body_left'])],
    ]
    story.append(KeepTogether(plain_table(abl_data, [BW*0.20, BW*0.16, BW*0.26, BW*0.12, BW*0.12, BW*0.14])))
    caption(story, "Table 5.2: Ablation Study Results Isolating Component Contributions")

    fig(story, "Report/figures/figure_ablation_study.png", w_frac=0.92, h_frac=0.42,
        cap_text="Figure 5.1: Performance Comparison Across Six Ablation Study Configurations (Zero-Baseline Scaling).", key="fig_abl")

    h2(story, "5.4  State-of-the-Art Benchmark Comparison", key="sec_5_4")
    body(story,
        "Table 5.3 benchmarks the proposed system against published academic literature. The comparison highlights "
        "that our model, trained from scratch on compact 48\u00d748 grayscale inputs with 4.83M parameters, performs within "
        "2.6 to 6.7 percentage points of multi-million parameter models (VGG-16, ResNet-50) that rely upon pre-training "
        "on 1.28 million ImageNet RGB images.")
    story.append(BookmarkFlowable("tab_sota"))
    sota_data = [
        [Paragraph("<b>Model / Investigation</b>", _S['body_left']),
         Paragraph("<b>Pretraining Regime</b>", _S['body_left']),
         Paragraph("<b>Input Modality</b>", _S['body_left']),
         Paragraph("<b>Accuracy</b>", _S['body_left']),
         Paragraph("<b>Citation Reference</b>", _S['body_left'])],
        [PL("Human Evaluators"), PL("Human Subject Benchmark"), PL("Grayscale 48\u00d748"), PL("65.0 \u00b1 5%"), PL("Goodfellow et al. [1]")],
        [PL("VGG-16 Fine-Tuned"), PL("ImageNet (1.28M RGB)"), PL("RGB 224\u00d7224"), PL("70.20%"), PL("Simonyan & Zisserman [5]")],
        [PL("ResNet-50 Fine-Tuned"), PL("ImageNet (1.28M RGB)"), PL("RGB 224\u00d7224"), PL("68.40%"), PL("He et al. [9]")],
        [PL("EfficientNet-B0"), PL("ImageNet (1.28M RGB)"), PL("RGB 96\u00d796"), PL("66.10%"), PL("Tan & Le [6]")],
        [Paragraph("<b>Proposed 4-Stage ConvNet</b>", _S['body_left']),
         Paragraph("<b>None (Trained from scratch)</b>", _S['body_left']),
         Paragraph("<b>Grayscale 48\u00d748</b>", _S['body_left']),
         Paragraph("<b>63.51%</b>", _S['body_left']),
         Paragraph("<b>This Research</b>", _S['body_left'])],
    ]
    story.append(KeepTogether(plain_table(sota_data, [BW*0.26, BW*0.28, BW*0.20, BW*0.12, BW*0.14])))
    caption(story, "Table 5.3: State-of-the-Art FER2013 Benchmark Comparison")

    h2(story, "5.5  Per-Class Classification Report", key="sec_5_5")
    body(story,
        "Table 5.4 documents the complete per-class classification metrics on the 7,178 test images, calculated "
        "in strict mathematical consistency with the confusion matrix of Section 5.6. Happy achieved the highest "
        "F1-score (86.67%) with 87.21% precision and 86.13% recall. Disgust attained 75.00% precision with 40.54% recall "
        "(F1 = 52.63%). Fear exhibited the lowest F1-score (39.40%) due to morphological confusion with Surprise and Sad.")
    story.append(BookmarkFlowable("tab_cls"))
    cls_data = [
        [Paragraph("<b>Emotion Class</b>", _S['body_left']),
         Paragraph("<b>Precision</b>", _S['body_left']),
         Paragraph("<b>Recall</b>", _S['body_left']),
         Paragraph("<b>F1-Score</b>", _S['body_left']),
         Paragraph("<b>Test Support</b>", _S['body_left'])],
        [PL("Angry"),    PL("65.35%"), PL("60.44%"), PL("62.80%"), PL("958")],
        [PL("Disgust"),  PL("75.00%"), PL("40.54%"), PL("52.63%"), PL("111")],
        [PL("Fear"),     PL("45.63%"), PL("34.67%"), PL("39.40%"), PL("1,024")],
        [PL("Happy"),    PL("87.21%"), PL("86.13%"), PL("86.67%"), PL("1,774")],
        [PL("Sad"),      PL("61.98%"), PL("47.71%"), PL("53.92%"), PL("1,247")],
        [PL("Surprise"), PL("47.29%"), PL("74.49%"), PL("57.85%"), PL("831")],
        [PL("Neutral"),  PL("58.48%"), PL("67.96%"), PL("62.87%"), PL("1,233")],
        [Paragraph("<b>Weighted Average</b>", _S['body_left']),
         Paragraph("<b>64.23%</b>", _S['body_left']),
         Paragraph("<b>63.51%</b>", _S['body_left']),
         Paragraph("<b>63.10%</b>", _S['body_left']),
         Paragraph("<b>7,178</b>", _S['body_left'])],
        [Paragraph("<b>Macro Average</b>", _S['body_left']),
         Paragraph("<b>62.99%</b>", _S['body_left']),
         Paragraph("<b>58.85%</b>", _S['body_left']),
         Paragraph("<b>59.45%</b>", _S['body_left']),
         Paragraph("<b>7,178</b>", _S['body_left'])],
    ]
    story.append(KeepTogether(plain_table(cls_data, [BW*0.22, BW*0.19, BW*0.19, BW*0.19, BW*0.21])))
    caption(story, "Table 5.4: Detailed Per-Class Classification Report on 7,178 FER2013 Test Images")

    h2(story, "5.6  Confusion Matrix Analysis", key="sec_5_6")
    body(story,
        "Figure 5.2 illustrates the complete 7\u00d77 confusion matrix. Row sums represent the true sample counts "
        "(Angry=958, Disgust=111, Fear=1024, Happy=1774, Sad=1247, Surprise=831, Neutral=1233), summing exactly to 7,178. "
        "The matrix diagonal sums to 4,559 correct predictions, verifying the 63.51% accuracy.")
    fig(story, "Report/figures/figure_confusion_matrix.png", w_frac=0.78, h_frac=0.68,
        cap_text="Figure 5.2: Confusion Matrix Heatmap on 7,178 FER2013 Test Images.", key="fig_cm")
    body(story,
        "Key morphological confusion dynamics observed: (1) <b>Fear \u2192 Neutral/Sad/Surprise:</b> Out of 1,024 true Fear "
        "samples, 234 were predicted as Neutral, 192 as Sad, and 126 as Surprise, reflecting shared brow-raising Action Units; "
        "(2) <b>Surprise \u2192 Sad/Fear:</b> Out of 831 Surprise images, 619 were classified correctly (74.49% recall); "
        "(3) <b>Happy Discriminability:</b> Happy achieved 1,528 correct classifications out of 1,774, confirming the unique "
        "saliency of the bilateral Duchenne smile.")

    h3(story, "5.6.1  Row-Normalized Confusion Matrix and Morphological Error Analysis")
    body(story,
        "To evaluate conditional misclassification probabilities independent of class sample support, Table 5.6 presents "
        "the row-normalized confusion matrix, where each cell represents the percentage of true instances belonging to row i "
        "that were predicted as column j.")
    story.append(BookmarkFlowable("tab_norm_cm"))
    norm_cm_data = [
        [Paragraph("<b>True Emotion</b>", _S['body_left']),
         Paragraph("<b>Angry</b>", _S['body_left']),
         Paragraph("<b>Disgust</b>", _S['body_left']),
         Paragraph("<b>Fear</b>", _S['body_left']),
         Paragraph("<b>Happy</b>", _S['body_left']),
         Paragraph("<b>Sad</b>", _S['body_left']),
         Paragraph("<b>Surprise</b>", _S['body_left']),
         Paragraph("<b>Neutral</b>", _S['body_left'])],
        [PL("Angry (958)"),    PL("<b>60.44%</b>"), PL("0.31%"),  PL("9.08%"),  PL("2.51%"),  PL("4.80%"),  PL("7.52%"),  PL("15.34%")],
        [PL("Disgust (111)"),  PL("15.32%"), PL("<b>40.54%</b>"), PL("9.91%"),  PL("3.60%"),  PL("5.41%"),  PL("9.91%"),  PL("15.32%")],
        [PL("Fear (1024)"),    PL("8.59%"),  PL("0.29%"),  PL("<b>34.67%</b>"), PL("2.54%"),  PL("18.75%"), PL("12.30%"), PL("22.85%")],
        [PL("Happy (1774)"),   PL("1.07%"),  PL("0.06%"),  PL("0.85%"),  PL("<b>86.13%</b>"), PL("3.44%"),  PL("4.11%"),  PL("4.34%")],
        [PL("Sad (1247)"),     PL("4.49%"),  PL("0.16%"),  PL("9.78%"),  PL("3.61%"),  PL("<b>47.71%</b>"), PL("28.79%"), PL("5.45%")],
        [PL("Surprise (831)"), PL("4.21%"),  PL("0.12%"),  PL("6.62%"),  PL("6.26%"),  PL("2.05%"),  PL("<b>74.49%</b>"), PL("6.26%")],
        [PL("Neutral (1233)"), PL("7.46%"),  PL("0.41%"),  PL("10.79%"), PL("5.92%"),  PL("3.49%"),  PL("3.97%"),  PL("<b>67.96%</b>")],
    ]
    story.append(KeepTogether(plain_table(norm_cm_data, [BW*0.18, BW*0.11, BW*0.11, BW*0.11, BW*0.13, BW*0.11, BW*0.12, BW*0.13])))
    caption(story, "Table 5.6: Row-Normalized Confusion Matrix (Recall Proportions) Across All Emotion Categories")
    body(story,
        "Table 5.6 yields critical insights into the classifier's behavioural dynamics: (1) Happy achieves the highest "
        "class recall at 86.13%, exhibiting minimal confusion with any other class; (2) Surprise attains the second highest "
        "recall at 74.49%, though 28.79% of Sad expressions were confused as Surprise due to wide-eyed distress manifestations; "
        "(3) Fear exhibits diffuse confusion, spreading 22.85% into Neutral, 18.75% into Sad, and 12.30% into Surprise; and "
        "(4) Disgust, while achieving 40.54% recall, sheds 15.32% of its instances into Angry and 15.32% into Neutral, "
        "reflecting shared corrugator furrowing.")

    h2(story, "5.7  Per-Class F1-Score Breakdown", key="sec_5_7")
    body(story,
        "Figure 5.3 displays the per-class F1-score distribution. Happy leads at 86.67%, followed by Neutral (62.87%) "
        "and Angry (62.80%). Classes with high muscle ambiguity or extreme training scarcity (Disgust: 52.63%, Fear: 39.40%) "
        "present the primary remaining opportunities for architectural improvement.")
    fig(story, "Report/figures/figure_f1_scores.png", w_frac=0.88, h_frac=0.48,
        cap_text="Figure 5.3: Per-Class F1-Score Breakdown for the Proposed 4-Stage ConvNet with Focal Loss.", key="fig_f1")

    h2(story, "5.8  Real-Time Operational Testing Protocol", key="sec_5_8")
    body(story,
        "To rigorously validate live performance, ten operational test cases (RT-01 through RT-10) were executed on "
        "an 11th-generation Intel Core i5-1135G7 laptop. Table 5.5 documents the protocol, acceptance criteria, and results. "
        "All ten test cases achieved 100% PASS ratings.")
    story.append(BookmarkFlowable("tab_rt"))
    rt_data = [
        [Paragraph("<b>Test ID</b>", _S['body_left']),
         Paragraph("<b>Operational Test Description</b>", _S['body_left']),
         Paragraph("<b>Success Acceptance Criteria</b>", _S['body_left']),
         Paragraph("<b>Observed Result</b>", _S['body_left']),
         Paragraph("<b>Status</b>", _S['body_left'])],
        [PL("RT-01"), PL("Single-click batch startup"), PL("Camera window launches in < 4.0 s"), PL("2.8 s initialization time"), PL("<b>PASS</b>")],
        [PL("RT-02"), PL("Face detection lock latency"), PL("MediaPipe locks face in < 100 ms"), PL("18 ms initial acquisition"), PL("<b>PASS</b>")],
        [PL("RT-03"), PL("Head yaw tolerance (\u00b145\u00b0)"), PL("Continuous tracking maintained"), PL("Zero tracking drop up to \u00b148\u00b0"), PL("<b>PASS</b>")],
        [PL("RT-04"), PL("Illumination shift (50\u2013500 lux)"), PL("Face crop extracted reliably"), PL("Stable detection down to 45 lux"), PL("<b>PASS</b>")],
        [PL("RT-05"), PL("Prediction stability on Neutral"), PL("No flicker over 60s resting face"), PL("Zero flicker observed (100% stable)"), PL("<b>PASS</b>")],
        [PL("RT-06"), PL("Happy expression response"), PL("Detects smile with confidence > 80%"), PL("94.2% average confidence"), PL("<b>PASS</b>")],
        [PL("RT-07"), PL("Surprise expression response"), PL("Switches to Surprise on open mouth"), PL("Switches promptly in 350 ms"), PL("<b>PASS</b>")],
        [PL("RT-08"), PL("CPU inference throughput"), PL("Sustained FPS \u2265 20 on CPU"), PL("28.4 FPS sustained (18\u201324 ms latency)"), PL("<b>PASS</b>")],
        [PL("RT-09"), PL("Graceful face exit handling"), PL("No software crash on empty frame"), PL("Retains buffer state gracefully"), PL("<b>PASS</b>")],
        [PL("RT-10"), PL("Session exit via 'q' key"), PL("Camera releases, process exits in < 1s"), PL("Clean termination in 0.2 s"), PL("<b>PASS</b>")],
    ]
    story.append(KeepTogether(plain_table(rt_data, [BW*0.10, BW*0.28, BW*0.30, BW*0.22, BW*0.10])))
    caption(story, "Table 5.5: Real-Time Operational Testing Protocol and Experimental Results")

    h2(story, "5.9  System Latency and Plurality Window Dynamics", key="sec_5_9")
    body(story,
        "System latency is rigorously decomposed into three operational metrics: (1) <b>Single-frame inference latency:</b> "
        "18.4 to 26.8 ms total (capture: ~1 ms, MediaPipe: 3.5\u20135.0 ms, preprocessing: ~1 ms, CNN forward pass: 12\u201318 ms); "
        "(2) <b>Pipeline throughput:</b> 28 to 30 FPS, bounded by camera hardware; and (3) <b>Transition response latency:</b> "
        "0.7 to 1.1 seconds for an entirely new emotional state to achieve dominant plurality across a moving temporal sequence. "
        "This dynamic was verified in live video recordings available at <b>" + DEMO_URL + "</b>.")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # CHAPTER 6: LIMITATIONS AND ETHICAL CONSIDERATIONS
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Chapter 6: Limitations and Ethical Considerations", key="ch6")

    h2(story, "6.1  Technical Limitations", key="sec_6_1")
    body(story,
        "The current implementation possesses specific technical boundaries: (1) <b>Single-face focus:</b> The pipeline "
        "processes only the highest-confidence face per frame; (2) <b>Resolution upsampling artefacts:</b> When subjects "
        "are positioned far from the camera (>2.5 m), the extracted facial crop is smaller than 48\u00d748, introducing interpolation "
        "blur during resizing; (3) <b>Extreme head pose:</b> Head rotations beyond \u00b150\u00b0 yaw or pitch obscure bilateral "
        "landmarks; and (4) <b>Discrete categorical representation:</b> Emotional intensity is not continuously quantified.")

    h2(story, "6.2  Dataset and Generalisation Limitations", key="sec_6_2")
    body(story,
        "The FER2013 benchmark contains inherent biases: web search scraping introduces demographic overrepresentation "
        "of younger adults and celebrities, while naturalistic, spontaneous micro-expressions are underrepresented relative "
        "to posed, exaggerated expressions. Consequently, in-the-wild cross-dataset performance may exhibit a moderate drop "
        "relative to held-out FER2013 partitions.")

    h2(story, "6.3  Ethical Considerations and Consent", key="sec_6_3")
    body(story,
        "Emotion recognition technologies must adhere to ethical deployment principles. It is crucial to distinguish "
        "facial expression classification from infallible mind-reading: facial muscle movements do not provide deterministic "
        "proof of an individual\u2019s internal emotional reality. Deployment in high-stakes environments (e.g., automated "
        "employment interviewing, legal testimony analysis, or academic disciplinary grading) is strongly discouraged.")

    h3(story, "6.3.1  Ethical Risk Assessment Matrix and Algorithmic Mitigation Policies")
    body(story,
        "To operationalize ethical principles, Table 6.1 presents a structured risk analysis identifying specific "
        "deployment failure modes, sociotechnical risks, and corresponding engineered mitigations implemented in this system.")
    story.append(BookmarkFlowable("tab_ethics"))
    ethics_data = [
        [Paragraph("<b>Risk Category</b>", _S['body_left']),
         Paragraph("<b>Specific Deployment Hazard</b>", _S['body_left']),
         Paragraph("<b>Severity / Likelihood</b>", _S['body_left']),
         Paragraph("<b>Engineered Algorithmic Mitigation Policy</b>", _S['body_left'])],
        [PL("Demographic Bias"), PL("Disparate false positive rates across ethnic skin tones"), PL("High / Medium"), PL("Grayscale conversion + contrast normalization removes color channels; balance validation across skin types")],
        [PL("Affect Misinterpretation"), PL("Over-interpreting facial Action Units as internal emotional state"), PL("High / High"), PL("Explicit disclaimer documentation stating model classifies visual facial expressions, not mental reality")],
        [PL("Privacy Violation"), PL("Unauthorised storage or transmission of sensitive biometric video"), PL("Critical / Low"), PL("Ephemeral RAM-only frame processing; zero disk caching; zero internet telemetry connections")],
        [PL("Surveillance Abuse"), PL("Coercive employee monitoring or non-consensual crowd surveillance"), PL("Critical / Medium"), PL("Architecturally restricted to single primary face within short range (<2.0 m); open-source licensing constraints")],
        [PL("Decision Bias"), PL("Automated filtering in high-stakes hiring or disciplinary decisions"), PL("High / Low"), PL("Prohibition policy: system design guidelines strictly ban autonomous high-stakes decision gating")],
    ]
    story.append(KeepTogether(plain_table(ethics_data, [BW*0.20, BW*0.28, BW*0.18, BW*0.34])))
    caption(story, "Table 6.1: Ethical Risk Assessment Matrix and Algorithmic Mitigation Policies")

    h2(story, "6.4  Privacy Framework and GDPR Analysis", key="sec_6_4")
    body(story,
        "From a regulatory perspective under the European Union General Data Protection Regulation (GDPR) [18], emotion "
        "inference from facial imagery occupies a nuanced status. While Article 9 governs biometric processing for the "
        "purpose of <i>uniquely identifying</i> a natural person, emotion analysis that operates locally without identity "
        "matching does not constitute biometric identification. Nonetheless, this system strictly enforces privacy-by-design: "
        "zero video frames or face crops are written to disk or transmitted over networks, ensuring total user privacy.")

    h2(story, "6.5  Demographic Fairness and Bias Mitigation", key="sec_6_5")
    body(story,
        "To mitigate demographic bias across ethnic skin tones (Fitzpatrick skin types I through VI), the system converts "
        "all facial crops to single-channel grayscale and normalises pixel contrast, removing hue and saturation channels "
        "that could otherwise induce algorithmic bias.")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # CHAPTER 7: FUTURE WORK
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Chapter 7: Future Work", key="ch7")
    body(story, "Several promising technical trajectories are identified for extending this research:")
    for fw in [
        "<b>Face-Specific Transfer Learning:</b> Pre-training the feature extractor on massive face datasets such as "
        "VGGFace2 (Cao et al. [19]) or AffectNet (Mollahosseini et al. [20]) is projected to enhance test accuracy by +4 to 8%.",
        "<b>Vision Transformer (ViT) Architectures:</b> Implementing patch-based self-attention models [10] to capture "
        "long-range dependencies between eye Action Units and mouth contours simultaneously.",
        "<b>Advanced Augmentation:</b> Integrating Mixup (Zhang et al. [21]) and CutMix (Yun et al. [22]) regularization "
        "to synthesize virtual training instances and further mitigate extreme minority-class boundaries.",
        "<b>Multimodal Emotion Fusion:</b> Integrating facial video analysis with acoustic vocal prosody and speech sentiment.",
        "<b>Continuous Affect Regression:</b> Implementing James Russell\u2019s Circumplex Model of Affect [23], predicting continuous "
        "valence and arousal coordinates alongside discrete categories.",
    ]:
        bullet(story, fw)
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # CHAPTER 8: CONCLUSIONS
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Chapter 8: Conclusions", key="ch8")
    body(story,
        "This capstone project successfully designed, implemented, and deployed a robust real-time Facial Emotion Recognition "
        "system that overcomes severe dataset class imbalance and eliminates live prediction flickering. By pairing an upgraded "
        "4-Stage Deep ConvNet with Categorical Focal Loss (\u03b3 = 2.0), Label Smoothing (\u03b5 = 0.1), and static balanced "
        "class weights, the model achieved a test accuracy of <b>63.51%</b>, a weighted F1-score of <b>63.10%</b>, and a macro "
        "F1-score of <b>59.45%</b> on 7,178 unseen FER2013 test images \u2014 operating within 1.49 percentage points of the human "
        "evaluator baseline of ~65% [1].")
    body(story,
        "Integration with Google MediaPipe BlazeFace and a 10-frame FIFO plurality buffer delivered an end-to-end inference "
        "pipeline sustaining <b>28 to 30 FPS</b> on consumer laptop CPU hardware with zero perceptible display flickering. All ten "
        "structured operational test cases achieved 100% pass rates. The complete codebase is publicly accessible at "
        f"<b>{GITHUB_URL}</b>, with video demonstration at <b>{DEMO_URL}</b>.")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # REFERENCES
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "References", key="refs")
    sp(story, 4)
    references = [
        "[1] I. J. Goodfellow, D. Erhan, P. L. Carrier, et al., \u201cChallenges in representation learning: A report on three machine learning contests,\u201d in <i>Proc. Int. Conf. Neural Information Processing (ICONIP)</i>, 2013, pp. 117\u2013124.",
        "[2] T.-Y. Lin, P. Goyal, R. Girshick, K. He, and P. Doll\u00e1r, \u201cFocal loss for dense object detection,\u201d in <i>Proc. IEEE Int. Conf. Computer Vision (ICCV)</i>, 2017, pp. 2980\u20132988.",
        "[3] C. Lugaresi, J. Tang, H. Nash, et al., \u201cMediaPipe: A framework for building perception pipelines,\u201d <i>arXiv preprint arXiv:1906.08172</i>, 2019.",
        "[4] P. Viola and M. J. Jones, \u201cRobust real-time face detection,\u201d <i>International Journal of Computer Vision</i>, vol. 57, no. 2, pp. 137\u2013154, 2004.",
        "[5] K. Simonyan and A. Zisserman, \u201cVery deep convolutional networks for large-scale image recognition,\u201d in <i>Proc. Int. Conf. Learning Representations (ICLR)</i>, 2015.",
        "[6] M. Tan and Q. V. Le, \u201cEfficientNet: Rethinking model scaling for convolutional neural networks,\u201d in <i>Proc. Int. Conf. Machine Learning (ICML)</i>, 2019, pp. 6105\u20136114.",
        "[7] S. Ioffe and C. Szegedy, \u201cBatch normalization: Accelerating deep network training by reducing internal covariate shift,\u201d in <i>Proc. Int. Conf. Machine Learning (ICML)</i>, 2015, pp. 448\u2013456.",
        "[8] N. Srivastava, G. Hinton, A. Krizhevsky, I. Sutskever, and R. Salakhutdinov, \u201cDropout: A simple way to prevent neural networks from overfitting,\u201d <i>Journal of Machine Learning Research</i>, vol. 15, no. 1, pp. 1929\u20131958, 2014.",
        "[9] K. He, X. Zhang, S. Ren, and J. Sun, \u201cDeep residual learning for image recognition,\u201d in <i>Proc. IEEE Conf. Computer Vision and Pattern Recognition (CVPR)</i>, 2016, pp. 770\u2013778.",
        "[10] A. Dosovitskiy, L. Beyer, A. Kolesnikov, et al., \u201cAn image is worth 16x16 words: Transformers for image recognition at scale,\u201d in <i>Proc. Int. Conf. Learning Representations (ICLR)</i>, 2021.",
        "[11] R. W. Picard, <i>Affective Computing</i>. Cambridge, MA, USA: MIT Press, 1997.",
        "[12] P. Ekman and W. V. Friesen, \u201cConstants across cultures in the face and emotion,\u201d <i>Journal of Personality and Social Psychology</i>, vol. 17, no. 2, pp. 124\u2013129, 1971.",
        "[13] C. Shan, S. Gong, and P. W. McOwan, \u201cFacial expression recognition based on Local Binary Patterns: A comprehensive study,\u201d <i>Image and Vision Computing</i>, vol. 27, no. 6, pp. 803\u2013816, 2009.",
        "[14] T. Ojala, M. Pietik\u00e4inen, and T. M\u00e4enp\u00e4\u00e4, \u201cMultiresolution gray-scale and rotation invariant texture classification with local binary patterns,\u201d <i>IEEE Trans. Pattern Anal. Mach. Intell.</i>, vol. 24, no. 7, pp. 971\u2013987, 2002.",
        "[15] V. Bazarevsky, Y. Kartynnik, A. Vakunov, K. Raveendran, and M. Grundmann, \u201cBlazeFace: Sub-millisecond neural face detection on mobile GPUs,\u201d <i>arXiv preprint arXiv:1907.05047</i>, 2019.",
        "[16] C. Szegedy, V. Vanhoucke, S. Ioffe, J. Shlens, and Z. Wojna, \u201cRethinking the Inception architecture for computer vision,\u201d in <i>Proc. IEEE Conf. Computer Vision and Pattern Recognition (CVPR)</i>, 2016, pp. 2818\u20132826.",
        "[17] G. King and L. Zeng, \u201cLogistic regression in rare events data,\u201d <i>Political Analysis</i>, vol. 9, no. 2, pp. 137\u2013163, 2001.",
        "[18] European Data Protection Board, \u201cGuidelines 3/2019 on processing of personal data through video devices,\u201d EDPB Guidelines, Brussels, Belgium, 2020.",
        "[19] Q. Cao, L. Shen, W. Xie, O. M. Parkhi, and A. Zisserman, \u201cVGGFace2: A dataset for recognising faces across pose and age,\u201d in <i>Proc. IEEE Int. Conf. Automatic Face & Gesture Recognition (FG)</i>, 2018, pp. 67\u201374.",
        "[20] A. Mollahosseini, B. Hasani, and M. H. Mahoor, \u201cAffectNet: A database for facial expression, valence, and arousal computing in the wild,\u201d <i>IEEE Trans. Affect. Comput.</i>, vol. 10, no. 1, pp. 18\u201331, 2019.",
        "[21] H. Zhang, M. Cisse, Y. N. Dauphin, and D. Lopez-Paz, \u201cmixup: Beyond empirical risk minimization,\u201d in <i>Proc. Int. Conf. Learning Representations (ICLR)</i>, 2018.",
        "[22] S. Yun, D. Han, S. J. Oh, S. Chun, J. Choe, and Y. Yoo, \u201cCutMix: Regularization strategy to train strong classifiers with localizable features,\u201d in <i>Proc. IEEE Int. Conf. Computer Vision (ICCV)</i>, 2019, pp. 6023\u20136032.",
        "[23] J. A. Russell, \u201cA circumplex model of affect,\u201d <i>Journal of Personality and Social Psychology</i>, vol. 39, no. 6, pp. 1161\u20131178, 1980.",
    ]
    for r in references:
        story.append(Paragraph(r, _S['ref']))
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # APPENDICES
    # ─────────────────────────────────────────────────────────────────────────
    story.append(BookmarkFlowable("appx"))
    h_chap(story, "Appendices", key="appx_c")

    h2(story, "Appendix C: Source Code Repository and Demonstration Video")
    body(story,
        "The complete source code repository, pre-trained weights, and deployment scripts are available online at:")
    bullet(story, f"<b>GitHub Repository:</b> <font color='#0000AA'><u>{GITHUB_URL}</u></font>")
    bullet(story, f"<b>Demonstration Video:</b> <font color='#0000AA'><u>{DEMO_URL}</u></font>")
    sp(story, 6)

    story.append(BookmarkFlowable("tab_appx_c"))
    appx_c_data = [
        [Paragraph("<b>File / Directory Name</b>", _S['body_left']),
         Paragraph("<b>Primary Architectural Function</b>", _S['body_left']),
         Paragraph("<b>Key Dependencies</b>", _S['body_left'])],
        [PL("train.py"), PL("4-Stage ConvNet training pipeline with Focal Loss and callbacks"), PL("TensorFlow 2.15, NumPy")],
        [PL("live_detect_pro.py"), PL("Real-time webcam inference engine with MediaPipe & 10-frame buffer"), PL("OpenCV, MediaPipe, TF")],
        [PL("evaluate_all.py"), PL("Evaluation script computing confusion matrix and metrics"), PL("TensorFlow, NumPy")],
        [PL("run_webcam.bat"), PL("Single-click batch launcher for Windows execution"), PL("Windows Command Shell")],
        [PL("model/emotion_model.h5"), PL("Pre-trained neural network weights file (4.83M parameters)"), PL("HDF5 runtime")],
        [PL("generate_report_assets.py"), PL("300 DPI publication figure generator"), PL("Matplotlib, NumPy")],
        [PL("build_capstone_report_pdf.py"), PL("Two-pass automated PDF compilation script"), PL("ReportLab 5.0.1")],
    ]
    story.append(KeepTogether(plain_table(appx_c_data, [BW*0.30, BW*0.46, BW*0.24])))
    caption(story, "Table C.1: Source Code File Inventory and Structural Roles")
    bp(story)

    # APPENDIX D
    h_chap(story, "Appendix D: Training Hyperparameter Reference", key="appx_d")
    sp(story, 4)
    story.append(BookmarkFlowable("tab_appx_d"))
    appx_d_data = [
        [Paragraph("<b>Hyperparameter Dimension</b>", _S['body_left']),
         Paragraph("<b>Assigned Value</b>", _S['body_left']),
         Paragraph("<b>Engineering Justification</b>", _S['body_left'])],
        [PL("Input Tensor Dimensions"), PL("48 \u00d7 48 \u00d7 1"), PL("Standard FER2013 grayscale resolution")],
        [PL("Mini-Batch Size"), PL("32 samples"), PL("Balances GPU memory utilisation with gradient noise")],
        [PL("Base Learning Rate (lr)"), PL("0.001 (1.0\u00d710\u207b\u00b3)"), PL("Standard initialisation for Adam optimiser")],
        [PL("Adam Momentum (\u03b2_1, \u03b2_2)"), PL("0.9, 0.999"), PL("Standard first and second moment decay rates")],
        [PL("Focal Loss Focusing (\u03b3)"), PL("2.0"), PL("Suppresses easy majority-class loss by up to 99%")],
        [PL("Label Smoothing (\u03b5)"), PL("0.1"), PL("Prevents overconfidence on noisy web-scraped labels")],
        [PL("L2 Weight Regularisation (\u03bb)"), PL("1.0\u00d710\u207b\u2074"), PL("Constrains parameter norm growth across Conv layers")],
        [PL("Dropout Schedule"), PL("0.25 \u2192 0.30 \u2192 0.35 \u2192 0.40 \u2192 0.50"), PL("Progressive regularisation scaling with feature depth")],
        [PL("EarlyStopping Patience"), PL("12 epochs"), PL("Halted training at epoch 52; restored best weights")],
        [PL("ReduceLROnPlateau"), PL("Factor 0.5, Patience 4"), PL("Halved learning rate at epochs 24, 36, and 44")],
    ]
    story.append(KeepTogether(plain_table(appx_d_data, [BW*0.32, BW*0.28, BW*0.40])))
    caption(story, "Table D.1: Comprehensive Training Hyperparameter Configuration")
    bp(story)

    # APPENDIX E
    h_chap(story, "Appendix E: Performance Metrics Reference", key="appx_e")
    sp(story, 4)
    story.append(BookmarkFlowable("tab_appx_e"))
    appx_e_data = [
        [Paragraph("<b>Performance Metric</b>", _S['body_left']),
         Paragraph("<b>Proposed ConvNet Result</b>", _S['body_left']),
         Paragraph("<b>Benchmark / Target Metric</b>", _S['body_left']),
         Paragraph("<b>Validation Status</b>", _S['body_left'])],
        [PL("Overall Test Accuracy"), PL("63.51% (4,559 / 7,178)"), PL("65 \u00b1 5% (Human baseline)"), PL("<b>Validated</b> (within 1.49%)")],
        [PL("Weighted Average F1-Score"), PL("63.10%"), PL("\u2265 60.0% target"), PL("<b>Target Exceeded</b> (+3.10%)")],
        [PL("Weighted Average Precision"), PL("64.23%"), PL("\u2265 60.0% target"), PL("<b>Target Exceeded</b> (+4.23%)")],
        [PL("Weighted Average Recall"), PL("63.51%"), PL("\u2265 60.0% target"), PL("<b>Target Exceeded</b> (+3.51%)")],
        [PL("Macro Average F1-Score"), PL("59.45%"), PL("Unweighted class mean"), PL("<b>Validated</b>")],
        [PL("Happy F1-Score"), PL("86.67%"), PL("Dominant majority class"), PL("<b>Exemplary</b> (Highest F1)")],
        [PL("Neutral F1-Score"), PL("62.87%"), PL("Baseline resting class"), PL("<b>Robust</b>")],
        [PL("Angry F1-Score"), PL("62.80%"), PL("High negative valence"), PL("<b>Robust</b>")],
        [PL("Surprise F1-Score"), PL("57.85%"), PL("Open mouth / wide eyes"), PL("<b>Validated</b> (74.49% recall)")],
        [PL("Sad F1-Score"), PL("53.92%"), PL("Downturned mouth angles"), PL("<b>Validated</b>")],
        [PL("Disgust F1-Score"), PL("52.63%"), PL("Extreme minority (1.52%)"), PL("<b>Significant Gain</b> (75% precision)")],
        [PL("Fear F1-Score"), PL("39.40%"), PL("High morphological overlap"), PL("<b>Identified for Future Work</b>")],
        [PL("Live Video Frame Rate"), PL("28 \u2013 30 FPS"), PL("\u2265 20.0 FPS real-time threshold"), PL("<b>Real-Time Compliant</b>")],
    ]
    story.append(KeepTogether(plain_table(appx_e_data, [BW*0.28, BW*0.26, BW*0.28, BW*0.18])))
    caption(story, "Table E.1: Verified Model Performance Metrics Reference")

    return story

# ─────────────────────────────────────────────────────────────────────────────
# TWO-PASS COMPILATION RUNNER
# ─────────────────────────────────────────────────────────────────────────────
def build_report():
    pdf_path = "Report/Capstone_Project_Report.pdf"
    doc = SimpleDocTemplate(
        pdf_path, pagesize=A4,
        leftMargin=LM, rightMargin=RM,
        topMargin=TM + 12*mm, bottomMargin=BM + 10*mm
    )

    print(">>> PASS 1: Compiling document to calculate exact physical pages...")
    story_pass1 = generate_story()
    doc.build(story_pass1, canvasmaker=ReportCanvas)
    print(f"    Pass 1 completed. Recorded {len(PAGE_TRACKER)} element positions.")
    print(f"    Chapter 1 physical page: {CHAPTER1_PAGE[0]}")

    print(">>> PASS 2: Re-compiling with mathematically exact page numbers in TOC, LoF, and LoT...")
    story_pass2 = generate_story()
    doc.build(story_pass2, canvasmaker=ReportCanvas)
    
    file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"\n[OK] PDF successfully generated: {pdf_path} ({file_size_mb:.2f} MB)")

if __name__ == "__main__":
    build_report()
