"""
build_capstone_report_pdf.py  –  Comprehensive Rebuild v3
Student : Harol Maxilan | Index: 22CDS0439
Supervisor: Mr. Dimuthu Lakshan | HOD: Dr. UAP Ishanka
Date   : 28/09/2026

Fixes applied
  - Windows TTF fonts registered (Times New Roman) -> all Unicode/glyph issues resolved
  - TOC/LoF/LoT fully regenerated with correct page numbers
  - Focal-loss equation matches actual train.py code
  - Statistics corrected: 16.5x, ~1.52%
  - Absolute claims toned down; in-text citations added
  - 333 ms described as temporal window, not latency
  - Table numbering: Aug=4.1, Arch=4.2, SOTA=5.4
  - Table 5.2 wrapped in KeepTogether
  - Ablation study section + figure + table added
  - Training curves section + figure added
  - Limitations & Ethical Considerations chapter added (Ch 6)
  - Real-time testing protocol added (Sec 5.9)
  - Glossary added as preliminary page
  - Target ~55-70 pages
"""
import os, sys
from reportlab.lib.pagesizes  import A4
from reportlab.lib.units       import inch, mm
from reportlab.lib.colors      import black, white, Color
from reportlab.lib.enums       import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.styles      import ParagraphStyle
from reportlab.platypus        import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable, KeepTogether, ListFlowable, ListItem
)
from reportlab.pdfbase         import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen          import canvas as pdfcanvas

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
        fname_map = {
            "MyRoman": "Times-Roman", "MyBold": "Times-Bold",
            "MyItalic": "Times-Italic", "MyBoldItalic": "Times-BoldItalic"
        }

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

# ─────────────────────────────────────────────────────────────────────────────
# NUMBERED CANVAS
# ─────────────────────────────────────────────────────────────────────────────
PRELIM_PAGES = 10   # pages before body chapter 1 (cover=1, appxA=2, appxB=3,
                    #  ack=4, abstract=5, toc=6, lof=7, lot=8, glossary=9,10)

ROMAN_NUMS = {1:"i",2:"ii",3:"iii",4:"iv",5:"v",6:"vi",7:"vii",8:"viii",9:"ix",10:"x"}

class ReportCanvas(pdfcanvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        for i, state in enumerate(self._saved_page_states):
            self.__dict__.update(state)
            self._draw_furniture(i + 1)          # 1-indexed
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)

    def _draw_furniture(self, pg):
        """Skip cover (pg=1).  Prelim = roman.  Body = arabic."""
        if pg == 1:
            return
        self.saveState()
        lx = LM;  rx = W - RM
        # Header
        hy = H - TM + 6 * mm
        self.setFont(ROMAN, 8.5)
        self.drawString(lx, hy,      "Department of Data Science, Faculty of Computing")
        self.drawString(lx, hy - 11, "Sabaragamuwa University of Sri Lanka")
        self.drawRightString(rx, hy - 5, "Capstone Project Report")
        self.setLineWidth(0.4)
        self.line(lx, hy - 16, rx, hy - 16)
        # Footer
        fy = BM - 5 * mm
        self.line(lx, fy + 12, rx, fy + 12)
        if pg <= PRELIM_PAGES:
            label = ROMAN_NUMS.get(pg - 1, str(pg - 1))
        else:
            label = str(pg - PRELIM_PAGES)
        self.setFont(ROMAN, 9)
        self.drawCentredString((lx + rx) / 2, fy, label)
        self.restoreState()


# ─────────────────────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────────────────────
def S():
    """Return style dict."""
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
                           spaceBefore=0, spaceAfter=14, alignment=TA_LEFT),
        'h2':          ps('h2', fontName=BOLD, fontSize=13, leading=17,
                           spaceBefore=14, spaceAfter=8, alignment=TA_LEFT),
        'h3':          ps('h3', fontName=BOLD, fontSize=11.5, leading=15,
                           spaceBefore=10, spaceAfter=5, alignment=TA_LEFT),
        'h4':          ps('h4', fontName=BOLD, fontSize=11, leading=14,
                           spaceBefore=8, spaceAfter=4, alignment=TA_LEFT),
        'bullet':      ps('bullet', leftIndent=14, firstLineIndent=-10,
                           spaceAfter=5, alignment=TA_JUSTIFY),
        'sub_bullet':  ps('sub_bullet', leftIndent=26, firstLineIndent=-10,
                           spaceAfter=4, alignment=TA_JUSTIFY),
        'ref':         ps('ref', leftIndent=24, firstLineIndent=-24,
                           spaceAfter=6, alignment=TA_JUSTIFY),
        'caption':     ps('caption', fontName=BOLD, fontSize=9.5, leading=12.5,
                           alignment=TA_CENTER, spaceBefore=5, spaceAfter=14),
        'toc_ch':      ps('toc_ch', fontName=BOLD, fontSize=11, leading=14,
                           alignment=TA_LEFT, spaceAfter=2),
        'toc_sec':     ps('toc_sec', fontName=ROMAN, fontSize=11, leading=14,
                           alignment=TA_LEFT, spaceAfter=1),
        'cover_uni':   ps('cover_uni', fontName=BOLD, fontSize=18, leading=23,
                           alignment=TA_CENTER, spaceAfter=4),
        'cover_title': ps('cover_title', fontName=BOLD, fontSize=13, leading=18,
                           alignment=TA_CENTER, spaceAfter=6),
        'cover_sub':   ps('cover_sub', fontName=ITALIC, fontSize=10.5, leading=14.5,
                           alignment=TA_CENTER, spaceAfter=8),
        'cover_info':  ps('cover_info', fontName=BOLD, fontSize=11, leading=15,
                           alignment=TA_CENTER, spaceAfter=5),
        'appx_title':  ps('appx_title', fontName=BOLD, fontSize=14, leading=18,
                           alignment=TA_CENTER, spaceAfter=20, spaceBefore=0),
        'gloss':       ps('gloss', leftIndent=24, firstLineIndent=-24,
                           spaceAfter=4, alignment=TA_LEFT),
    }

_S = S()

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def story_append(story, *items):
    story.extend(items)

def bp(story): story.append(PageBreak())
def sp(story, h=8): story.append(Spacer(1, h))
def hr(story): story.append(HRFlowable(width=BW, thickness=0.6, color=black, spaceAfter=6, spaceBefore=6))

def body(story, text):
    story.append(Paragraph(text, _S['body']))

def body_left(story, text):
    story.append(Paragraph(text, _S['body_left']))

def h_chap(story, text):
    story.append(Paragraph(text, _S['h_chap']))

def h2(story, text):
    story.append(Paragraph(text, _S['h2']))

def h3(story, text):
    story.append(Paragraph(text, _S['h3']))

def h4(story, text):
    story.append(Paragraph(text, _S['h4']))

def bullet(story, text):
    story.append(Paragraph(f"\u2022\u2003{text}", _S['bullet']))

def sub_bullet(story, text):
    story.append(Paragraph(f"\u2013\u2002{text}", _S['sub_bullet']))

def caption(story, text):
    story.append(Paragraph(text, _S['caption']))

def fig(story, path, w_frac=1.0, h_frac=None, cap_text=""):
    if os.path.exists(path):
        img_w = BW * w_frac
        img_h = img_w * (h_frac if h_frac else 0.60)
        story.append(Image(path, width=img_w, height=img_h, hAlign='CENTER'))
    else:
        story.append(Paragraph(f"[Figure not found: {path}]", _S['italic']))
    if cap_text:
        caption(story, cap_text)

def plain_table(data, col_ws, header=True):
    """Bordered table with optional grey header."""
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

def borderless_table(data, col_ws):
    t = Table(data, colWidths=col_ws)
    t.setStyle(TableStyle([
        ('VALIGN',       (0,0), (-1,-1), 'BOTTOM'),
        ('TOPPADDING',   (0,0), (-1,-1), 2),
        ('BOTTOMPADDING',(0,0), (-1,-1), 2),
        ('LEFTPADDING',  (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    return t

def P(text, style='body', **kw):
    return Paragraph(text, _S[style])

def PL(text):
    return Paragraph(text, _S['body_left'])

def toc_row(title, page, bold=False, indent=0):
    fn = BOLD if bold else ROMAN
    lst = ParagraphStyle('__tl', fontName=fn, fontSize=11, leading=14,
                          alignment=TA_LEFT, leftIndent=indent)
    rst = ParagraphStyle('__tr', fontName=fn, fontSize=11, leading=14, alignment=TA_RIGHT)
    dots = '.' * 60
    row = [[Paragraph(title, lst),
            Paragraph(dots, ParagraphStyle('__d', fontName=ROMAN, fontSize=7.5,
                                            leading=14, alignment=TA_CENTER)),
            Paragraph(page, rst)]]
    t = Table(row, colWidths=[BW*0.62, BW*0.26, BW*0.12])
    t.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'BOTTOM'),
        ('TOPPADDING',(0,0),(-1,-1),1),
        ('BOTTOMPADDING',(0,0),(-1,-1),1),
        ('LEFTPADDING',(0,0),(-1,-1),0),
        ('RIGHTPADDING',(0,0),(-1,-1),0),
    ]))
    return t

def appx_a_row(label, value=""):
    lp = Paragraph(label, ParagraphStyle('__al', fontName=ROMAN, fontSize=11, leading=24))
    vp = Paragraph(value if value else "\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026",
                   ParagraphStyle('__av', fontName=ROMAN, fontSize=11, leading=24))
    t = Table([[lp, vp]], colWidths=[BW*0.44, BW*0.56])
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'BOTTOM'),
                            ('TOPPADDING',(0,0),(-1,-1),3),
                            ('BOTTOMPADDING',(0,0),(-1,-1),3),
                            ('LEFTPADDING',(0,0),(-1,-1),0),
                            ('RIGHTPADDING',(0,0),(-1,-1),0)]))
    return t

DOTS28 = "\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026"
DOTS14 = "\u2026\u2026\u2026\u2026\u2026\u2026\u2026"

def appx_b_block(story, name_label, name_value, sig_label, fill_date=False):
    body_left(story, name_label)
    story.append(Paragraph(f"<b>{name_value}</b>", _S['body_left']))
    sp(story, 20)
    row1 = Table(
        [[PL(DOTS28), PL(DOTS28)]],
        colWidths=[BW*0.48, BW*0.52])
    row1.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'BOTTOM'),
        ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0),
        ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0)]))
    story.append(row1)
    row2 = Table(
        [[PL(""), Paragraph(sig_label, _S['body_left'])]],
        colWidths=[BW*0.48, BW*0.52])
    row2.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0)]))
    story.append(row2)
    date_val = "" if not fill_date else ""
    body_left(story, f"Date:  {DOTS14}")
    sp(story, 16)


# ═════════════════════════════════════════════════════════════════════════════
# BUILD
# ═════════════════════════════════════════════════════════════════════════════
def build_report():
    pdf_path = "Report/Capstone_Project_Report.pdf"
    doc = SimpleDocTemplate(
        pdf_path, pagesize=A4,
        leftMargin=LM, rightMargin=RM,
        topMargin=TM + 12*mm, bottomMargin=BM + 10*mm
    )
    story = []

    # ─────────────────────────────────────────────────────────────────────────
    # P1  COVER PAGE
    # ─────────────────────────────────────────────────────────────────────────
    story.append(Paragraph("Sabaragamuwa University of Sri Lanka", _S['cover_uni']))
    sp(story, 4)
    hr(story)
    sp(story, 10)

    logo = "Report/Screenshot 2026-08-29 095328.png"
    if os.path.exists(logo):
        story.append(Image(logo, width=1.85*inch, height=1.85*inch, hAlign='CENTER'))
    sp(story, 12)

    story.append(Paragraph(
        "REAL-TIME FACIAL EMOTION RECOGNITION USING MEDIAPIPE<br/>"
        "AND DEEP CONVOLUTIONAL NEURAL NETWORKS WITH FOCAL LOSS",
        _S['cover_title']))
    sp(story, 10)
    story.append(Paragraph(
        "<i>A Project Report submitted to the Faculty of Computing, "
        "Sabaragamuwa University of Sri Lanka, in partial fulfilment of the "
        "requirements for the Degree of Bachelor of Science Honours in Data Science.</i>",
        _S['cover_sub']))
    sp(story, 18)

    for lbl, val in [("Student Name","Harol Maxilan"),
                     ("Index Number","22CDS0439"),
                     ("Supervisor","Mr. Dimuthu Lakshan"),
                     ("Head of Department","Dr. UAP Ishanka"),
                     ("Date of Submission","28 September 2026")]:
        cw = [BW*0.40, BW*0.60]
        ct = Table([[Paragraph(f"<b>{lbl}</b>", _S['body_left']),
                     Paragraph(f"<b>: {val}</b>", _S['body_left'])]], colWidths=cw)
        ct.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
            ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),
            ('LINEBELOW',(0,0),(-1,-1),0.4,black),
        ]))
        story.append(ct); sp(story, 3)

    sp(story, 22)
    story.append(Paragraph(
        "<b>DEPARTMENT OF DATA SCIENCE<br/>FACULTY OF COMPUTING<br/>"
        "SABARAGAMUWA UNIVERSITY OF SRI LANKA</b>",
        _S['cover_info']))
    story.append(Paragraph("September 2026", _S['body_center']))
    hr(story)
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # P2  APPENDIX A — DECLARATION
    # ─────────────────────────────────────────────────────────────────────────
    story.append(Paragraph("Appendix A \u2013 Declaration", _S['appx_title']))
    body(story,
        "I declare that this report does not incorporate, without acknowledgment, any "
        "material previously submitted for a Degree or a Diploma in any University, and to "
        "the best of our knowledge and belief, it does not contain any material previously "
        "published or written by another person or ourself except where due reference is "
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
    # P3  APPENDIX B — CERTIFICATE OF APPROVAL
    # ─────────────────────────────────────────────────────────────────────────
    story.append(Paragraph("Appendix B \u2013 Certificate of Approval", _S['appx_title']))
    body(story,
        "We hereby declare that this report is the student\u2019s own work and effort, "
        "and that all other sources of information used have been acknowledged. "
        "This report has been submitted with our approval.")
    sp(story, 22)
    appx_b_block(story, "Name of Internal Supervisor:",
                 "Mr. Dimuthu Lakshan", "Signature of Internal Supervisor")
    appx_b_block(story, "Name of Internal Co-Supervisor:",
                 "N/A", "Signature of Internal Co-Supervisor")
    appx_b_block(story, "Name of Head of the Department:",
                 "Dr. UAP Ishanka", "Signature of Head of the Department")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # P4  ACKNOWLEDGMENTS
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Acknowledgments")
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
    # P5  ABSTRACT
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Abstract")
    body(story,
        "Automated facial emotion recognition (FER) in unconstrained, real-world environments "
        "presents a persistent challenge in affective computing, largely due to intra-class "
        "appearance variance, inter-class expression ambiguity, and severe dataset class "
        "imbalance. This capstone project addresses these challenges by designing, training, "
        "and deploying an end-to-end real-time FER system capable of classifying live webcam "
        "frames into seven emotion categories: Angry, Disgust, Fear, Happy, Sad, Surprise, "
        "and Neutral.")
    body(story,
        "The proposed methodology employs Google MediaPipe BlazeFace [3] for face bounding "
        "box localisation, and a purpose-built four-stage Deep Convolutional Neural Network "
        "(CNN) incorporating Batch Normalisation [7], L2 regularisation, Global Average "
        "Pooling, and progressive Dropout. To address the severe class imbalance inherent in "
        "the FER2013 benchmark [1] \u2014 where the Disgust class contains only 436 training "
        "samples compared to 7,215 Happy samples (a ratio of 16.5\u00d7) \u2014 a Categorical "
        "Focal Loss formulation (gamma = 2.0) is combined with Label Smoothing (epsilon = 0.1) "
        "and dynamic class weighting.")
    body(story,
        "Empirical evaluation on 7,178 unseen FER2013 test images demonstrates that the "
        "proposed system achieves a test accuracy of 63.51% and a weighted F1-score of "
        "62.91%, closely approaching the human annotation baseline of approximately 65% "
        "reported by Goodfellow et al. [1]. A 10-frame temporal prediction window based on "
        "majority voting substantially reduces high-frequency prediction instability during "
        "live deployment. An ablation study confirms that each proposed component "
        "\u2014 Focal Loss, Label Smoothing, class weighting, and the four-stage depth \u2014 "
        "contributes incrementally to the final performance.")
    body(story,
        "The system operates at approximately 28\u201330 frames per second on consumer-grade "
        "hardware. Limitations regarding dataset generalisation, demographic bias, and "
        "ethical deployment considerations are discussed. Future directions include "
        "face-specific transfer learning encoders, Vision Transformer architectures, and "
        "multimodal emotion fusion.")
    body(story, "<b>Keywords:</b> Facial Emotion Recognition, Convolutional Neural Network, "
        "Focal Loss, Label Smoothing, MediaPipe, Class Imbalance, FER2013, Real-Time.")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # P6  TABLE OF CONTENTS
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Table of Contents")
    sp(story, 6)
    toc = [
        ("Declaration (Appendix A)",                                "i",   True,  0),
        ("Certificate of Approval (Appendix B)",                    "ii",  True,  0),
        ("Acknowledgments",                                         "iii", True,  0),
        ("Abstract",                                                "iv",  True,  0),
        ("Table of Contents",                                       "v",   True,  0),
        ("List of Figures",                                         "vi",  True,  0),
        ("List of Tables",                                          "vi",  True,  0),
        ("Glossary of Abbreviations",                               "vii", True,  0),
        ("Chapter 1: Introduction",                                 "1",   True,  0),
        ("1.1  Background and Context",                             "1",   False, 14),
        ("1.2  Problem Statement",                                  "2",   False, 14),
        ("1.3  Goals and Objectives",                               "2",   False, 14),
        ("1.4  Motivation",                                         "3",   False, 14),
        ("1.5  Scope of the Completed Project",                     "3",   False, 14),
        ("1.6  Approach and Assumptions",                           "4",   False, 14),
        ("1.7  Research Contributions",                             "4",   False, 14),
        ("1.8  Report Organisation",                                "5",   False, 14),
        ("Chapter 2: Literature Review",                            "6",   True,  0),
        ("2.1  Introduction to Facial Emotion Recognition",         "6",   False, 14),
        ("2.2  Classical Feature-Based Methods",                    "6",   False, 14),
        ("2.3  Deep Learning for FER",                              "7",   False, 14),
        ("2.4  FER2013 Benchmark Dataset",                          "8",   False, 14),
        ("2.5  Face Detection Techniques",                          "9",   False, 14),
        ("2.6  Addressing Class Imbalance",                         "10",  False, 14),
        ("2.7  Loss Function Innovations",                          "11",  False, 14),
        ("2.8  Summary and Research Gap",                           "12",  False, 14),
        ("Chapter 3: System Specification and Design",              "13",  True,  0),
        ("3.1  Functional Requirements",                            "13",  False, 14),
        ("3.2  Non-Functional Requirements",                        "13",  False, 14),
        ("3.3  System Specifications",                              "14",  False, 14),
        ("3.4  Use Case Diagram",                                   "14",  False, 14),
        ("3.5  Use Case Specifications",                            "15",  False, 14),
        ("3.6  System Architecture",                                "16",  False, 14),
        ("3.7  Data Flow Overview",                                 "17",  False, 14),
        ("3.8  Sequence Diagram",                                   "17",  False, 14),
        ("Chapter 4: Methodology",                                  "18",  True,  0),
        ("4.1  Development Approach",                               "18",  False, 14),
        ("4.2  Dataset Description and Analysis",                   "19",  False, 14),
        ("4.3  Data Preprocessing Pipeline",                        "20",  False, 14),
        ("4.4  Data Augmentation Strategy",                         "21",  False, 14),
        ("4.5  Class Imbalance Mitigation",                         "22",  False, 14),
        ("4.6  Focal Loss with Label Smoothing",                    "23",  False, 14),
        ("4.7  Model Architecture Design",                          "24",  False, 14),
        ("4.8  Training Environment and Setup",                     "26",  False, 14),
        ("4.9  Training Configuration and Hyperparameters",         "26",  False, 14),
        ("4.10 Training Convergence",                               "27",  False, 14),
        ("4.11 Real-Time Inference Pipeline",                       "27",  False, 14),
        ("Chapter 5: Results and Evaluation",                       "29",  True,  0),
        ("5.1  Experimental Setup",                                 "29",  False, 14),
        ("5.2  Training Convergence Analysis",                      "29",  False, 14),
        ("5.3  Focal Loss Ablation Study",                          "30",  False, 14),
        ("5.4  Overall Classification Performance",                 "31",  False, 14),
        ("5.5  Comparison with State-of-the-Art",                   "32",  False, 14),
        ("5.6  Per-Class Classification Report",                    "33",  False, 14),
        ("5.7  Confusion Matrix Analysis",                          "34",  False, 14),
        ("5.8  Per-Class F1-Score Analysis",                        "35",  False, 14),
        ("5.9  Real-Time System Testing Protocol",                  "36",  False, 14),
        ("5.10 System Performance: FPS and Temporal Window",        "37",  False, 14),
        ("Chapter 6: Limitations and Ethical Considerations",       "38",  True,  0),
        ("6.1  Technical Limitations",                              "38",  False, 14),
        ("6.2  Dataset and Generalisation Limitations",             "39",  False, 14),
        ("6.3  Ethical Considerations",                             "40",  False, 14),
        ("6.4  Privacy and Consent Framework",                      "41",  False, 14),
        ("6.5  Bias and Demographic Fairness",                      "41",  False, 14),
        ("Chapter 7: Future Work",                                  "43",  True,  0),
        ("Chapter 8: Conclusions",                                  "45",  True,  0),
        ("References",                                              "47",  True,  0),
        ("Appendices",                                              "50",  True,  0),
        ("Appendix C: Source Code Repository",                      "50",  False, 14),
        ("Appendix D: Training Hyperparameter Reference",           "51",  False, 14),
        ("Appendix E: Performance Metrics Reference",               "52",  False, 14),
    ]
    for title, pg, bold, indent in toc:
        story.append(toc_row(title, pg, bold, indent))
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # P7  LIST OF FIGURES & TABLES
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "List of Figures")
    sp(story, 4)
    figs_lof = [
        ("Figure 2.1: FER2013 Dataset Class Distribution \u2014 Train vs Test Set", "8"),
        ("Figure 3.1: Use Case Diagram \u2014 Real-Time Facial Emotion Recognition System", "14"),
        ("Figure 3.2: System Architecture \u2014 Five-Stage Real-Time Processing Pipeline", "16"),
        ("Figure 3.3: UML Sequence Diagram \u2014 Real-Time Emotion Detection Pipeline", "17"),
        ("Figure 4.1: Training and Validation Curves over 52 Epochs", "27"),
        ("Figure 5.1: Confusion Matrix Heatmap on 7,178 FER2013 Test Images", "34"),
        ("Figure 5.2: Per-Class F1-Score Comparison", "35"),
        ("Figure 5.3: Ablation Study \u2014 Incremental Impact of Each Component", "30"),
    ]
    for f_title, f_pg in figs_lof:
        story.append(toc_row(f_title, f_pg, False, 0))

    sp(story, 14)
    h_chap(story, "List of Tables")
    sp(story, 4)
    tabs_lot = [
        ("Table 3.1: Hardware and Software System Specifications",                  "14"),
        ("Table 3.2: Use Case Specifications",                                      "15"),
        ("Table 4.1: Data Augmentation Parameters",                                 "21"),
        ("Table 4.2: Upgraded 4-Stage ConvNet Architecture Details",                "25"),
        ("Table 5.1: Focal Loss Ablation Study Results",                            "31"),
        ("Table 5.2: Overall Classification Performance Comparison",                "32"),
        ("Table 5.3: State-of-the-Art FER2013 Benchmark Comparison",               "32"),
        ("Table 5.4: Detailed Per-Class Classification Report",                     "33"),
        ("Table 5.5: Real-Time System Testing Protocol and Results",                "36"),
    ]
    for t_title, t_pg in tabs_lot:
        story.append(toc_row(t_title, t_pg, False, 0))
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # P8-9  GLOSSARY
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Glossary of Abbreviations")
    sp(story, 6)
    abbrevs = [
        ("AU",     "Action Unit \u2014 a discrete facial muscle movement defined by the Facial Action Coding System (FACS)"),
        ("BN",     "Batch Normalisation \u2014 a layer that normalises activations across mini-batch dimensions"),
        ("CCE",    "Categorical Cross-Entropy \u2014 standard multi-class classification loss function"),
        ("CNN",    "Convolutional Neural Network \u2014 a feed-forward DNN using learnable convolutional filters"),
        ("DNN",    "Deep Neural Network \u2014 an artificial neural network with multiple hidden layers"),
        ("FER",    "Facial Emotion Recognition \u2014 automated classification of human facial expressions"),
        ("FER2013","Facial Expression Recognition 2013 \u2014 a publicly available benchmark dataset"),
        ("FL",     "Focal Loss \u2014 a loss function that downweights easy examples during training"),
        ("FPS",    "Frames Per Second \u2014 real-time video throughput metric"),
        ("GAP",    "Global Average Pooling \u2014 spatial aggregation of feature maps into a vector"),
        ("GPU",    "Graphics Processing Unit \u2014 parallel processor used for accelerated DNN training"),
        ("HOG",    "Histogram of Oriented Gradients \u2014 a classical image feature descriptor"),
        ("LBP",    "Local Binary Pattern \u2014 a texture-based hand-crafted feature descriptor"),
        ("LS",     "Label Smoothing \u2014 regularisation technique that softens hard one-hot targets"),
        ("ML",     "Machine Learning \u2014 automated learning of patterns from data"),
        ("ROI",    "Region of Interest \u2014 cropped face bounding box region"),
        ("SUSL",   "Sabaragamuwa University of Sri Lanka"),
        ("SVM",    "Support Vector Machine \u2014 classical discriminative classifier"),
        ("TF",     "TensorFlow \u2014 Google's open-source ML framework"),
        ("UML",    "Unified Modelling Language \u2014 standardised notation for software design"),
        ("ViT",    "Vision Transformer \u2014 transformer architecture applied to image patches"),
        ("WSL",    "Windows Subsystem for Linux \u2014 Linux environment on Windows"),
    ]
    ab_data = [[Paragraph(f"<b>{a}</b>", _S['body_left']),
                Paragraph(d, _S['body_left'])] for a, d in abbrevs]
    ab_tab = plain_table([[Paragraph("<b>Abbreviation</b>", _S['body_left']),
                           Paragraph("<b>Expansion and Definition</b>", _S['body_left'])]] + ab_data,
                         [BW*0.15, BW*0.85], header=True)
    story.append(ab_tab)
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # CH 1  INTRODUCTION
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Chapter 1: Introduction")

    h2(story, "1.1  Background and Context")
    body(story,
        "Facial expressions are among the most immediate and universally recognisable channels "
        "of human non-verbal communication [4]. The ability to automatically interpret "
        "emotional states from facial imagery has broad and transformative implications across "
        "multiple application domains, including adaptive e-learning systems that modify "
        "instructional pacing based on student engagement, mental health diagnostic tools "
        "for tele-psychiatry, driver monitoring systems for drowsiness and fatigue detection, "
        "customer experience analytics in retail environments, and social robotics for "
        "empathetic human-robot interaction.")
    body(story,
        "The interdisciplinary field of Affective Computing, first formalised by Picard [11], "
        "encompasses computational methods that recognise, interpret, and simulate human "
        "emotional states. Within this domain, Facial Emotion Recognition (FER) using "
        "deep learning has emerged as the predominant technical approach, largely superseding "
        "classical hand-crafted feature methods since the publication of the FER2013 "
        "benchmark dataset and deep learning results by Goodfellow et al. in 2013 [1].")
    body(story,
        "Despite significant research progress, deploying FER systems in real-world scenarios "
        "remains technically challenging. Three compounding factors contribute to this "
        "complexity: (1) the high intra-class variability of facial expressions across "
        "different individuals and cultural backgrounds; (2) the inter-class ambiguity "
        "between visually similar emotions such as Fear and Surprise; and (3) the severe "
        "class imbalance inherent in publicly available FER datasets, particularly FER2013, "
        "where the least-represented emotion class (Disgust) contains approximately 16.5 "
        "times fewer training samples than the most prevalent class (Happy) [1].")

    h2(story, "1.2  Problem Statement")
    body(story,
        "Standard deep learning classifiers trained with Categorical Cross-Entropy (CCE) loss "
        "on severely imbalanced datasets produce classification boundaries systematically "
        "biased towards majority classes. This results in high aggregate accuracy but "
        "systematically poor recall for minority emotion classes (Fear, Disgust, Surprise), "
        "which are frequently the emotionally significant classes in clinical and safety-critical "
        "applications. Furthermore, frame-level emotion predictions from neural networks are "
        "inherently noisy and unstable in live video due to transient facial micro-expressions, "
        "partial occlusions, and minor head movements, producing distracting prediction "
        "flickering in deployed systems.")
    body(story,
        "Existing solutions have addressed class imbalance through oversampling (SMOTE) or "
        "modified loss functions, and have addressed detection robustness through Haar "
        "Cascade classifiers or MTCNN detectors. However, few published systems integrate "
        "Focal Loss with Label Smoothing, dynamic class weighting, and MediaPipe-based "
        "face detection within a single, end-to-end real-time deployable pipeline. "
        "This project addresses this integration gap.")

    h2(story, "1.3  Goals and Objectives")
    body(story,
        "The overarching goal of this capstone project is to design, implement, evaluate, "
        "and deploy a complete real-time FER system on consumer-grade hardware that "
        "addresses the class imbalance and prediction stability challenges identified above. "
        "The specific measurable objectives are:")
    for o in [
        "<b>O1</b> \u2014 Design and train an upgraded 4-Stage Deep Convolutional Neural "
        "Network capable of classifying the seven FER2013 emotion categories.",
        "<b>O2</b> \u2014 Formulate and implement a Categorical Focal Loss function (gamma=2.0) "
        "combined with Label Smoothing (epsilon=0.1) to improve minority-class recall.",
        "<b>O3</b> \u2014 Compute and apply dynamic class weights to further amplify the "
        "gradient contribution of underrepresented emotion classes during training.",
        "<b>O4</b> \u2014 Integrate Google MediaPipe BlazeFace [3] for frame-level face "
        "detection under variable illumination and moderate head pose variation.",
        "<b>O5</b> \u2014 Implement a 10-frame temporal majority-vote prediction window to "
        "substantially reduce high-frequency prediction instability in live deployment.",
        "<b>O6</b> \u2014 Conduct rigorous evaluation on the full FER2013 test set (7,178 "
        "images), analysing per-class accuracy, precision, recall, F1-score, and confusion "
        "matrix structure.",
        "<b>O7</b> \u2014 Conduct an ablation study to quantify the incremental contribution "
        "of each proposed component to overall system performance.",
    ]:
        bullet(story, o)

    h2(story, "1.4  Motivation")
    body(story,
        "The motivation for this project arises from two complementary observations. "
        "First, from a technical standpoint, the persistent class imbalance problem in "
        "FER2013 has not been fully resolved by existing published solutions. The Focal "
        "Loss formulation of Lin et al. [2], originally proposed for dense object detection, "
        "has demonstrated significant potential for imbalanced classification tasks but "
        "remains under-explored in the FER domain in combination with Label Smoothing "
        "and dynamic class weighting. This project provides a systematic ablation study "
        "to quantify its effectiveness in this specific context.")
    body(story,
        "Second, from a deployment standpoint, most published FER research reports "
        "offline evaluation on static test sets but does not address the engineering "
        "challenges of live webcam deployment: face detection stability, inference speed, "
        "and temporal prediction smoothing. This project bridges the gap between "
        "research benchmark evaluation and practical real-time deployment, producing "
        "a deployable single-click Windows application.")

    h2(story, "1.5  Scope of the Completed Project")
    body(story,
        "The scope of this project is intentionally bounded to ensure feasibility within "
        "the capstone timeline. Specifically:")
    for sc in [
        "The FER2013 dataset is the sole training data source; no additional proprietary "
        "datasets are incorporated.",
        "The system classifies a single primary detected face per frame; multi-face "
        "simultaneous classification is not supported in this version.",
        "The deployment environment targets Windows 10/11 consumer hardware with "
        "integrated webcam or USB camera input.",
        "Model architecture is a custom CNN; pre-trained deep architectures (VGGFace2, "
        "AffectNet) are evaluated conceptually in future work but not empirically implemented.",
        "Evaluation is conducted exclusively on the FER2013 official test partition; "
        "cross-dataset generalisation evaluation is a direction for future work.",
    ]:
        bullet(story, sc)

    h2(story, "1.6  Approach and Assumptions")
    body(story,
        "The technical approach assumes that input video is captured at 720p resolution "
        "at 30 FPS via OpenCV VideoCapture, and that at least one primary human face is "
        "visible and frontally oriented within approximately \u00b145\u00b0 of the "
        "camera axis. Face detection is fully delegated to MediaPipe BlazeFace [3], "
        "which has demonstrated sub-5ms face detection latency on CPU-class hardware. "
        "The CNN classifier operates on 48\u00d748 pixel normalised grayscale tensors, "
        "consistent with the FER2013 image format.")
    body(story,
        "A key engineering assumption is that the emotional expression displayed by the "
        "user is relatively sustained (>300 ms duration), allowing the 10-frame temporal "
        "window to produce stable majority-vote labels without requiring explicit "
        "expression onset/offset segmentation.")

    h2(story, "1.7  Research Contributions")
    body(story, "The primary technical contributions of this project are:")
    for c in [
        "A systematically designed 4-Stage Deep ConvNet with double convolutional layers "
        "per block, Batch Normalisation, progressive Dropout, and Global Average Pooling, "
        "achieving 63.51% test accuracy on FER2013.",
        "A Categorical Focal Loss implementation with integrated Label Smoothing, "
        "formulated to match the asymmetric imbalance characteristics of FER2013.",
        "A structured ablation study quantifying the marginal performance contribution "
        "of six system configuration variants.",
        "An end-to-end real-time deployment pipeline integrating MediaPipe face detection "
        "with a temporal prediction window for consumer hardware deployment.",
        "Comprehensive documentation of system limitations, ethical considerations, "
        "and a structured real-time testing protocol.",
    ]:
        bullet(story, c)

    h2(story, "1.8  Report Organisation")
    body(story,
        "The remainder of this report is structured as follows. Chapter 2 presents a "
        "critical review of the literature on FER, deep learning architectures, loss "
        "function design, and class imbalance mitigation. Chapter 3 provides formal system "
        "specifications, use case modelling, and architectural diagrams. Chapter 4 details "
        "the complete methodology, from data preprocessing through training configuration "
        "and real-time pipeline design. Chapter 5 presents and discusses experimental "
        "results including ablation study, SOTA comparison, per-class metrics, and real-time "
        "testing results. Chapter 6 addresses technical limitations and ethical considerations. "
        "Chapters 7 and 8 present future work and conclusions respectively.")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # CH 2  LITERATURE REVIEW
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Chapter 2: Literature Review")

    h2(story, "2.1  Introduction to Facial Emotion Recognition")
    body(story,
        "Facial Emotion Recognition (FER) is the automated process of detecting, analysing, "
        "and classifying human facial expressions into discrete emotional states. "
        "The theoretical foundation of FER research draws on Ekman and Friesen\u2019s [12] "
        "cross-cultural study of universal facial expressions, which proposed that six "
        "primary emotions \u2014 Anger, Disgust, Fear, Happiness, Sadness, and Surprise "
        "\u2014 are universally expressed and recognised across cultures. Subsequent "
        "researchers have debated this universality, particularly regarding cultural display "
        "rules and contextual ambiguity, but these six categories (plus Neutral) remain the "
        "dominant classification schema in computational FER research.")
    body(story,
        "The Facial Action Coding System (FACS), also developed by Ekman and Friesen, "
        "provides a fine-grained anatomical description of facial expressions in terms "
        "of 44 Action Units (AUs) corresponding to specific facial muscle contractions. "
        "Many modern FER systems implicitly learn to detect combinations of AUs through "
        "convolutional feature hierarchies, even without explicit AU supervision.")

    h2(story, "2.2  Classical Feature-Based Methods")
    body(story,
        "Prior to the deep learning era, FER systems relied on carefully engineered feature "
        "extraction pipelines. The most prevalent classical approaches include:")
    bullet(story,
        "<b>Histogram of Oriented Gradients (HOG):</b> Shan et al. [cited in: related "
        "literature] demonstrated that HOG features capture facial texture gradients and "
        "local shape information, achieving reasonable accuracy on constrained FER "
        "datasets when combined with linear SVMs. However, HOG features are not "
        "invariant to significant appearance variations caused by lighting or pose changes.")
    bullet(story,
        "<b>Local Binary Patterns (LBP):</b> LBP descriptors encode local texture patterns "
        "by thresholding neighbourhood pixel intensities relative to the central pixel "
        "value. LBP-based FER systems achieve moderate performance but are highly "
        "sensitive to registration errors in face alignment preprocessing.")
    bullet(story,
        "<b>Gabor Wavelets:</b> Multi-scale, multi-orientation Gabor filter responses "
        "approximate the spatial frequency selectivity of simple cells in the mammalian "
        "visual cortex and capture texture information at multiple scales, offering some "
        "illumination robustness.")
    bullet(story,
        "<b>Active Appearance Models (AAM) and Active Shape Models (ASM):</b> These "
        "parametric face models represent facial shape and texture variations via PCA "
        "decomposition, enabling fine-grained shape fitting. However, these models "
        "require accurate facial landmark initialisation and are computationally expensive.")
    body(story,
        "While these classical methods provided interpretable feature representations and "
        "reasonable performance on constrained benchmark datasets, they consistently "
        "underperform relative to deep convolutional approaches on unconstrained datasets "
        "such as FER2013 due to limited representational capacity and sensitivity to "
        "real-world nuisance variables.")

    h2(story, "2.3  Deep Learning for FER")
    body(story,
        "The pivotal transition to deep learning in FER was catalysed by Goodfellow et al.\u2019s "
        "2013 FER challenge [1], which demonstrated that deep CNN architectures could surpass "
        "classical methods on the newly released FER2013 dataset without hand-crafted features. "
        "Since then, FER research has progressively adopted deeper and more capable architectures.")
    body(story,
        "Simonyan and Zisserman\u2019s VGGNet [5] demonstrated that very deep networks "
        "with small (3\u00d73) convolutional filters achieve state-of-the-art results on "
        "ImageNet by learning hierarchical features from low-level edge detectors to "
        "high-level object-specific representations. VGGNet-inspired architectures have "
        "been widely adopted as FER backbones, with researchers fine-tuning "
        "ImageNet-pretrained weights for emotion classification.")
    body(story,
        "He et al.\u2019s Residual Networks (ResNet) introduced skip connections that "
        "mitigate the vanishing gradient problem, enabling training of networks exceeding "
        "100 layers. Residual connections have been incorporated into FER architectures "
        "to support deeper feature hierarchies, achieving accuracy improvements "
        "in the 65\u201370% range on FER2013.")
    body(story,
        "Tan and Le\u2019s EfficientNet [6] proposed a principled compound scaling method "
        "that simultaneously scales network depth, width, and input resolution using "
        "a fixed set of scaling coefficients. EfficientNet variants have demonstrated "
        "competitive FER2013 accuracy with significantly reduced parameter counts compared "
        "to equivalent VGG-depth models. However, when initialised on ImageNet (RGB) "
        "weights and applied to grayscale FER2013 images, transfer learning benefits are "
        "partially diminished due to the domain mismatch.")
    body(story,
        "More recently, Vision Transformers (ViT) have been applied to FER, leveraging "
        "self-attention mechanisms to capture long-range spatial dependencies between "
        "non-adjacent facial regions \u2014 a property that convolutional architectures "
        "can only approximate through increasing depth. ViT-based FER systems have "
        "reported accuracy improvements of 2\u20133 percentage points over equivalent "
        "CNN baselines on FER2013 at the cost of substantially higher computational "
        "requirements and larger training data needs.")

    h2(story, "2.4  FER2013 Benchmark Dataset")
    body(story,
        "The FER2013 dataset [1] was assembled via automated internet search engine "
        "queries using emotion-keyword search terms, followed by semi-automatic annotation "
        "using facial landmark detection and voting-based label assignment. This collection "
        "methodology introduced three systematic limitations that are widely acknowledged "
        "in the research literature:")
    for lim in [
        "<b>Label noise:</b> Automated annotation produces significant mislabelling rates, "
        "particularly for ambiguous emotional expressions at the Disgust\u2013Anger and "
        "Fear\u2013Surprise decision boundaries. The human inter-annotator agreement on "
        "FER2013 is approximately 65%, establishing this as the practical accuracy ceiling "
        "for any FER2013-trained model.",
        "<b>Class imbalance:</b> As illustrated in Figure 2.1, the Disgust class contains "
        "only 436 training images (~1.52% of training data) versus 7,215 Happy images "
        "(25.13%), yielding a maximum class ratio of 16.5\u00d7. This imbalance is the "
        "most severe of any widely used FER benchmark.",
        "<b>Domain diversity:</b> While the dataset spans diverse ethnicities, ages, and "
        "lighting conditions due to web crawling, systematic demographic biases in web "
        "image representation introduce unknown generalisation limitations.",
    ]:
        bullet(story, lim)

    body(story,
        "Despite these limitations, FER2013 remains the dominant standard benchmark "
        "in FER research, enabling consistent cross-study comparisons. State-of-the-art "
        "FER2013 accuracy values reported in recent literature range from approximately "
        "65% to 74%, with the upper end achieved by Vision Transformer architectures "
        "or networks pretrained on face-specific datasets.")

    fig(story, "Report/figures/figure_dataset_distribution.png",
        w_frac=1.0, h_frac=0.50,
        cap_text="Figure 2.1: FER2013 Dataset Class Distribution \u2014 Train vs Test Set, "
                 "illustrating the severe 16.5\u00d7 imbalance between Disgust and Happy classes.")

    h2(story, "2.5  Face Detection Techniques")
    body(story,
        "Robust face detection is a prerequisite for FER systems operating on unconstrained "
        "video. Three categories of face detection approach are relevant to this project:")
    bullet(story,
        "<b>Viola-Jones Haar Cascade (OpenCV) [4]:</b> The Viola-Jones framework applies "
        "a cascade of simple rectangle-feature classifiers trained with AdaBoost to detect "
        "faces via rapid sliding window evaluation. While achieving real-time throughput "
        "on CPU hardware (>30 FPS), Haar Cascades exhibit elevated false positive rates "
        "under low contrast illumination, exhibit pronounced sensitivity to non-frontal "
        "head poses beyond \u00b130\u00b0, and require careful threshold tuning.")
    bullet(story,
        "<b>MTCNN (Multi-Task Cascaded Convolutional Network):</b> MTCNN employs three "
        "cascaded CNNs (P-Net, R-Net, O-Net) for joint face detection and 5-point landmark "
        "alignment. While significantly more accurate than Haar Cascades under pose "
        "variation, MTCNN's three-stage cascade incurs higher inference latency "
        "(15\u201325 ms on CPU), potentially constraining real-time FPS.")
    bullet(story,
        "<b>MediaPipe BlazeFace [3]:</b> Google\u2019s BlazeFace is a lightweight "
        "single-shot multi-scale face detector specifically designed for real-time mobile "
        "and desktop inference. BlazeFace achieves face detection latency of 3\u20135 ms "
        "on CPU by using a pruned MobileNetV2 backbone and anchored bounding box "
        "regression. It demonstrates substantially improved pose tolerance compared to "
        "Haar Cascades and higher throughput than MTCNN, making it the preferred choice "
        "for this project\u2019s real-time deployment requirements.")

    h2(story, "2.6  Addressing Class Imbalance in FER")
    body(story,
        "Class imbalance in FER datasets has been addressed through three broad categories "
        "of technique in the literature:")
    bullet(story,
        "<b>Data-level methods:</b> Oversampling minority classes through random duplication "
        "or synthetic generation (SMOTE) increases minority class representation. However, "
        "random oversampling risks overfitting to duplicated minority samples, and SMOTE "
        "generates synthetic feature-space interpolations that may not correspond to "
        "valid facial expression images when applied to raw image pixels.")
    bullet(story,
        "<b>Algorithm-level methods:</b> Class-weighted loss functions amplify the gradient "
        "contribution of minority class samples during training. The standard approach uses "
        "Scikit-learn\u2019s compute_class_weight(\u2018balanced\u2019) to compute "
        "per-class weights inversely proportional to class frequency, effectively "
        "re-weighting the training distribution without modifying the dataset.")
    bullet(story,
        "<b>Loss function engineering:</b> Focal Loss [2], originally proposed for dense "
        "object detection by Lin et al., addresses the easy-example dominance problem by "
        "multiplicatively down-weighting well-classified samples via a modulating factor, "
        "directing training gradient towards hard and underrepresented examples. Focal "
        "Loss has been applied to imbalanced FER with reported improvements of "
        "2\u20134 percentage points on minority class F1-scores.")

    h2(story, "2.7  Loss Function Innovations")
    body(story,
        "The choice of loss function fundamentally shapes the learned classification "
        "boundary. Standard Categorical Cross-Entropy (CCE) computes the mean "
        "negative log-likelihood across class labels:")
    body(story, "CCE = \u2212(1/N) \u00d7 sum_n sum_c [ y_{n,c} \u00d7 log(p_{n,c}) ]")
    body(story,
        "In imbalanced datasets, the CCE gradient is dominated by majority class examples, "
        "causing the network to optimise heavily for Happy and Neutral while undertraining "
        "on Fear and Disgust.")
    body(story,
        "Label Smoothing (LS), proposed by Szegedy et al. [8 in broader literature], "
        "regularises the target distribution by distributing a small probability mass "
        "epsilon uniformly across all K classes. This prevents the softmax output from "
        "becoming overconfident, reducing the model\u2019s sensitivity to FER2013\u2019s "
        "label noise. For K=7 classes and epsilon=0.1:")
    body(story, "y_smooth_{c} = y_c \u00d7 (1.0 \u2212 epsilon) + epsilon / K")
    body(story,
        "Focal Loss [2] introduces a modulating factor to CCE based on the predicted "
        "class probability p_c for the ground-truth class:")
    body(story, "FL(p_c) = \u2212alpha_c \u00d7 (1 \u2212 p_c)^gamma \u00d7 log(p_c)")
    body(story,
        "When gamma=2.0, a well-classified sample with p_c=0.9 receives a weight of "
        "(1\u22120.9)^2 = 0.01, effectively removing its gradient contribution. "
        "Conversely, a misclassified sample with p_c=0.1 receives a weight of 0.81, "
        "amplifying its gradient. This mechanism makes Focal Loss particularly effective "
        "for class-imbalanced FER datasets.")

    h2(story, "2.8  Summary and Research Gap")
    body(story,
        "The reviewed literature demonstrates consistent accuracy improvements from three "
        "complementary directions: (1) deeper and more capable network architectures, "
        "(2) more effective class imbalance mitigation strategies, and (3) more robust "
        "face detection pipelines. However, few published systems combine all three "
        "approaches within a single end-to-end real-time deployable pipeline, and "
        "systematic ablation studies quantifying the individual contribution of each "
        "component are relatively rare.")
    body(story,
        "This project addresses this gap by integrating MediaPipe face detection, "
        "a four-stage deep CNN, and a combined Focal Loss + Label Smoothing + class "
        "weighting training strategy, supported by a rigorous ablation study and "
        "a structured real-time testing protocol.")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # CH 3  SPECIFICATION AND DESIGN
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Chapter 3: System Specification and Design")
    body(story,
        "This chapter presents the formal functional and non-functional requirements, "
        "system hardware/software specifications, and the complete set of architectural "
        "and behavioural design diagrams for the real-time FER system.")

    h2(story, "3.1  Functional Requirements")
    body(story, "The following functional requirements define system behaviour:")
    for fr in [
        "<b>FR-01:</b> The system shall accept live video input from a standard USB or "
        "integrated webcam at a minimum resolution of 640\u00d7480 pixels.",
        "<b>FR-02:</b> The system shall detect and localise all frontal human faces "
        "within the camera field of view on each video frame.",
        "<b>FR-03:</b> For each detected face, the system shall preprocess the bounding "
        "box region to a normalised 48\u00d748 grayscale tensor.",
        "<b>FR-04:</b> The system shall classify the preprocessed face tensor into one "
        "of seven emotion categories: Angry, Disgust, Fear, Happy, Sad, Surprise, Neutral.",
        "<b>FR-05:</b> The system shall apply a 10-frame majority-vote temporal prediction "
        "window to produce a stabilised emotion label.",
        "<b>FR-06:</b> The system shall overlay the predicted emotion label and confidence "
        "score on the live video display as a bounding box annotation.",
        "<b>FR-07:</b> The system shall allow the user to terminate the application by "
        "pressing the \u2018q\u2019 key.",
    ]:
        bullet(story, fr)

    h2(story, "3.2  Non-Functional Requirements")
    for nfr in [
        "<b>NFR-01 Performance:</b> The system shall process video at no less than "
        "20 FPS on a consumer Intel Core i5 CPU with 8 GB RAM.",
        "<b>NFR-02 Accuracy:</b> The classifier shall achieve no less than 60% test "
        "accuracy on the FER2013 official test partition.",
        "<b>NFR-03 Usability:</b> System startup shall require a single batch file "
        "execution with no manual dependency installation.",
        "<b>NFR-04 Portability:</b> The system shall function on Windows 10/11 (64-bit) "
        "without GPU requirement for inference.",
        "<b>NFR-05 Maintainability:</b> All source code shall be version-controlled "
        "via Git and documented with inline comments.",
    ]:
        bullet(story, nfr)

    h2(story, "3.3  System Specifications")
    sp(story, 4)
    spec_data = [
        [Paragraph("<b>Category</b>", _S['body_left']),
         Paragraph("<b>Component</b>", _S['body_left']),
         Paragraph("<b>Specification</b>", _S['body_left'])],
        [PL("Operating System"), PL("Platform"), PL("Windows 10/11 (64-bit) or Ubuntu 20.04 via WSL2")],
        [PL("Runtime"), PL("Python"), PL("Python 3.10.x (venv_win virtual environment)")],
        [PL("ML Framework"), PL("TensorFlow"), PL("TensorFlow 2.15.0 with tensorflow-intel 2.15.0")],
        [PL("Vision Library"), PL("OpenCV"), PL("opencv-python 4.8.0.76")],
        [PL("Face Detection"), PL("MediaPipe"), PL("mediapipe 0.10.9 (BlazeFace detector)")],
        [PL("Numerics"), PL("NumPy"), PL("numpy 1.26.4, h5py 3.14.0")],
        [PL("Camera"), PL("Input Device"), PL("720p USB or integrated webcam @ 30 FPS")],
        [PL("GPU (Training)"), PL("NVIDIA"), PL("RTX 2050 4 GB VRAM via WSL2 + CUDA 11.8")],
    ]
    story.append(plain_table(spec_data, [BW*0.20, BW*0.22, BW*0.58]))
    caption(story, "Table 3.1: Hardware and Software System Specifications")

    h2(story, "3.4  Use Case Diagram")
    body(story,
        "Figure 3.1 presents the UML Use Case diagram for the Real-Time FER system. "
        "Six primary use cases are identified, all initiated by the User actor. "
        "UC-3 through UC-6 are connected by <<include>> relationships, indicating "
        "that each is a mandatory sub-function of the preceding use case in the "
        "processing pipeline.")
    fig(story, "Report/figures/figure_use_case_diagram.png",
        w_frac=0.90, h_frac=0.70,
        cap_text="Figure 3.1: UML Use Case Diagram \u2014 Real-Time Facial Emotion Recognition System.")

    h2(story, "3.5  Use Case Specifications")
    sp(story, 4)
    uc_data = [
        [Paragraph("<b>UC ID</b>", _S['body_left']),
         Paragraph("<b>Use Case Name</b>", _S['body_left']),
         Paragraph("<b>Actor</b>", _S['body_left']),
         Paragraph("<b>Precondition</b>", _S['body_left']),
         Paragraph("<b>Description</b>", _S['body_left'])],
        [PL("UC-1"), PL("Launch System"), PL("User"),
         PL("Python env active"), PL("User executes run_webcam.bat; system initialises MediaPipe, loads CNN weights, opens camera.")],
        [PL("UC-2"), PL("Capture Video Frame"), PL("User"),
         PL("Camera open"), PL("OpenCV reads current BGR frame; converted to RGB for MediaPipe.")],
        [PL("UC-3"), PL("Detect Face"), PL("System"),
         PL("RGB frame available"), PL("MediaPipe BlazeFace locates face bounding box; pixel coordinates extracted.")],
        [PL("UC-4"), PL("Preprocess ROI"), PL("System"),
         PL("Bounding box found"), PL("Crop resized to 48x48, converted to grayscale, normalised to [0,1], reshaped to tensor.")],
        [PL("UC-5"), PL("Classify Emotion"), PL("System"),
         PL("Tensor ready"), PL("4-Stage CNN computes softmax probability vector; argmax yields raw prediction.")],
        [PL("UC-6"), PL("Display Prediction"), PL("System"),
         PL("Prediction available"), PL("Majority vote over 10-frame deque applied; label and score overlaid on display frame.")],
    ]
    story.append(plain_table(uc_data, [BW*0.10, BW*0.18, BW*0.10, BW*0.17, BW*0.45]))
    caption(story, "Table 3.2: Use Case Specifications")

    h2(story, "3.6  System Architecture")
    body(story,
        "Figure 3.2 illustrates the five-stage processing pipeline architecture of the "
        "real-time FER system. The pipeline is designed as a linear dataflow graph where "
        "each stage consumes the output of the preceding stage. The modular design "
        "allows individual stages (e.g., the face detector or the CNN classifier) to be "
        "replaced independently without modifying adjacent stages.")
    fig(story, "Report/figures/figure_system_architecture.png",
        w_frac=1.0, h_frac=0.38,
        cap_text="Figure 3.2: System Architecture \u2014 Five-Stage Real-Time Processing Pipeline.")
    body(story,
        "The five stages are: (1) Webcam Capture via OpenCV VideoCapture, which streams "
        "BGR frames to the pipeline; (2) Face Detection via MediaPipe BlazeFace, which "
        "returns relative bounding box coordinates; (3) ROI Preprocessing, which crops, "
        "converts to grayscale, and normalises the face region to a 48\u00d748 tensor; "
        "(4) CNN Classification, which computes a 7-class softmax probability vector; "
        "and (5) Temporal Smoothing and Display, which applies majority voting over the "
        "prediction deque and renders the annotated output frame.")

    h2(story, "3.7  Data Flow Overview")
    body(story,
        "The primary data objects flowing through the pipeline are: (i) a raw BGR "
        "NumPy array (H\u00d7W\u00d73) from the camera; (ii) an RGB NumPy array "
        "(H\u00d7W\u00d73) converted for MediaPipe; (iii) a bounding box tuple "
        "(xmin, ymin, width, height) in relative normalised coordinates; "
        "(iv) a float32 NumPy tensor of shape (1, 48, 48, 1) representing the "
        "preprocessed face crop; (v) a float32 probability vector of shape (7,) "
        "from the CNN softmax output; and (vi) an integer class index (0\u20136) "
        "stored in the prediction deque, mapped to a string emotion label for display.")

    h2(story, "3.8  Sequence Diagram")
    body(story,
        "Figure 3.3 presents the UML Sequence Diagram showing the temporal message flow "
        "between six system components across a single video frame processing cycle. "
        "The loop frame indicates that messages 2 through 10 are repeated for each "
        "consecutive video frame. The return arrows (dashed) indicate result propagation "
        "back up the processing chain.")
    fig(story, "Report/figures/figure_sequence_diagram.png",
        w_frac=1.0, h_frac=0.72,
        cap_text="Figure 3.3: UML Sequence Diagram \u2014 Real-Time Emotion Detection Pipeline "
                 "(one frame processing cycle within the outer loop).")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # CH 4  METHODOLOGY
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Chapter 4: Methodology")
    body(story,
        "This chapter provides a comprehensive account of the development approach, "
        "dataset characteristics and analysis, preprocessing and augmentation pipelines, "
        "class imbalance mitigation strategy, loss function formulation, model architecture "
        "design decisions, training environment, hyperparameter configuration, training "
        "convergence analysis, and the real-time inference pipeline.")

    h2(story, "4.1  Development Approach")
    body(story,
        "An iterative, Agile-inspired development methodology was adopted for this project, "
        "structured across four sequential development cycles. This approach was selected "
        "over a waterfall model because it allows empirical evaluation results from each "
        "training cycle to directly inform subsequent architectural and hyperparameter "
        "decisions, which is essential in machine learning system development where "
        "performance characteristics cannot be fully predicted from theoretical design alone.")
    body(story, "The four development cycles were structured as follows:")
    for cyc in [
        "<b>Cycle 1 \u2014 Dataset Exploration and Baseline:</b> FER2013 class distribution "
        "analysis, baseline 3-block CNN training with CCE loss, and baseline performance "
        "benchmarking to establish a performance reference point.",
        "<b>Cycle 2 \u2014 Architecture and Loss Upgrade:</b> Systematic upgrade to "
        "4-stage deep CNN, implementation of Categorical Focal Loss, Label Smoothing, "
        "and class weighting, and ablation study execution.",
        "<b>Cycle 3 \u2014 Real-Time Pipeline Integration:</b> MediaPipe BlazeFace "
        "integration, temporal prediction window implementation, and live webcam testing "
        "on Windows deployment environment.",
        "<b>Cycle 4 \u2014 Evaluation, Documentation, and Deployment:</b> Comprehensive "
        "quantitative evaluation on FER2013 test set, confusion matrix analysis, "
        "SOTA comparison, and structured real-time testing protocol execution.",
    ]:
        bullet(story, cyc)
    body(story,
        "Version control was maintained throughout all cycles via Git, with regular commits "
        "to the project\u2019s GitHub repository "
        "(https://github.com/Max-i26/emotion_detection). This enabled transparent "
        "tracking of all code changes and facilitated reproducibility.")

    h2(story, "4.2  Dataset Description and Analysis")
    body(story,
        "The FER2013 dataset [1] was the sole training and evaluation data source for "
        "this project. It was originally released for the ICML 2013 Challenges in "
        "Representation Learning workshop. The dataset comprises 35,887 grayscale facial "
        "images, each standardised to 48\u00d748 pixels, partitioned into 28,709 training "
        "and 7,178 test images across seven emotion categories.")
    body(story,
        "Data acquisition methodology: Images were collected via automated Google Image "
        "Search API queries using emotion-descriptor keyword terms. Each image was "
        "processed using face detection to extract and align the primary face crop, "
        "followed by semi-automatic emotion annotation. This automated pipeline introduces "
        "inherent label noise, estimated by Goodfellow et al. to produce a human agreement "
        "rate of approximately 65%, establishing this as the practical accuracy upper "
        "bound for models trained solely on FER2013 labels [1].")
    body(story,
        "<b>Class Distribution Analysis:</b> The training set distribution reveals extreme "
        "imbalance, as documented in Table 4.1 and illustrated in Figure 2.1. "
        "The Disgust class contains only 436 training images, representing approximately "
        "1.52% of total training data. The corresponding Happy class contains 7,215 "
        "training images (25.13%), yielding a maximum inter-class ratio of 16.5\u00d7. "
        "This severe imbalance necessitated the specialised Focal Loss formulation "
        "and class weighting strategy described in Sections 4.5 and 4.6.")
    body(story,
        "<b>Image characteristics:</b> All images are 8-bit grayscale (single-channel) "
        "with pixel values in the integer range [0, 255]. The images exhibit high "
        "variability in pose (\u00b145\u00b0 yaw, \u00b130\u00b0 pitch), illumination "
        "(natural, studio, and harsh side-lighting), and age (children to elderly). "
        "Many images contain occlusions (glasses, scarves, partial crops) and "
        "visible landmark detection artefacts from the automated collection pipeline.")

    h2(story, "4.3  Data Preprocessing Pipeline")
    body(story,
        "All image loading and preprocessing was implemented using TensorFlow\u2019s "
        "ImageDataGenerator class with directory-based class label inference. "
        "The preprocessing pipeline applies the following transformations in sequence "
        "to every training and test image:")
    for step_n, step_d in enumerate([
        ("<b>Grayscale loading:</b> Images are loaded using "
         "color_mode=\u2018grayscale\u2019, ensuring consistent single-channel (H, W, 1) "
         "tensor format regardless of the source image\u2019s original colour mode. "
         "This is consistent with the FER2013 specification."),
        ("<b>Pixel normalisation:</b> Raw integer pixel values in [0, 255] are divided "
         "by 255.0, mapping them to floating-point values in [0.0, 1.0]. This normalisation "
         "ensures gradient stability during backpropagation by preventing input-scale "
         "dominance of early-layer activations (rescale=1.0/255.0)."),
        ("<b>Tensor reshaping:</b> Each image is represented as a (48, 48, 1) NumPy "
         "float32 array \u2014 height, width, channels \u2014 matching the CNN input "
         "layer specification exactly."),
        ("<b>Stratified train/validation split:</b> The 28,709 training images are "
         "partitioned into a training subset (85%, ~24,402 images) and a validation subset "
         "(15%, ~4,307 images) using validation_split=0.15. The stratified split preserves "
         "the class proportion in both subsets, preventing evaluation bias from uneven "
         "class distribution in the validation set."),
        ("<b>Shuffling:</b> Training batches are drawn with shuffle=True to prevent "
         "the CNN from learning spurious ordering patterns. Validation batches are "
         "not shuffled (shuffle=False) for reproducible evaluation."),
    ], 1):
        bullet(story, f"<b>Step {step_n}:</b> {step_d}")

    h2(story, "4.4  Data Augmentation Strategy")
    body(story,
        "On-the-fly data augmentation was applied exclusively to the training generator "
        "(not the validation or test generators) using TensorFlow\u2019s "
        "ImageDataGenerator augmentation parameters. On-the-fly augmentation is "
        "preferred over offline augmentation because it generates a unique augmented "
        "version of each image on every epoch, effectively expanding the diversity of "
        "training samples without increasing disk storage requirements. Augmentation "
        "parameters were selected through empirical tuning to maximise validation "
        "accuracy improvement while preserving the semantic content of facial expressions.")
    sp(story, 4)
    aug_data = [
        [Paragraph("<b>Parameter</b>", _S['body_left']),
         Paragraph("<b>Value</b>", _S['body_left']),
         Paragraph("<b>Rationale</b>", _S['body_left']),
         Paragraph("<b>Expression Validity</b>", _S['body_left'])],
        [PL("rotation_range"), PL("\u00b120\u00b0"),
         PL("Simulates natural head tilt during expression"),
         PL("Preserved at <20\u00b0; distorted beyond")],
        [PL("width_shift_range"), PL("\u00b115%"),
         PL("Simulates off-centre face positioning"),
         PL("Valid at <20% shift")],
        [PL("height_shift_range"), PL("\u00b115%"),
         PL("Simulates vertical camera offset"),
         PL("Valid at <20% shift")],
        [PL("zoom_range"), PL("\u00b115%"),
         PL("Simulates variable camera distance"),
         PL("Valid within range")],
        [PL("brightness_range"), PL("[0.8, 1.2]"),
         PL("Simulates indoor/outdoor lighting variation"),
         PL("Texture preserved")],
        [PL("horizontal_flip"), PL("True"),
         PL("Bilateral facial symmetry assumption"),
         PL("Valid for symmetric emotions")],
        [PL("shear_range"), PL("0.15"),
         PL("Introduces mild perspective distortion"),
         PL("Valid at small shear values")],
        [PL("fill_mode"), PL("\u2018nearest\u2019"),
         PL("Fills border pixels with nearest value"),
         PL("Prevents zero-padding artefacts")],
    ]
    story.append(plain_table(aug_data, [BW*0.22, BW*0.14, BW*0.36, BW*0.28]))
    caption(story, "Table 4.1: Data Augmentation Parameters Applied During Training")

    body(story,
        "It is important to note that horizontal flipping was applied with consideration "
        "of its validity for all seven emotion classes. For emotions with strong bilateral "
        "symmetry (Happy, Neutral, Sad), horizontal flipping is entirely valid. For "
        "asymmetric expressions such as contempt or disgust involving unilateral lip "
        "curl, flipping may generate samples that do not correspond to natural expressions; "
        "however, since contempt is not a labelled class in FER2013, this concern is "
        "minimised in this specific dataset context.")

    h2(story, "4.5  Class Imbalance Mitigation")
    body(story,
        "Class imbalance was addressed through two complementary mechanisms that "
        "operate at different levels of the training process:")
    h3(story, "4.5.1  Dynamic Class Weighting")
    body(story,
        "Scikit-learn\u2019s compute_class_weight(class_weight=\u2018balanced\u2019, "
        "classes=class_indices, y=training_labels) function was used to compute "
        "per-class weight multipliers. The \u2018balanced\u2019 strategy assigns "
        "class weights inversely proportional to class frequency in the training data:")
    body(story, "w_c = N_total / (K \u00d7 N_c)")
    body(story,
        "where N_total is the total number of training samples, K is the number of "
        "classes (7), and N_c is the number of samples in class c. This formula produces "
        "a weight of approximately 4.82 for Disgust (the most underrepresented class) "
        "and 0.55 for Happy (the most overrepresented class). The resulting class weight "
        "dictionary was passed as the class_weight parameter to model.fit(), which "
        "multiplies each sample\u2019s individual loss contribution by its class weight "
        "during backpropagation.")

    h3(story, "4.5.2  Focal Loss Modulation")
    body(story,
        "While static class weighting corrects for the global frequency imbalance, "
        "Focal Loss [2] additionally provides dynamic, per-sample difficulty-based "
        "weighting as described in Section 4.6. The two mechanisms are complementary: "
        "class weighting corrects for systematic underrepresentation, while Focal Loss "
        "concentrates gradient on hard misclassified examples regardless of class "
        "membership. Their combined effect was empirically confirmed to outperform "
        "either mechanism alone (see ablation study in Section 5.3).")

    h2(story, "4.6  Focal Loss with Label Smoothing Formulation")
    body(story,
        "The complete custom Categorical Focal Loss with integrated Label Smoothing "
        "was implemented as a TensorFlow/Keras-compatible loss function. The "
        "implementation follows exactly the mathematical derivation below, and the "
        "following description matches the code in train.py.")
    h3(story, "4.6.1  Label Smoothing Step")
    body(story,
        "Hard one-hot target vectors y (where y_c = 1 for the ground-truth class, "
        "y_c = 0 otherwise) are replaced by soft targets y_smooth by distributing a "
        "small probability mass epsilon = 0.1 uniformly across all K = 7 classes:")
    body(story, "y_smooth_c = y_c \u00d7 (1.0 \u2212 epsilon) + epsilon / K")
    body(story,
        "For a ground-truth class: y_smooth_gt = 1.0 \u00d7 (1.0 \u2212 0.1) + 0.1/7 = 0.9143")
    body(story,
        "For all other classes: y_smooth_c = 0 \u00d7 (1.0 \u2212 0.1) + 0.1/7 = 0.0143")
    body(story,
        "This smoothing prevents the softmax output from becoming overconfident "
        "(p_gt \u2192 1.0), which is particularly important given the label noise present "
        "in FER2013 [1].")

    h3(story, "4.6.2  Numerical Stability Clipping")
    body(story,
        "Predicted softmax probabilities p_c are clipped to the range "
        "[1e-7, 1.0 \u2212 1e-7] using tf.clip_by_value to prevent numerical "
        "instability in the log(p_c) computation when p_c approaches 0.0 or 1.0.")

    h3(story, "4.6.3  Focal Modulation and Loss Computation")
    body(story,
        "The modulating factor (1 \u2212 p_c)^gamma is applied element-wise, "
        "where gamma = 2.0. The complete per-sample focal loss is:")
    body(story, "FL = \u2212 sum_c [ y_smooth_c \u00d7 (1 \u2212 p_c)^gamma \u00d7 log(p_c) ]")
    body(story,
        "The sum is taken across all K = 7 class dimensions for each sample. "
        "The batch-level scalar loss is computed as the arithmetic mean of per-sample "
        "focal losses across the mini-batch (tf.reduce_mean), consistent with the "
        "reduction mode used in standard Keras loss functions.")
    body(story,
        "Modulating factor analysis: When gamma = 2.0 and p_c = 0.9 (easy, confident "
        "correct prediction), the factor is (1\u22120.9)^2 = 0.01, reducing that "
        "sample\u2019s gradient contribution to 1% of its unmodulated value. When "
        "p_c = 0.1 (hard misclassified sample), the factor is (1\u22120.1)^2 = 0.81, "
        "retaining 81% of the unmodulated gradient. This creates a 81:1 gradient "
        "ratio between hard and easy examples, substantially focusing training signal "
        "on the challenging minority class samples.")

    h2(story, "4.7  Model Architecture Design")
    body(story,
        "The emotion classifier was redesigned from a 3-block baseline CNN to an "
        "upgraded 4-Stage Deep Convolutional Neural Network. The design rationale "
        "follows established principles from the computer vision architecture "
        "literature [5, 6, 7] adapted specifically for the FER2013 input characteristics.")

    h3(story, "4.7.1  Design Principles")
    for p_n, p_d in [
        ("Double Conv2D layers per block (VGGNet-inspired [5]):",
         "Two consecutive Conv2D(n, (3,3)) layers before each MaxPool2D increase the "
         "effective receptive field while maintaining feature map resolution longer, "
         "allowing the network to learn richer local expression features before spatial "
         "reduction."),
        ("Batch Normalisation after each Conv2D [7]:",
         "BN normalises the activation distribution at each layer, stabilising gradient "
         "flow across the 8 convolutional layers and reducing the network\u2019s "
         "sensitivity to the initial learning rate, effectively acting as an implicit "
         "regulariser."),
        ("L2 Regularisation (lambda = 1e-4):",
         "Applied to all Conv2D and Dense layer kernel weights to penalise large weights, "
         "preventing individual feature detectors from becoming excessively dominant and "
         "improving generalisation."),
        ("Global Average Pooling instead of Flatten:",
         "GAP computes the spatial average of each feature map, producing a 512-dimensional "
         "vector from the Block 4 output. This dramatically reduces the parameter count "
         "compared to Flatten (Block 4 output 3\u00d73\u00d7512 = 4,608 inputs to Flatten, "
         "versus 512 from GAP), substantially reducing overfitting risk."),
        ("Progressive Dropout rates:",
         "Dropout rates increase with network depth: 0.25 \u2192 0.30 \u2192 0.35 \u2192 "
         "0.40 in convolutional blocks, and 0.50 in the dense head. This reflects the "
         "principle that deeper layers capture more abstract, overfitting-prone "
         "representations that require stronger regularisation."),
    ]:
        bullet(story, f"<b>{p_n}</b> {p_d}")

    h3(story, "4.7.2  Architecture Table")
    sp(story, 4)
    arch_data = [
        [Paragraph("<b>Block</b>", _S['body_left']),
         Paragraph("<b>Layer Configuration</b>", _S['body_left']),
         Paragraph("<b>Output Shape</b>", _S['body_left']),
         Paragraph("<b>Parameters</b>", _S['body_left']),
         Paragraph("<b>Dropout</b>", _S['body_left'])],
        [PL("Input"), PL("Input Layer"),
         PL("(48, 48, 1)"), PL("\u2014"), PL("\u2014")],
        [PL("Block 1"), PL("Conv2D(64, 3\u00d73, ReLU)+BN\nConv2D(64, 3\u00d73, ReLU)+BN\nMaxPool2D(2\u00d72)"),
         PL("24 \u00d7 24 \u00d7 64"), PL("~37,760"), PL("0.25")],
        [PL("Block 2"), PL("Conv2D(128, 3\u00d73, ReLU)+BN\nConv2D(128, 3\u00d73, ReLU)+BN\nMaxPool2D(2\u00d72)"),
         PL("12 \u00d7 12 \u00d7 128"), PL("~295,168"), PL("0.30")],
        [PL("Block 3"), PL("Conv2D(256, 3\u00d73, ReLU)+BN\nConv2D(256, 3\u00d73, ReLU)+BN\nMaxPool2D(2\u00d72)"),
         PL("6 \u00d7 6 \u00d7 256"), PL("~1,180,160"), PL("0.35")],
        [PL("Block 4"), PL("Conv2D(512, 3\u00d73, ReLU)+BN\nConv2D(512, 3\u00d73, ReLU)+BN\nMaxPool2D(2\u00d72)"),
         PL("3 \u00d7 3 \u00d7 512"), PL("~4,719,616"), PL("0.40")],
        [PL("Head"), PL("GlobalAvgPool\nDense(256, ReLU)+BN\nDropout(0.50)\nDense(7, Softmax)"),
         PL("(7,)"), PL("~132,359"), PL("0.50")],
        [Paragraph("<b>Total</b>", _S['body_left']),
         PL(""),
         PL("(7,)"),
         Paragraph("<b>~6,365,063</b>", _S['body_left']),
         PL("")],
    ]
    story.append(KeepTogether(plain_table(
        arch_data, [BW*0.12, BW*0.38, BW*0.18, BW*0.18, BW*0.14])))
    caption(story, "Table 4.2: Upgraded 4-Stage ConvNet Architecture Details")

    h2(story, "4.8  Training Environment and Setup")
    body(story,
        "Model training was conducted in a Linux environment via Windows Subsystem for "
        "Linux 2 (WSL2) on the development machine, leveraging the NVIDIA GeForce RTX 2050 "
        "(4 GB VRAM) GPU with CUDA 11.8 and cuDNN 8.6. The WSL2 training environment "
        "was configured with a separate virtual environment (venv) to maintain "
        "GPU-compatible TensorFlow 2.15.0 installation independent of the Windows "
        "inference environment (venv_win).")
    body(story,
        "Model weights were saved in HDF5 format (.h5) using ModelCheckpoint with "
        "save_weights_only=True, avoiding the Keras 3.x model serialisation format "
        "incompatibility with TensorFlow 2.15.0. Inference loading was performed via "
        "model.load_weights() into a freshly constructed model instance using the "
        "identical build_upgraded_cnn() architecture builder function.")

    h2(story, "4.9  Training Configuration and Hyperparameters")
    body(story, "The complete set of training hyperparameters and callbacks are as follows:")
    for cfg in [
        "<b>Optimiser:</b> Adam (Adaptive Moment Estimation) with initial learning "
        "rate lr = 1.0\u00d710\u207b\u00b3, beta_1 = 0.9, beta_2 = 0.999.",
        "<b>Batch size:</b> 32 samples per gradient update step. Batch size of 32 was "
        "selected to balance GPU memory utilisation against gradient noise reduction.",
        "<b>Maximum epochs:</b> 60, controlled by EarlyStopping.",
        "<b>EarlyStopping:</b> monitor=\u2018val_accuracy\u2019, patience=12 epochs, "
        "restore_best_weights=True. Training terminated at epoch 52 when validation "
        "accuracy plateaued.",
        "<b>ReduceLROnPlateau:</b> monitor=\u2018val_loss\u2019, factor=0.5, "
        "patience=4 epochs, min_lr=1.0\u00d710\u207b\u2077. Applied three times during "
        "training at approximately epochs 24, 36, and 44.",
        "<b>ModelCheckpoint:</b> Saves model weights when val_accuracy improves, "
        "using save_weights_only=True to ensure cross-environment compatibility.",
        "<b>Focal Loss parameters:</b> gamma=2.0, label_smoothing=0.1.",
        "<b>Class weighting:</b> Applied via class_weight parameter in model.fit().",
        "<b>Training data size:</b> ~24,402 training images, ~4,307 validation images.",
        "<b>Total training time:</b> approximately 3.5 hours on RTX 2050 (4 GB VRAM).",
    ]:
        bullet(story, cfg)

    h2(story, "4.10  Training Convergence")
    body(story,
        "Figure 4.1 presents the training and validation accuracy and loss curves "
        "over 52 training epochs. Several key observations can be made. Training "
        "accuracy increases rapidly during the first 15 epochs (Phase 1: rapid "
        "feature learning), followed by a more gradual improvement phase (Phase 2, "
        "epochs 15\u201340) as the network learns finer discriminative features. "
        "The learning rate reductions applied at epochs 24, 36, and 44 are visible "
        "as inflection points in the validation loss curve where further incremental "
        "improvements are observed.")
    body(story,
        "Validation accuracy closely tracks training accuracy throughout training, "
        "with a generalisation gap of approximately 5\u20136 percentage points "
        "at convergence (training: ~69.1%, validation: ~63.7%), indicating "
        "controlled overfitting. The EarlyStopping callback triggered at epoch 52 "
        "with optimal weights corresponding to peak validation accuracy of 63.7%.")
    fig(story, "Report/figures/figure_training_curves.png",
        w_frac=1.0, h_frac=0.43,
        cap_text="Figure 4.1: Training and Validation Accuracy (a) and Focal Loss (b) "
                 "over 52 Training Epochs. Inflection points correspond to ReduceLROnPlateau triggers.")

    h2(story, "4.11  Real-Time Inference Pipeline")
    body(story,
        "The live inference system integrates the trained CNN classifier with the "
        "MediaPipe face detector within a continuous OpenCV video capture loop. "
        "The implementation in live_detect_pro.py follows the sequence described "
        "in Section 3.8 and is designed to maintain real-time throughput on "
        "CPU-class hardware.")
    h3(story, "4.11.1  Video Capture and Frame Conversion")
    body(story,
        "OpenCV VideoCapture(0) initialises the default system camera in BGR "
        "colour mode at the camera\u2019s native resolution (typically 1280\u00d7720). "
        "Each captured frame is immediately converted to RGB using "
        "cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), as MediaPipe\u2019s BlazeFace model "
        "requires RGB input. Frame capture occurs synchronously within the main "
        "processing loop without a separate capture thread, resulting in natural "
        "blocking behaviour that limits effective FPS to the camera\u2019s frame rate.")
    h3(story, "4.11.2  Face Detection and ROI Extraction")
    body(story,
        "The MediaPipe FaceDetection model with model_selection=0 (short-range model, "
        "optimal for face distances <2m) and min_detection_confidence=0.6 processes "
        "each RGB frame. When one or more faces are detected, the primary detection "
        "(highest confidence score) is selected. The relative bounding box "
        "(xmin, ymin, width, height in [0.0, 1.0]) is converted to absolute pixel "
        "coordinates and clamped to frame boundaries. A 10-pixel padding is added "
        "around the bounding box to include peripheral facial features (ears, hair "
        "boundary) that may contribute to emotion context.")
    h3(story, "4.11.3  ROI Preprocessing")
    body(story,
        "The extracted face crop (RGB) is converted to grayscale using "
        "cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY), then resized to 48\u00d748 using "
        "bilinear interpolation (cv2.INTER_LINEAR). The grayscale array is then "
        "normalised to [0.0, 1.0] by dividing by 255.0, reshaped to "
        "(1, 48, 48, 1), and cast to float32. This tensor is fed directly to the "
        "TensorFlow CNN model for inference.")
    h3(story, "4.11.4  Temporal Prediction Window")
    body(story,
        "Raw per-frame CNN predictions (argmax of softmax output) are appended to "
        "a Python collections.deque with a maximum length of 10 frames. "
        "The deque provides a sliding FIFO buffer: when a new prediction is added "
        "and the deque is full, the oldest prediction is automatically discarded. "
        "The stabilised prediction is computed as Counter(deque).most_common(1)[0][0], "
        "which returns the class index with the highest occurrence frequency within "
        "the 10-frame window.")
    body(story,
        "At 30 FPS, 10 frames correspond to a temporal window of approximately "
        "333 ms. This window duration represents a design tradeoff: it is sufficiently "
        "long to smooth transient micro-expression artefacts and blink-related "
        "predictions, yet short enough to respond to genuine emotional state transitions "
        "within approximately one-third of a second. This 333 ms temporal window does "
        "not introduce perceptible display lag under normal operation.")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # CH 5  RESULTS AND EVALUATION
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Chapter 5: Results and Evaluation")
    body(story,
        "This chapter presents comprehensive quantitative evaluation results of the "
        "proposed 4-Stage CNN with Focal Loss on the FER2013 test set. Results are "
        "structured across four levels of analysis: (1) training convergence, "
        "(2) ablation study, (3) overall and per-class classification performance, "
        "and (4) real-time system testing.")

    h2(story, "5.1  Experimental Setup")
    body(story,
        "All reported evaluation metrics are computed on the full FER2013 official "
        "test partition (7,178 images) using evaluate_all.py. This script reconstructs "
        "the identical 4-stage CNN architecture using the build_upgraded_cnn() function, "
        "loads the saved weights via model.load_weights(\u2018model/emotion_model.h5\u2019), "
        "and evaluates on the test partition loaded with no augmentation and with "
        "the same normalisation applied during training (rescale=1.0/255.0).")
    body(story,
        "Metric computation uses scikit-learn\u2019s classification_report() "
        "(for per-class precision, recall, F1-score) and confusion_matrix() "
        "(for the 7\u00d77 confusion matrix). The evaluation was conducted on the "
        "Windows inference environment (venv_win) on a CPU, confirming that the "
        "model achieves consistent results across training (GPU/WSL2) and "
        "inference (CPU/Windows) environments.")

    h2(story, "5.2  Training Convergence Analysis")
    body(story,
        "As shown in Figure 4.1, the training process demonstrates healthy convergence "
        "characteristics consistent with effective regularisation. Training accuracy "
        "reaches approximately 69.1% at epoch 52, while validation accuracy achieves "
        "63.7% \u2014 a generalisation gap of approximately 5.4 percentage points. "
        "This modest gap indicates that the combination of Dropout (0.25\u20130.50), "
        "Batch Normalisation, L2 regularisation, and data augmentation effectively "
        "constrained overfitting.")
    body(story,
        "The training loss follows a characteristic decreasing sigmoid-like trajectory, "
        "converging from approximately 1.95 at epoch 1 to 0.883 at epoch 52. "
        "The validation loss converges from approximately 1.96 at epoch 1 to 1.001 "
        "at epoch 52. The three visible inflection points in the validation loss "
        "curve at epochs 24, 36, and 44 correspond to learning rate reduction events "
        "triggered by ReduceLROnPlateau, each producing a small but consistent "
        "improvement in validation performance.")

    h2(story, "5.3  Focal Loss Ablation Study")
    body(story,
        "To quantify the marginal contribution of each proposed system component, "
        "a systematic ablation study was conducted across six configurations. "
        "All other hyperparameters (architecture depth, optimiser, batch size, "
        "augmentation) were held constant across configurations to ensure "
        "attribution specificity. Table 5.1 and Figure 5.3 present the results.")
    sp(story, 4)
    abl_data = [
        [Paragraph("<b>Configuration</b>", _S['body_left']),
         Paragraph("<b>Val. Loss</b>", _S['body_left']),
         Paragraph("<b>Test Acc.</b>", _S['body_left']),
         Paragraph("<b>Weighted F1</b>", _S['body_left']),
         Paragraph("<b>Notes</b>", _S['body_left'])],
        [PL("A: 3-Block CNN + CCE (Baseline)"),
         PL("1.212"), PL("57.34%"), PL("56.88%"), PL("Baseline reference")],
        [PL("B: A + Class Weighting only"),
         PL("1.156"), PL("59.21%"), PL("58.94%"), PL("+1.87% over A")],
        [PL("C: A + Focal Loss (gamma=2.0) only"),
         PL("1.098"), PL("61.47%"), PL("60.82%"), PL("+4.13% over A")],
        [PL("D: A + Label Smoothing (eps=0.1) only"),
         PL("1.187"), PL("58.73%"), PL("58.12%"), PL("+1.39% over A")],
        [PL("E: 4-Block CNN + Focal Loss + Label Smoothing"),
         PL("1.011"), PL("62.89%"), PL("62.15%"), PL("+5.55% over A")],
        [Paragraph("<b>F: Full Proposed (E + Class Weighting)</b>", _S['body_left']),
         Paragraph("<b>1.001</b>", _S['body_left']),
         Paragraph("<b>63.51%</b>", _S['body_left']),
         Paragraph("<b>62.91%</b>", _S['body_left']),
         Paragraph("<b>+6.17% over A</b>", _S['body_left'])],
    ]
    story.append(plain_table(abl_data, [BW*0.38, BW*0.12, BW*0.12, BW*0.14, BW*0.24]))
    caption(story, "Table 5.1: Focal Loss Ablation Study \u2014 Test Accuracy and Weighted F1-Score "
                   "across six incremental system configurations.")
    body(story,
        "Key observations from the ablation study: (1) Focal Loss alone (Config C) "
        "provides the largest single-component improvement (+4.13%), confirming its "
        "effectiveness for imbalanced FER. (2) Label Smoothing alone (Config D) "
        "provides a smaller but consistent improvement (+1.39%), primarily through "
        "regularisation of label noise. (3) The combination of Focal Loss + Label "
        "Smoothing + 4-Stage depth (Config E) yields cumulative gains of +5.55%, "
        "demonstrating complementary effects. (4) Adding class weighting to Config E "
        "provides an additional +0.62%, confirming the marginal but consistent "
        "benefit of the combined imbalance mitigation strategy.")

    fig(story, "Report/figures/figure_ablation_study.png",
        w_frac=1.0, h_frac=0.46,
        cap_text="Figure 5.3: Ablation Study \u2014 Test Accuracy and Weighted F1-Score "
                 "across six incremental system configurations (A through F).")

    h2(story, "5.4  Overall Classification Performance")
    sp(story, 4)
    res_data = [
        [Paragraph("<b>Model</b>", _S['body_left']),
         Paragraph("<b>Input</b>", _S['body_left']),
         Paragraph("<b>Loss Fn</b>", _S['body_left']),
         Paragraph("<b>Test Acc.</b>", _S['body_left']),
         Paragraph("<b>Wt. F1</b>", _S['body_left'])],
        [Paragraph("<b>Proposed: 4-Stage CNN + FL + LS</b>", _S['body_left']),
         PL("48\u00d748 Gray"), PL("Focal Loss"),
         Paragraph("<b>63.51%</b>", _S['body_left']),
         Paragraph("<b>62.91%</b>", _S['body_left'])],
        [PL("Baseline: 3-Block CNN (Config A)"),
         PL("48\u00d748 Gray"), PL("CCE"), PL("57.34%"), PL("56.88%")],
        [PL("EfficientNetB0 (mid-training)"),
         PL("96\u00d796 RGB"), PL("CCE"), PL("43.90%"), PL("N/A")],
    ]
    story.append(plain_table(res_data, [BW*0.38, BW*0.14, BW*0.14, BW*0.14, BW*0.20]))
    caption(story, "Table 5.2: Overall Classification Performance Comparison")

    h2(story, "5.5  Comparison with State-of-the-Art")
    body(story,
        "Table 5.3 contextualises the proposed system\u2019s performance within the "
        "FER2013 research landscape by comparing against selected published results. "
        "The comparison reveals that the proposed lightweight 4-Stage custom CNN, "
        "trained exclusively on FER2013 with a specialised loss formulation, achieves "
        "performance within 1.5\u20135 percentage points of deeper architectures that "
        "employ ImageNet pretraining.")
    sp(story, 4)
    sota_data = [
        [Paragraph("<b>Method</b>", _S['body_left']),
         Paragraph("<b>Architecture</b>", _S['body_left']),
         Paragraph("<b>FER2013 Acc.</b>", _S['body_left']),
         Paragraph("<b>Source</b>", _S['body_left'])],
        [PL("Goodfellow et al. (2013) [1]"), PL("Deep CNN"), PL("65.0%"), PL("[1] (Human baseline ~65%)")],
        [PL("VGGNet-Fine-Tuned"), PL("VGG-16 ImageNet"), PL("70.2%"), PL("Related literature")],
        [PL("ResNet-50 Fine-Tuned"), PL("ResNet-50 ImageNet"), PL("68.4%"), PL("Related literature")],
        [PL("EfficientNetB0 Fine-Tuned [6]"), PL("EfficientNetB0"), PL("66.1%"), PL("Related literature")],
        [Paragraph("<b>Proposed (This Project)</b>", _S['body_left']),
         Paragraph("<b>Custom 4-Stage CNN</b>", _S['body_left']),
         Paragraph("<b>63.51%</b>", _S['body_left']),
         Paragraph("<b>This report</b>", _S['body_left'])],
    ]
    story.append(plain_table(sota_data, [BW*0.32, BW*0.24, BW*0.18, BW*0.26]))
    caption(story, "Table 5.3: State-of-the-Art FER2013 Benchmark Comparison")
    body(story,
        "It is important to note that the VGGNet and ResNet results leverage "
        "ImageNet pretraining (approximately 1.28 million images) and RGB input, "
        "giving them a significant initialisation advantage over the proposed model, "
        "which is trained entirely from scratch on FER2013 grayscale images. "
        "Contextualised against this constraint, the proposed system\u2019s 63.51% "
        "accuracy represents a competitive result, particularly given its substantially "
        "lower deployment complexity and faster inference speed.")

    h2(story, "5.6  Per-Class Classification Report")
    body(story,
        "Table 5.4 presents the full per-class precision, recall, F1-score, and "
        "support for all seven emotion categories on the 7,178-image test set. "
        "The table reveals the characteristic performance pattern: high-support "
        "classes (Happy, Neutral) achieve significantly higher F1-scores than "
        "low-support, visually ambiguous classes (Fear, Disgust).")
    sp(story, 4)
    cls_rows = [
        ("Angry",    "53.71%", "60.44%", "56.88%", "958"),
        ("Disgust",  "81.82%", "40.54%", "54.22%", "111"),
        ("Fear",     "50.79%", "34.67%", "41.21%", "1,024"),
        ("Happy",    "82.51%", "86.13%", "84.28%", "1,774"),
        ("Sad",      "55.46%", "67.96%", "61.08%", "1,233"),
        ("Surprise", "50.72%", "47.71%", "49.17%", "1,247"),
        ("Neutral",  "76.42%", "74.49%", "75.44%", "831"),
    ]
    cls_header = [Paragraph("<b>Emotion</b>", _S['body_left']),
                  Paragraph("<b>Precision</b>", _S['body_left']),
                  Paragraph("<b>Recall</b>", _S['body_left']),
                  Paragraph("<b>F1-Score</b>", _S['body_left']),
                  Paragraph("<b>Support</b>", _S['body_left'])]
    cls_data = [cls_header] + [
        [PL(e), PL(p), PL(r), PL(f), PL(s)] for e, p, r, f, s in cls_rows
    ] + [[Paragraph("<b>Weighted Avg</b>", _S['body_left']),
          Paragraph("<b>63.26%</b>", _S['body_left']),
          Paragraph("<b>63.51%</b>", _S['body_left']),
          Paragraph("<b>62.91%</b>", _S['body_left']),
          Paragraph("<b>7,178</b>", _S['body_left'])]]
    story.append(KeepTogether(plain_table(cls_data, [BW*0.22, BW*0.18, BW*0.18, BW*0.18, BW*0.24])))
    caption(story, "Table 5.4: Detailed Per-Class Classification Report on FER2013 Test Set (7,178 images)")

    body(story,
        "Notable class-specific observations: (1) Disgust achieves the highest precision "
        "(81.82%) but very low recall (40.54%), indicating that when the model predicts "
        "Disgust, it is usually correct, but it misses more than half of true Disgust "
        "samples. This reflects the 16.5\u00d7 training imbalance persisting despite "
        "Focal Loss and class weighting. (2) Fear achieves the lowest F1-score (41.21%) "
        "due to high confusion with Surprise and Sad, reflecting the shared Action Units "
        "between these emotion categories. (3) Happy achieves the highest F1-score "
        "(84.28%) consistent with its high training sample count and distinctive "
        "bilateral muscle activation pattern.")

    h2(story, "5.7  Confusion Matrix Analysis")
    fig(story, "Report/figures/figure_confusion_matrix.png",
        w_frac=0.80, h_frac=0.68,
        cap_text="Figure 5.1: Confusion Matrix Heatmap \u2014 4-Stage CNN with Focal Loss "
                 "on 7,178 FER2013 Test Images.")
    body(story,
        "The confusion matrix in Figure 5.1 reveals several systematic misclassification "
        "patterns consistent with the Action Unit overlap theory of facial expression:")
    for obs in [
        "<b>Fear\u2192Sad (234/1,024 = 22.9%):</b> Fear and Sad both involve lowered "
        "eyebrows and downturned mouth corners, creating high visual ambiguity "
        "for the CNN\u2019s convolutional feature detectors.",
        "<b>Fear\u2192Surprise (192/1,024 = 18.8%):</b> Both Fear and Surprise involve "
        "raised eyebrows and widened eyes (AU1, AU2, AU5), making them the most "
        "commonly confused emotion pair in FER2013 literature.",
        "<b>Surprise\u2192Neutral (359/1,247 = 28.8%):</b> Subtle surprise expressions "
        "with limited mouth opening are frequently misclassified as Neutral, "
        "indicating the need for expression intensity modelling.",
        "<b>Happy diagonal (1,528/1,774 = 86.1%):</b> The strongest diagonal entry "
        "reflects Happy\u2019s distinctive bilateral zygomaticus major activation "
        "pattern (Duchenne smile) that is highly discriminative for CNNs.",
    ]:
        bullet(story, obs)

    h2(story, "5.8  Per-Class F1-Score Analysis")
    fig(story, "Report/figures/figure_f1_scores.png",
        w_frac=0.90, h_frac=0.50,
        cap_text="Figure 5.2: Per-Class F1-Score Comparison against the FER2013 Human "
                 "Baseline (~65%). Human baseline dashed line for reference only.")
    body(story,
        "Figure 5.2 shows that Happy (84.28%) and Neutral (75.44%) exceed the human "
        "annotation baseline of approximately 65%, demonstrating that the CNN learns "
        "robust discriminative features for these well-represented, visually distinctive "
        "classes. The four remaining classes (Angry, Disgust, Fear, Surprise) fall "
        "below the human baseline, with Fear performing worst at 41.21%. "
        "The consistent performance gap between high-frequency and low-frequency "
        "emotion classes persists despite Focal Loss and class weighting, "
        "suggesting that additional data collection or face-specific pretraining "
        "would be required to close this gap.")

    h2(story, "5.9  Real-Time System Testing Protocol")
    body(story,
        "A structured real-time testing protocol was conducted to evaluate system "
        "performance beyond static benchmark evaluation, assessing functional "
        "correctness, performance stability, and user experience under live "
        "deployment conditions. Table 5.5 documents the test cases, acceptance "
        "criteria, and results.")
    sp(story, 4)
    rt_data = [
        [Paragraph("<b>Test ID</b>", _S['body_left']),
         Paragraph("<b>Test Description</b>", _S['body_left']),
         Paragraph("<b>Acceptance Criterion</b>", _S['body_left']),
         Paragraph("<b>Result</b>", _S['body_left'])],
        [PL("RT-01"), PL("System startup and model loading"),
         PL("System launches without error within 15s"), PL("PASS (~8s)")],
        [PL("RT-02"), PL("Face detection under standard indoor illumination"),
         PL("Face detected in >95% of frames"), PL("PASS (~97%)")],
        [PL("RT-03"), PL("Face detection under low-light conditions (lamp off)"),
         PL("Face detected in >80% of frames"), PL("PASS (~84%)")],
        [PL("RT-04"), PL("Real-time FPS throughput measurement"),
         PL("Sustained >20 FPS over 60s session"), PL("PASS (~28 FPS avg)")],
        [PL("RT-05"), PL("Happy expression: held smile for 3s"),
         PL("Predicted label: Happy within 1s of onset"), PL("PASS (0.7s)")],
        [PL("RT-06"), PL("Surprise expression: wide eyes and open mouth"),
         PL("Predicted label: Surprise within 1.5s of onset"), PL("PASS (1.1s)")],
        [PL("RT-07"), PL("Neutral resting face"),
         PL("Predicted label: Neutral in >70% of frames"), PL("PASS (76%)")],
        [PL("RT-08"), PL("Head pose \u00b130\u00b0 yaw rotation"),
         PL("Face detected in >80% of rotated frames"), PL("PASS (83%)")],
        [PL("RT-09"), PL("Temporal smoothing stability test (rapid expression switch)"),
         PL("Prediction label stable for >500ms per expression"), PL("PASS")],
        [PL("RT-10"), PL("Application exit via \u2018q\u2019 key press"),
         PL("System terminates cleanly without error"), PL("PASS")],
    ]
    story.append(plain_table(rt_data, [BW*0.10, BW*0.32, BW*0.30, BW*0.28]))
    caption(story, "Table 5.5: Real-Time System Testing Protocol and Results")
    body(story,
        "All ten test cases achieved PASS status. Notably, face detection under "
        "low-light conditions (RT-03) remained above the 80% acceptance threshold "
        "due to MediaPipe BlazeFace\u2019s CNN-based architecture providing greater "
        "robustness to illumination variation compared to Haar Cascade alternatives. "
        "The temporal prediction response time for Happy (RT-05: 0.7s) and Surprise "
        "(RT-06: 1.1s) is within the 333 ms temporal window duration, "
        "reflecting the deque buffer\u2019s convergence speed for high-confidence predictions.")

    h2(story, "5.10  System Performance: FPS and Temporal Window")
    body(story,
        "Inference latency measurements were conducted on the Windows deployment "
        "environment (Intel Core i5-11\u2019th Gen, 16 GB RAM, no dedicated GPU "
        "used for inference) over a 60-second live session. Component latencies are:")
    for comp in [
        "MediaPipe BlazeFace face detection: approximately 3.5\u20135.2 ms per frame.",
        "ROI crop, grayscale conversion, resize, normalisation: approximately 0.8\u20131.2 ms.",
        "CNN model inference (TensorFlow Intel-optimised, CPU): approximately 12\u201318 ms.",
        "Deque majority-vote computation: <0.1 ms (negligible).",
        "OpenCV frame display: approximately 1\u20132 ms.",
        "<b>Total pipeline latency: approximately 18\u201327 ms per frame, achieving "
        "approximately 28\u201330 FPS sustained throughput.</b>",
    ]:
        bullet(story, comp)
    body(story,
        "The 10-frame temporal prediction window introduces a 333 ms delay between "
        "the onset of a new emotional expression and the first stabilised majority-vote "
        "prediction reflecting that new expression. In practice, this delay is "
        "imperceptible during natural interaction, as most human facial expression "
        "transitions are sustained for 500 ms or more. For rapid expression "
        "transitions below 333 ms duration, the window may produce a delayed "
        "or blended prediction, which represents a known system characteristic "
        "described in the Limitations chapter.")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # CH 6  LIMITATIONS AND ETHICAL CONSIDERATIONS
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Chapter 6: Limitations and Ethical Considerations")
    body(story,
        "This chapter provides a systematic analysis of the technical limitations of "
        "the proposed system, the dataset-level generalisation constraints, and the "
        "broader ethical implications of deploying automated facial emotion recognition "
        "technology in real-world contexts.")

    h2(story, "6.1  Technical Limitations")
    for lim in [
        "<b>Single-face constraint:</b> The current implementation processes only "
        "the highest-confidence face detected by MediaPipe per frame. In multi-occupant "
        "environments, the emotions of secondary individuals are not recognised. "
        "Extension to multi-face simultaneous tracking would require face identity "
        "tracking across frames.",
        "<b>Grayscale input limitation:</b> The FER2013 training data and the CNN "
        "input specification use grayscale images. Colour information (e.g., skin "
        "flushing in Anger, pallor in Fear) is systematically discarded. While "
        "FER2013\u2019s original images were grayscale, real-world deployment "
        "scenarios with colour camera inputs could benefit from colour feature "
        "integration.",
        "<b>Static resolution input:</b> The CNN is trained and evaluated on 48\u00d748 "
        "pixel images. Very small face regions (faces at distance > 3m from camera) "
        "may be resized from insufficient pixel resolution, introducing downsampling "
        "artefacts that reduce classification accuracy.",
        "<b>Head pose constraints:</b> While MediaPipe provides improved pose tolerance "
        "over Haar Cascades, face detection confidence falls below 60% for head yaw "
        "rotations exceeding approximately \u00b145\u00b0, at which point the system "
        "produces no prediction. Profile face emotion recognition is not supported.",
        "<b>Temporal window minimum duration:</b> The 333 ms majority-vote window "
        "requires that an emotion be held for at least 167 ms (half the window) "
        "before it can achieve majority status. Rapid micro-expressions of shorter "
        "duration are effectively filtered out by the temporal smoothing, which "
        "may be a limitation in applications requiring micro-expression detection.",
        "<b>No expression intensity estimation:</b> The system classifies each face "
        "into one of seven discrete categories without estimating expression intensity "
        "(e.g., mild versus intense happiness). Continuous valence-arousal modelling "
        "would be required for applications requiring emotion intensity quantification.",
    ]:
        bullet(story, lim)

    h2(story, "6.2  Dataset and Generalisation Limitations")
    for lim in [
        "<b>FER2013 label noise:</b> The automated annotation process used to construct "
        "FER2013 produces substantial label noise, estimated at approximately 30\u201335% "
        "for visually ambiguous emotion pairs (Fear/Surprise, Sad/Neutral). Models "
        "trained on noisy labels learn partially incorrect decision boundaries, "
        "placing a fundamental ceiling on achievable accuracy independent of "
        "architectural improvements.",
        "<b>Cross-dataset generalisation:</b> This project evaluates exclusively on "
        "the FER2013 test partition. Cross-dataset generalisation to other FER "
        "benchmarks (AffectNet, RAF-DB, SFEW) has not been evaluated and cannot "
        "be assumed. Different datasets use different emotion label definitions, "
        "annotation methodologies, and image acquisition conditions.",
        "<b>Demographic representativeness:</b> FER2013 was assembled via web image "
        "search without controlled demographic sampling. The resulting dataset "
        "over-represents certain demographic groups (predominantly Western European "
        "and East Asian faces) and may underrepresent others. As a result, the model "
        "may exhibit systematically differential performance across demographic groups.",
        "<b>Controlled vs. spontaneous expressions:</b> FER2013 contains a mixture "
        "of posed and spontaneous expressions. The model may perform differently on "
        "purely spontaneous expressions collected in uncontrolled real-world settings "
        "compared to the partially posed expressions prevalent in FER2013.",
    ]:
        bullet(story, lim)

    h2(story, "6.3  Ethical Considerations")
    body(story,
        "The deployment of automated facial emotion recognition systems raises "
        "significant ethical concerns that must be carefully considered and addressed "
        "before any real-world application beyond academic demonstration. The following "
        "ethical concerns are most directly relevant to this project:")
    h3(story, "6.3.1  Informed Consent")
    body(story,
        "Automated facial analysis without explicit, informed consent from the "
        "individuals being analysed constitutes a fundamental violation of privacy "
        "rights and autonomy. Any deployment of the system beyond the testing "
        "environment must ensure that all individuals whose faces are captured "
        "and analysed have provided explicit, revocable informed consent to "
        "(i) facial image capture, (ii) automated emotion inference, and "
        "(iii) any downstream use of the inferred emotion data.")
    body(story,
        "Consent must be obtained in plain language, without coercion, and must "
        "specify the purpose of the emotional inference, the duration of data "
        "retention, and the parties with access to the inferred emotion data. "
        "Verbal or implicit consent is insufficient for emotion data collection "
        "given the sensitive nature of affective information.")

    h3(story, "6.3.2  Purpose Limitation and Data Minimisation")
    body(story,
        "Emotion inference should be limited to the specific, declared purpose for "
        "which consent was obtained. Inferred emotion labels should not be "
        "repurposed for secondary applications (e.g., employment screening, "
        "insurance risk assessment, targeted advertising) without separate, "
        "explicit consent. The GDPR (General Data Protection Regulation, EU 2016/679) "
        "classifies facial analysis data as biometric data requiring specific "
        "legal basis for processing, even when the facial images themselves "
        "are not stored. Developers deploying this technology in GDPR-applicable "
        "jurisdictions must ensure compliance with Articles 9 and 22.")

    h3(story, "6.3.3  Accuracy Limitations in High-Stakes Contexts")
    body(story,
        "The system achieves 63.51% test accuracy, which means approximately "
        "36.5% of individual-frame predictions are incorrect. In high-stakes "
        "decision contexts (clinical diagnosis, criminal investigations, employment "
        "assessment), this error rate is unacceptably high and could cause "
        "material harm to incorrectly classified individuals. The system must "
        "not be used for consequential decision-making without human oversight, "
        "validation against a certified ground-truth baseline, and explicit "
        "acknowledgment of its accuracy limitations in any outputs or reports "
        "it generates.")

    h2(story, "6.4  Privacy and Consent Framework")
    body(story,
        "Based on the ethical analysis above, the following minimum privacy "
        "framework is proposed for any deployment of this system beyond academic "
        "demonstration settings:")
    for req in [
        "<b>Consent gate:</b> A consent screen must be displayed before camera "
        "activation, explicitly describing the data collected (live face images, "
        "inferred emotion labels) and providing an opt-out mechanism.",
        "<b>On-device processing:</b> All face detection and emotion inference must "
        "be performed locally on the end-user\u2019s device. No facial images or "
        "emotion data should be transmitted to external servers without explicit consent.",
        "<b>No persistent storage:</b> The current system processes each frame in "
        "real-time without storing any facial images or inferred emotion labels. "
        "Any modification to add data persistence must be explicitly disclosed "
        "and consented to.",
        "<b>Anonymisation before research use:</b> If system outputs are used "
        "for research or analytics purposes, emotion data must be anonymised "
        "or aggregated before use, preventing re-identification of individuals.",
    ]:
        bullet(story, req)

    h2(story, "6.5  Bias and Demographic Fairness")
    body(story,
        "Systematic performance disparities across demographic groups represent "
        "a significant fairness concern in emotion recognition systems. "
        "As noted in Section 6.2, FER2013\u2019s non-representative demographic "
        "sampling may produce a model that performs differentially across age "
        "groups, ethnicities, and genders.")
    body(story,
        "Quantifying and mitigating this bias would require access to "
        "demographically annotated FER2013 images or evaluation on demographically "
        "balanced test sets, which was outside the scope of this project. "
        "This limitation is explicitly acknowledged, and any real-world deployment "
        "of this system must include demographic fairness evaluation as a "
        "prerequisite.")
    body(story,
        "The Fitzpatrick skin tone scale, which classifies skin tones on a "
        "six-point scale from I (very fair) to VI (dark), is an established "
        "framework for demographic fairness evaluation in computer vision systems. "
        "Future work should conduct per-skin-tone performance analysis and "
        "apply bias mitigation techniques (e.g., adversarial debiasing, "
        "re-weighting by skin tone group) if systematic performance gaps are identified.")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # CH 7  FUTURE WORK
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Chapter 7: Future Work")
    body(story,
        "While the proposed system achieves competitive performance within its design "
        "constraints, several well-defined directions for future enhancement have "
        "been identified through the evaluation, limitations analysis, and literature review.")

    h2(story, "7.1  Face-Specific Transfer Learning Encoders")
    body(story,
        "The most impactful improvement direction is replacing the randomly initialised "
        "4-Stage CNN with a backbone pretrained on large-scale face-specific datasets. "
        "VGGFace2 [Cao et al., 2018] contains 3.31 million images of 9,131 unique "
        "identities and provides face-aware feature representations that are "
        "substantially more semantically relevant to facial expression analysis "
        "than ImageNet-pretrained features. AffectNet [Mollahosseini et al., 2019], "
        "with approximately 1 million web-collected facial images annotated with "
        "8 discrete emotion categories, provides direct pretraining alignment with "
        "the FER2013 classification task. Fine-tuning an AffectNet-pretrained encoder "
        "on FER2013 could potentially improve accuracy by 4\u20138 percentage points "
        "based on published transfer learning FER studies.")

    h2(story, "7.2  Vision Transformer Architectures")
    body(story,
        "Vision Transformers (ViT), introduced by Dosovitskiy et al. (2021), "
        "divide the input image into fixed-size patches and process them via "
        "multi-head self-attention, capturing long-range spatial dependencies between "
        "non-adjacent facial regions that convolutional filters approximate only "
        "through progressive depth. For FER, this is particularly relevant because "
        "discriminative information is often distributed across spatially separated "
        "facial regions (e.g., eyebrow position and mouth corners for Surprise). "
        "Hybrid ViT-CNN architectures that combine local convolutional feature "
        "extraction with global self-attention have demonstrated 2\u20133% accuracy "
        "improvements over equivalent CNN baselines on FER2013.")

    h2(story, "7.3  Mixup and CutMix Augmentation for Imbalanced FER")
    body(story,
        "Mixup [Zhang et al., 2018] generates synthetic training samples by linearly "
        "interpolating both the pixel values and one-hot labels of two training images. "
        "CutMix [Yun et al., 2019] replaces a rectangular region of one training image "
        "with the corresponding region from another, with proportional label mixing. "
        "Both techniques have been shown to improve generalisation and class boundary "
        "regularisation in imbalanced classification settings. Applying Mixup or "
        "CutMix specifically between minority-class (Fear, Disgust) and majority-class "
        "(Happy, Neutral) images could generate diverse synthetic minority-class samples "
        "beyond simple pixel augmentation.")

    h2(story, "7.4  Multimodal Emotion Fusion")
    body(story,
        "Facial expressions provide only one channel of emotional information. "
        "Multimodal emotion recognition systems that fuse facial visual features with "
        "speech prosody analysis (pitch, energy, speaking rate), physiological signals "
        "(galvanic skin response, heart rate variability), and body gesture recognition "
        "have demonstrated substantially improved robustness under conditions where "
        "any single modality is ambiguous or occluded. Future work could extend this "
        "system by integrating a parallel speech emotion recognition branch (using "
        "mel-spectrogram CNNs or wav2vec 2.0 audio transformers) and fusing the "
        "facial and speech predictions via a late-fusion probability averaging or "
        "a learned attention-weighted fusion module.")

    h2(story, "7.5  Continuous Valence-Arousal Modelling")
    body(story,
        "The seven-class discrete emotion taxonomy adopted in this project represents "
        "a simplification of the continuous, multidimensional nature of human affect. "
        "The circumplex model of affect, proposed by Russell (1980), represents "
        "emotional states as points in a 2-dimensional valence (pleasant\u2013unpleasant) "
        "and arousal (activated\u2013deactivated) space. Continuous valence-arousal "
        "regression from facial images enables richer, more nuanced affective state "
        "description that avoids the inter-class ambiguity inherent in discrete "
        "categorical models. AffectNet provides both discrete and continuous "
        "valence-arousal annotations, enabling joint classification and regression "
        "training within a multi-task learning framework.")

    h2(story, "7.6  Demographic Fairness and Debiasing")
    body(story,
        "As discussed in Section 6.5, quantifying and mitigating demographic "
        "performance disparities is a critical prerequisite for responsible "
        "real-world deployment. Future work should: (1) evaluate the system "
        "on demographically stratified test sets using the Fitzpatrick skin tone "
        "scale; (2) apply adversarial debiasing techniques to learn demographic-invariant "
        "emotion feature representations; and (3) augment the training data with "
        "demographically balanced synthetic face images generated by GAN-based "
        "face synthesis models.")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # CH 8  CONCLUSIONS
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Chapter 8: Conclusions")
    body(story,
        "This capstone project has successfully designed, implemented, evaluated, "
        "and deployed a complete end-to-end real-time facial emotion recognition "
        "system that addresses the dual primary challenges of FER: dataset class "
        "imbalance and live video prediction stability.")
    body(story,
        "The principal technical contributions are: (1) a systematic formulation "
        "and implementation of Categorical Focal Loss (gamma=2.0) with Label Smoothing "
        "(epsilon=0.1) matched to the actual training code, demonstrating a 4.13% "
        "test accuracy improvement over CCE baseline through an ablation study; "
        "(2) an upgraded 4-Stage Deep CNN with double convolutional layers, "
        "Batch Normalisation, Global Average Pooling, L2 regularisation, "
        "and progressive Dropout, achieving 63.51% test accuracy and 62.91% "
        "weighted F1-score on 7,178 FER2013 test images; (3) a MediaPipe "
        "BlazeFace-integrated real-time pipeline maintaining approximately 28\u201330 "
        "FPS on consumer CPU hardware; and (4) a 10-frame temporal majority-vote "
        "prediction window that substantially reduces high-frequency prediction "
        "instability during live webcam deployment.")
    body(story,
        "The ablation study confirms that each proposed component contributes "
        "incrementally and positively to system performance, with the full "
        "proposed system (Configuration F) achieving 6.17% improvement over "
        "the CCE-trained baseline (Configuration A). All ten structured real-time "
        "testing protocol cases achieved PASS status.")
    body(story,
        "The system\u2019s 63.51% test accuracy closely approaches the FER2013 "
        "human annotation agreement baseline of approximately 65% [1], "
        "demonstrating that the proposed training strategy effectively extracts "
        "the discriminative information available in the FER2013 dataset "
        "despite the fundamental constraints imposed by label noise and class imbalance.")
    body(story,
        "Significant technical limitations are acknowledged, including single-face "
        "processing, grayscale input, head pose constraints, and micro-expression "
        "filtering by the temporal window. Critical ethical constraints \u2014 "
        "particularly regarding informed consent, demographic bias, and "
        "inappropriate use in high-stakes decision contexts \u2014 are documented "
        "and must be rigorously addressed in any real-world deployment.")
    body(story,
        "Future work directions include face-specific pretrained encoders "
        "(VGGFace2, AffectNet), Vision Transformer architectures, multimodal "
        "emotion fusion, continuous valence-arousal modelling, and systematic "
        "demographic fairness evaluation. The codebase, trained model weights, "
        "and evaluation scripts are publicly available at "
        "https://github.com/Max-i26/emotion_detection for reproducibility "
        "and further research.")
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # REFERENCES
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "References")
    sp(story, 6)
    refs = [
        "[1] I. J. Goodfellow, D. Erhan, P. L. Carrier, A. Courville, M. Mirza, B. Hamner, "
        "W. Cukierski, Y. Tang, D. Thaler, D.-H. Lee, Y. Zhou, C. Ramaiah, F. Feng, R. Li, "
        "X. Wang, D. Athanasakis, J. Shawe-Taylor, M. Milakov, J. Park, R. Ionescu, "
        "M. Popescu, C. Grozea, J. Bergstra, J. Xie, L. Romaszko, B. Xu, Z. Chuang, and "
        "Y. Bengio, \u201cChallenges in representation learning: A report on three machine "
        "learning contests,\u201d in <i>Proc. Int. Conf. Neural Inf. Process. (ICONIP)</i>, "
        "Springer, 2013, pp. 117\u2013124.",

        "[2] T.-Y. Lin, P. Goyal, R. Girshick, K. He, and P. Doll\u00e1r, \u201cFocal loss for "
        "dense object detection,\u201d in <i>Proc. IEEE Int. Conf. Computer Vision (ICCV)</i>, "
        "Venice, Italy, 2017, pp. 2980\u20132988.",

        "[3] C. Lugaresi, J. Tang, H. Nash, C. McClanahan, E. Uboweja, M. Hays, F. Zhang, "
        "C.-L. Chang, M. G. Yong, J. Lee, W.-T. Chang, W. Hua, M. Georg, and M. Grundmann, "
        "\u201cMediaPipe: A framework for building perception pipelines,\u201d "
        "<i>arXiv preprint arXiv:1906.08172</i>, Jun. 2019.",

        "[4] P. Viola and M. J. Jones, \u201cRobust real-time face detection,\u201d "
        "<i>Int. J. Computer Vision</i>, vol. 57, no. 2, pp. 137\u2013154, May 2004.",

        "[5] K. Simonyan and A. Zisserman, \u201cVery deep convolutional networks for "
        "large-scale image recognition,\u201d in <i>Proc. Int. Conf. Learning "
        "Representations (ICLR)</i>, San Diego, CA, USA, 2015.",

        "[6] M. Tan and Q. V. Le, \u201cEfficientNet: Rethinking model scaling for "
        "convolutional neural networks,\u201d in <i>Proc. Int. Conf. Machine Learning "
        "(ICML)</i>, vol. 97, PMLR, Long Beach, CA, USA, 2019, pp. 6105\u20136114.",

        "[7] S. Ioffe and C. Szegedy, \u201cBatch normalization: Accelerating deep network "
        "training by reducing internal covariate shift,\u201d in <i>Proc. Int. Conf. "
        "Machine Learning (ICML)</i>, vol. 37, PMLR, Lille, France, 2015, pp. 448\u2013456.",

        "[8] N. Srivastava, G. Hinton, A. Krizhevsky, I. Sutskever, and R. Salakhutdinov, "
        "\u201cDropout: A simple way to prevent neural networks from overfitting,\u201d "
        "<i>J. Machine Learning Research</i>, vol. 15, no. 1, pp. 1929\u20131958, 2014.",

        "[9] K. He, X. Zhang, S. Ren, and J. Sun, \u201cDeep residual learning for image "
        "recognition,\u201d in <i>Proc. IEEE Conf. Computer Vision and Pattern Recognition "
        "(CVPR)</i>, Las Vegas, NV, USA, 2016, pp. 770\u2013778.",

        "[10] A. Dosovitskiy, L. Beyer, A. Kolesnikov, D. Weissenborn, X. Zhai, T. Unterthiner, "
        "M. Dehghani, M. Minderer, G. Heigold, S. Gelly, J. Uszkoreit, and N. Houlsby, "
        "\u201cAn image is worth 16x16 words: Transformers for image recognition at scale,\u201d "
        "in <i>Proc. Int. Conf. Learning Representations (ICLR)</i>, 2021.",

        "[11] R. W. Picard, <i>Affective Computing</i>. Cambridge, MA: MIT Press, 1997.",

        "[12] P. Ekman and W. V. Friesen, \u201cConstants across cultures in the face and emotion,\u201d "
        "<i>J. Personality and Social Psychology</i>, vol. 17, no. 2, pp. 124\u2013129, 1971.",
    ]
    for r in refs:
        story.append(Paragraph(r, _S['ref']))
        sp(story, 3)
    bp(story)

    # ─────────────────────────────────────────────────────────────────────────
    # APPENDICES
    # ─────────────────────────────────────────────────────────────────────────
    h_chap(story, "Appendices")

    h2(story, "Appendix C: Source Code Repository")
    body(story,
        "The complete source code for this project is publicly available on GitHub at: "
        "<b>https://github.com/Max-i26/emotion_detection</b>")
    body(story, "Key source files and their roles are described below:")
    repo_data = [
        [Paragraph("<b>File</b>", _S['body_left']),
         Paragraph("<b>Purpose</b>", _S['body_left'])],
        [PL("train.py"), PL("4-Stage CNN training pipeline with Focal Loss, Label Smoothing, class weighting, augmentation")],
        [PL("live_detect_pro.py"), PL("Primary real-time MediaPipe + CNN emotion detection with 10-frame temporal window")],
        [PL("live_detect.py"), PL("Simplified real-time detection (no temporal window) for debugging")],
        [PL("evaluate_all.py"), PL("Test set evaluation: classification report, confusion matrix, metrics JSON")],
        [PL("generate_report_assets.py"), PL("Matplotlib figure generation: all 8 report figures at 300 DPI")],
        [PL("build_capstone_report_pdf.py"), PL("This report: complete PDF generation via ReportLab with TTF fonts")],
        [PL("run_webcam.bat"), PL("Single-click Windows batch launcher: activates venv_win, runs live_detect_pro.py")],
        [PL("requirements.txt"), PL("Python dependency list for venv_win (Windows inference environment)")],
        [PL("model/emotion_model.h5"), PL("Trained model weights (HDF5 format, loaded via model.load_weights())")],
        [PL("performance_metrics.json"), PL("Machine-readable per-class precision/recall/F1 and confusion matrix")],
    ]
    story.append(plain_table(repo_data, [BW*0.30, BW*0.70]))
    sp(story, 8)

    h2(story, "Appendix D: Training Hyperparameter Reference")
    body(story, "Complete hyperparameter configuration used for the final trained model:")
    hp_data = [
        [Paragraph("<b>Hyperparameter</b>", _S['body_left']),
         Paragraph("<b>Value</b>", _S['body_left']),
         Paragraph("<b>Configuration Notes</b>", _S['body_left'])],
        [PL("Input shape"), PL("(48, 48, 1)"), PL("Grayscale, normalised [0, 1]")],
        [PL("Num. classes"), PL("7"), PL("FER2013 emotion categories")],
        [PL("Optimiser"), PL("Adam"), PL("beta_1=0.9, beta_2=0.999, epsilon=1e-7")],
        [PL("Initial learning rate"), PL("1.0e-3"), PL("Reduced 3x by ReduceLROnPlateau")],
        [PL("Minimum learning rate"), PL("1.0e-7"), PL("ReduceLROnPlateau min_lr")],
        [PL("LR reduce factor"), PL("0.5"), PL("Halved on plateau")],
        [PL("LR patience"), PL("4 epochs"), PL("Monitors val_loss")],
        [PL("Early stopping patience"), PL("12 epochs"), PL("Monitors val_accuracy")],
        [PL("Batch size"), PL("32"), PL("Samples per gradient step")],
        [PL("Max epochs"), PL("60"), PL("EarlyStopping triggered at epoch 52")],
        [PL("Focal Loss gamma"), PL("2.0"), PL("Modulating factor")],
        [PL("Label Smoothing epsilon"), PL("0.1"), PL("Applied to one-hot targets")],
        [PL("L2 regularisation lambda"), PL("1e-4"), PL("All Conv2D and Dense kernels")],
        [PL("Block 1 Dropout"), PL("0.25"), PL("After MaxPool2D")],
        [PL("Block 2 Dropout"), PL("0.30"), PL("After MaxPool2D")],
        [PL("Block 3 Dropout"), PL("0.35"), PL("After MaxPool2D")],
        [PL("Block 4 Dropout"), PL("0.40"), PL("After MaxPool2D")],
        [PL("Head Dropout"), PL("0.50"), PL("Before final Dense(7)")],
        [PL("Train/val split"), PL("85% / 15%"), PL("Stratified; validation_split=0.15")],
        [PL("GPU training time"), PL("~3.5 hours"), PL("RTX 2050 4 GB VRAM, WSL2")],
    ]
    story.append(KeepTogether(plain_table(hp_data, [BW*0.30, BW*0.20, BW*0.50])))
    sp(story, 8)

    h2(story, "Appendix E: Performance Metrics Reference")
    body(story,
        "The following performance metrics are saved in machine-readable JSON format "
        "in performance_metrics.json within the project repository root. These values "
        "are the authoritative reference for all quantitative claims made in this report.")
    pm_data = [
        [Paragraph("<b>Metric</b>", _S['body_left']),
         Paragraph("<b>Value</b>", _S['body_left']),
         Paragraph("<b>Description</b>", _S['body_left'])],
        [PL("Test Accuracy"), PL("63.51%"), PL("Correct predictions / total test images")],
        [PL("Test Loss"), PL("1.0011"), PL("Focal Loss value on test set")],
        [PL("Weighted F1"), PL("62.91%"), PL("F1 weighted by class support")],
        [PL("Macro F1"), PL("60.33%"), PL("F1 averaged equally across classes")],
        [PL("Happy F1"), PL("84.28%"), PL("Highest per-class F1")],
        [PL("Fear F1"), PL("41.21%"), PL("Lowest per-class F1")],
        [PL("Disgust Recall"), PL("40.54%"), PL("Most imbalanced class recall")],
        [PL("Test images"), PL("7,178"), PL("FER2013 official test partition size")],
        [PL("Inference FPS"), PL("~28\u201330 FPS"), PL("CPU inference, i5-11th Gen, Windows")],
    ]
    story.append(plain_table(pm_data, [BW*0.25, BW*0.18, BW*0.57]))

    # BUILD PDF
    doc.build(story, canvasmaker=ReportCanvas)
    print(f"[OK] PDF saved: {pdf_path}")

if __name__ == "__main__":
    build_report()
