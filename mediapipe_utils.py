import cv2
import mediapipe as mp

mp_face = mp.solutions.face_detection

face_detector = mp_face.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.5
)

def extract_face(frame):
    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_detector.process(rgb)

    if not results.detections:
        return None

    detection = results.detections[0]
    bbox = detection.location_data.relative_bounding_box

    x = int(bbox.xmin * w)
    y = int(bbox.ymin * h)
    bw = int(bbox.width * w)
    bh = int(bbox.height * h)

    x, y = max(0, x), max(0, y)

    face = frame[y:y+bh, x:x+bw]

    if face.size == 0:
        return None

    face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    face = cv2.resize(face, (48, 48))

    return face