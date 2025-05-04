import os
import sys
import cv2
import yaml
import logging.config
import numpy as np
from tkinter import filedialog
from core.model_loader.face_detection.FaceDetModelLoader import FaceDetModelLoader
from core.model_handler.face_detection.FaceDetModelHandler import FaceDetModelHandler

# configure logging
logging.config.fileConfig("config/logging.conf")
logger = logging.getLogger('api')

# loads config
with open('config/model_conf.yaml') as f:
    model_conf = yaml.safe_load(f)

# loads the face detection model
def load_det_model():
    model_path = 'models'
    scene = 'non-mask'
    model_category = 'face_detection'
    model_name = model_conf[scene][model_category]

    print('Loading the face detection model...')
    try:
        model_loader = FaceDetModelLoader(model_path, model_category, model_name)
        model, cfg = model_loader.load_model()
        print('Model loaded successfully!')
        return FaceDetModelHandler(model, 'cuda:0', cfg)
    except Exception as e:
        logger.error('Failed to load model:', exc_info=True)
        sys.exit(-1)

# detects the faces on an image and saves when the detection score is the highest
def detect_and_save(cap, entity_name):
    with open('config/app_conf.yaml') as f:
        app_conf = yaml.load(f, Loader=yaml.SafeLoader)

    draw_boxes = app_conf['detection']['draw_boxes']
    box_color = tuple(app_conf['detection']['box_color'])
    box_thickness = app_conf['detection']['box_thickness']

    detection_handler = load_det_model()
    output_dir = 'collected_images'
    os.makedirs(output_dir, exist_ok=True)

    best_face = None
    best_confidence = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        try:
            detections = detection_handler.inference_on_image(frame)
        except Exception as e:
            logger.error('Face detection failed:', exc_info=True)
            sys.exit(-1)

        if draw_boxes:
            for box in detections:
                confidence = box[4]
                if confidence > best_confidence:
                    best_face = frame.copy()
                    best_confidence = confidence

                box = list(map(int, box))
                cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), box_color, box_thickness)

        cv2.imshow("Video", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    logger.info(f"Created template called: \"{entity_name}\" with face detection certainty: {best_confidence}.")
    if best_face is not None:
        cv2.imwrite(os.path.join(output_dir, f"{entity_name}.jpg"), best_face)

# pathway for camera
def detect_camera(entity_name):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Failed to open camera.")
        return
    detect_and_save(cap, entity_name)

# pathway for video
def detect_video(entity_name):
    video_path = filedialog.askopenfilename(title="Wybierz plik wideo.",
                                            filetypes=[("Video Files", "*.mp4;*.avi;*.mkv")])
    if not video_path:
        logger.warning("No video file selected.")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error("Failed to open video file.")
        return
    detect_and_save(cap, entity_name)
