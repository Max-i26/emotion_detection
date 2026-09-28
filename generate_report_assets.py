import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

os.makedirs("Report/figures", exist_ok=True)

# Set global monochrome / grayscale publication style
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.edgecolor'] = 'black'
plt.rcParams['axes.linewidth'] = 1.0

# -------------------------------------------------------------
# 1. Dataset Distribution Chart (Grayscale)
# -------------------------------------------------------------
def generate_dataset_distribution():
    emotions = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]
    train_counts = [3995, 436, 4097, 7215, 4830, 3171, 4965]
    test_counts = [958, 111, 1024, 1774, 1233, 1247, 831]
    
    x = np.arange(len(emotions))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    rects1 = ax.bar(x - width/2, train_counts, width, label='Train Set (28,709)', color='#404040', edgecolor='black')
    rects2 = ax.bar(x + width/2, test_counts, width, label='Test Set (7,178)', color='#a0a0a0', edgecolor='black')
    
    ax.set_ylabel('Number of Images', fontsize=11, fontweight='bold')
    ax.set_xlabel('Emotion Classes', fontsize=11, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(emotions, fontsize=10)
    ax.legend(frameon=True, edgecolor='black')
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    for rect in rects1:
        height = rect.get_height()
        ax.annotate(f'{height}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 2),  
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=7.5)
                    
    for rect in rects2:
        height = rect.get_height()
        ax.annotate(f'{height}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 2),  
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=7.5)

    plt.tight_layout()
    plt.savefig("Report/figures/figure_dataset_distribution.png", dpi=300)
    plt.close()
    print("[OK] Generated figure_dataset_distribution.png")

# -------------------------------------------------------------
# 2. Confusion Matrix Heatmap (Grayscale)
# -------------------------------------------------------------
def generate_confusion_matrix_plot():
    emotions = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]
    cm = np.array([
        [579,   5,  69,  45, 122, 122,  16],
        [ 40,  45,   5,   6,   3,  11,   1],
        [148,   1, 355,  46, 136, 224, 114],
        [ 41,   0,  34, 1528, 102,  42,  27],
        [ 77,   1,  45,  96, 838, 157,  19],
        [164,   2, 115,  81, 276, 595,  14],
        [ 29,   1,  76,  50,  34,  22, 619]
    ])
    
    fig, ax = plt.subplots(figsize=(7, 6), dpi=300)
    cax = ax.matshow(cm, cmap=plt.cm.Greys, alpha=0.85)
    
    fig.colorbar(cax)
    
    ax.set_xticks(range(len(emotions)))
    ax.set_yticks(range(len(emotions)))
    ax.set_xticklabels(emotions, rotation=45, ha='left', fontsize=10)
    ax.set_yticklabels(emotions, fontsize=10)
    
    ax.set_xlabel('Predicted Label', fontsize=11, fontweight='bold', labelpad=10)
    ax.set_ylabel('True Label', fontsize=11, fontweight='bold')
    
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val = cm[i, j]
            color = "white" if val > thresh else "black"
            ax.text(j, i, f"{val}", ha="center", va="center", color=color, fontsize=9.5, fontweight='bold' if i==j else 'normal')
            
    plt.tight_layout()
    plt.savefig("Report/figures/figure_confusion_matrix.png", dpi=300)
    plt.close()
    print("[OK] Generated figure_confusion_matrix.png")

# -------------------------------------------------------------
# 3. Per-Class F1-Score Bar Chart
# -------------------------------------------------------------
def generate_f1_score_chart():
    emotions = ["Happy", "Neutral", "Sad", "Angry", "Disgust", "Surprise", "Fear"]
    f1_scores = [84.28, 75.44, 61.08, 56.88, 54.22, 49.17, 41.21]
    
    fig, ax = plt.subplots(figsize=(6.5, 4), dpi=300)
    bars = ax.barh(emotions, f1_scores, color='#606060', edgecolor='black', height=0.55)
    
    ax.set_xlabel('F1-Score (%)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Emotion Class', fontsize=11, fontweight='bold')
    ax.set_xlim(0, 100)
    ax.invert_yaxis()
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    
    for bar in bars:
        width = bar.get_width()
        ax.annotate(f'{width:.2f}%',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(3, 0),
                    textcoords="offset points",
                    ha='left', va='center', fontsize=9, fontweight='bold')
                    
    plt.tight_layout()
    plt.savefig("Report/figures/figure_f1_scores.png", dpi=300)
    plt.close()
    print("[OK] Generated figure_f1_scores.png")

# -------------------------------------------------------------
# 4. Use Case Diagram
# -------------------------------------------------------------
def generate_use_case_diagram():
    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=300)
    ax.axis('off')
    
    rect = plt.Rectangle((0.25, 0.05), 0.70, 0.90, fill=None, edgecolor='black', linewidth=1.5)
    ax.add_patch(rect)
    ax.text(0.60, 0.91, 'Real-Time Emotion AI System Boundary', fontsize=11, fontweight='bold', ha='center')
    
    ax.plot([0.10, 0.10], [0.45, 0.55], color='black', lw=2)
    circle = plt.Circle((0.10, 0.60), 0.04, color='black', fill=False, lw=2)
    ax.add_patch(circle)
    ax.plot([0.06, 0.14], [0.52, 0.52], color='black', lw=2)
    ax.plot([0.10, 0.06], [0.45, 0.35], color='black', lw=2)
    ax.plot([0.10, 0.14], [0.45, 0.35], color='black', lw=2)
    ax.text(0.10, 0.28, 'User / Subject', fontsize=10, fontweight='bold', ha='center')
    
    use_cases = [
        ("UC-1: Live Video Capture", 0.78),
        ("UC-2: Face Detection (MediaPipe)", 0.62),
        ("UC-3: Preprocessing & Grayscale Scaling", 0.46),
        ("UC-4: Emotion Classification (4-Stage CNN)", 0.30),
        ("UC-5: Temporal Prediction Smoothing", 0.14)
    ]
    
    for uc_title, y_pos in use_cases:
        bbox_props = dict(boxstyle="round,pad=0.5", fc="#f8f8f8", ec="black", lw=1.2)
        ax.text(0.60, y_pos, uc_title, fontsize=9.5, fontweight='bold', ha='center', va='center', bbox=bbox_props)
        ax.annotate('', xy=(0.42, y_pos), xytext=(0.16, 0.50),
                    arrowprops=dict(arrowstyle="-", color="black", lw=1.0))

    plt.xlim(0, 1.0)
    plt.ylim(0, 1.0)
    plt.tight_layout()
    plt.savefig("Report/figures/figure_use_case_diagram.png", dpi=300)
    plt.close()
    print("[OK] Generated figure_use_case_diagram.png")

# -------------------------------------------------------------
# 5. System Architecture & Pipeline Flow Diagram
# -------------------------------------------------------------
def generate_system_architecture_diagram():
    fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=300)
    ax.axis('off')
    
    boxes = [
        ("Webcam Input\n(Live Video Stream)", 0.08, 0.40, 0.16, 0.20),
        ("MediaPipe Face Detector\n(ROI Extraction)", 0.28, 0.40, 0.17, 0.20),
        ("Preprocessing\n(48x48 Grayscale [0,1])", 0.49, 0.40, 0.17, 0.20),
        ("4-Stage ConvNet\n(Focal Loss Model)", 0.70, 0.40, 0.15, 0.20),
        ("10-Frame Majority Vote\n& Bounding Box Overlay", 0.89, 0.40, 0.17, 0.20)
    ]
    
    for title, x, y, w, h in boxes:
        rect = plt.Rectangle((x - w/2, y - h/2), w, h, facecolor='#f4f4f4', edgecolor='black', linewidth=1.5, linestyle='-')
        ax.add_patch(rect)
        ax.text(x, y, title, fontsize=8.0, fontweight='bold', ha='center', va='center', multialignment='center')
        
    arrow_props = dict(arrowstyle="->", color="black", lw=1.5, mutation_scale=15)
    ax.annotate('', xy=(0.195, 0.40), xytext=(0.165, 0.40), arrowprops=arrow_props)
    ax.annotate('', xy=(0.405, 0.40), xytext=(0.365, 0.40), arrowprops=arrow_props)
    ax.annotate('', xy=(0.625, 0.40), xytext=(0.575, 0.40), arrowprops=arrow_props)
    ax.annotate('', xy=(0.805, 0.40), xytext=(0.775, 0.40), arrowprops=arrow_props)

    ax.text(0.50, 0.85, 'System Architecture & Real-Time Processing Pipeline', fontsize=11, fontweight='bold', ha='center')
    
    plt.xlim(0, 1.0)
    plt.ylim(0, 1.0)
    plt.tight_layout()
    plt.savefig("Report/figures/figure_system_architecture.png", dpi=300)
    plt.close()
    print("[OK] Generated figure_system_architecture.png")

# -------------------------------------------------------------
# 6. Sequence Diagram
# -------------------------------------------------------------
def generate_sequence_diagram():
    fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=300)
    ax.axis('off')
    
    lifelines = [
        ("User", 0.10),
        ("Camera Feed", 0.28),
        ("MediaPipe", 0.46),
        ("4-Stage CNN", 0.64),
        ("Display UI", 0.82)
    ]
    
    for title, x in lifelines:
        bbox_props = dict(boxstyle="square,pad=0.4", fc="#e8e8e8", ec="black", lw=1.2)
        ax.text(x, 0.92, title, fontsize=9.5, fontweight='bold', ha='center', bbox=bbox_props)
        ax.plot([x, x], [0.10, 0.87], color='black', linestyle='--', lw=1.0)

    messages = [
        (0.10, 0.28, 0.78, "1. Launch Application"),
        (0.28, 0.46, 0.68, "2. Capture Video Frame (RGB)"),
        (0.46, 0.46, 0.58, "3. Detect Face Bounding Box"),
        (0.46, 0.64, 0.48, "4. Pass Preprocessed Crop (48x48x1)"),
        (0.64, 0.64, 0.38, "5. Compute Softmax Probabilities"),
        (0.64, 0.82, 0.28, "6. Update 10-Frame Deque Buffer"),
        (0.82, 0.10, 0.18, "7. Render Overlay Box & Emotion Text")
    ]
    
    for x1, x2, y, label in messages:
        if x1 == x2:
            ax.annotate('', xy=(x1 + 0.05, y - 0.03), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="->", color="black", lw=1.2, connectionstyle="arc3,rad=-0.5"))
            ax.text(x1 + 0.06, y - 0.015, label, fontsize=8, fontweight='bold', va='center')
        else:
            ax.annotate('', xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="->", color="black", lw=1.2))
            ax.text((x1 + x2)/2, y + 0.02, label, fontsize=8, fontweight='bold', ha='center')

    plt.xlim(0, 1.0)
    plt.ylim(0, 1.0)
    plt.tight_layout()
    plt.savefig("Report/figures/figure_sequence_diagram.png", dpi=300)
    plt.close()
    print("[OK] Generated figure_sequence_diagram.png")

if __name__ == "__main__":
    generate_dataset_distribution()
    generate_confusion_matrix_plot()
    generate_f1_score_chart()
    generate_use_case_diagram()
    generate_system_architecture_diagram()
    generate_sequence_diagram()
