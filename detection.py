import os
import sys
import cv2
import yaml
import pickle
import logging.config
from tkinter import filedialog

from core.model_loader.face_detection.FaceDetModelLoader import FaceDetModelLoader
from core.model_handler.face_detection.FaceDetModelHandler import FaceDetModelHandler
from core.model_loader.face_alignment.FaceAlignModelLoader import FaceAlignModelLoader
from core.model_handler.face_alignment.FaceAlignModelHandler import FaceAlignModelHandler
from core.model_loader.face_recognition.FaceRecModelLoader import FaceRecModelLoader
from core.model_handler.face_recognition.FaceRecModelHandler import FaceRecModelHandler
from core.image_cropper.arcface_cropper.FaceRecImageCropper import FaceRecImageCropper

# configure logging
logging.config.fileConfig("config/logging.conf")
logger = logging.getLogger('api')

# load model configuration
with open('config/model_conf.yaml') as f:
    model_conf = yaml.safe_load(f)

# load all required models
def load_models():
    with open('config/app_conf.yaml') as f:
        app_conf = yaml.load(f, Loader=yaml.SafeLoader)

    device = app_conf['core']['device']

    model_path = 'models'
    scene = 'non-mask'
    try:
        face_det_loader = FaceDetModelLoader(model_path, 'face_detection', model_conf[scene]['face_detection'])
        face_det_model, face_det_cfg = face_det_loader.load_model()
        face_det_handler = FaceDetModelHandler(face_det_model, device, face_det_cfg)

        face_align_loader = FaceAlignModelLoader(model_path, 'face_alignment', model_conf[scene]['face_alignment'])
        face_align_model, face_align_cfg = face_align_loader.load_model()
        face_align_handler = FaceAlignModelHandler(face_align_model, device, face_align_cfg)

        face_rec_loader = FaceRecModelLoader(model_path, 'face_recognition', model_conf[scene]['face_recognition'])
        face_rec_model, face_rec_cfg = face_rec_loader.load_model()
        face_rec_handler = FaceRecModelHandler(face_rec_model, device, face_rec_cfg)
    except Exception as e:
        logger.error('Failed to load models:', exc_info=True)
        sys.exit(-1)

    return face_det_handler, face_align_handler, face_rec_handler

face_det_handler, face_align_handler, face_rec_handler = load_models()

# extract face feature from a frame
def extract_face_feature(image, face_det_handler, face_align_handler, face_rec_handler):
    dets = face_det_handler.inference_on_image(image)
    if len(dets) == 0:
        return None
    landmarks = face_align_handler.inference_on_image(image, dets[0])
    face_cropper = FaceRecImageCropper()
    cropped_face = face_cropper.crop_image_by_mat(image, landmarks.flatten().tolist())
    return face_rec_handler.inference_on_image(cropped_face)

# process capture to find best face and save feature
def detect_and_save_feature(cap, entity_name):
    with open('config/app_conf.yaml') as f:
        app_conf = yaml.load(f, Loader=yaml.SafeLoader)

    draw_boxes = app_conf['recognition']['draw_boxes']
    box_color = tuple(reversed(app_conf['recognition']['box_color']))
    box_thickness = app_conf['recognition']['box_thickness']
    show_score = app_conf['recognition']['show_score']
    show_best = app_conf['recognition']['show_best']
    font_scale = app_conf['recognition']['font_scale']
    font_color = tuple(reversed(app_conf['recognition']['font_color']))

    best_feature = None
    best_confidence = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        try:
            detections = face_det_handler.inference_on_image(frame)
        except Exception as e:
            logger.error('Face detection failed:', exc_info=True)
            sys.exit(-1)

        for box in detections:
            confidence = box[4]
            if confidence > best_confidence:
                feature = extract_face_feature(frame, face_det_handler, face_align_handler, face_rec_handler)
                if feature is not None:
                    best_feature = feature
                    best_confidence = confidence

        for box in detections:
            x1, y1, x2, y2, confidence = box
            box = list(map(int, [x1, y1, x2, y2]))
            conf_text = f"{confidence:.2f}"

            if draw_boxes:
                cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), box_color, box_thickness)

            if show_score:
                cv2.putText(frame, conf_text, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_color, 1)

            if show_best:
                max_conf_text = f"Max confidence: {best_confidence:.2f}"
                cv2.putText(frame, max_conf_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_color, 1)

        cv2.imshow("Detekcja Twarzy i Zapis Wzorca", frame)
        if cv2.waitKey(1) & 0xFF == 13: # enter
            break

    cap.release()
    cv2.destroyAllWindows()

    if best_feature is not None:
        logger.info(f"Saved face feature for: \"{entity_name}\" with confidence: {best_confidence:.4f}")
        os.makedirs('features', exist_ok=True)
        feature_path = 'stored_features.pkl'
        if os.path.exists(feature_path):
            with open(feature_path, 'rb') as f:
                all_features = pickle.load(f)
        else:
            all_features = {}

        all_features[entity_name] = best_feature
        with open(feature_path, 'wb') as f:
            pickle.dump(all_features, f)
    else:
        logger.warning("No face feature extracted.")

# camera input
def detect_camera(entity_name):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Failed to open camera.")
        return
    detect_and_save_feature(cap, entity_name)

# video input
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
    detect_and_save_feature(cap, entity_name)
