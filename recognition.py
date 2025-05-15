import os
import sys
import pickle
from tkinter import filedialog

sys.path.append('.')

import logging
mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)
import logging.config
logging.config.fileConfig("config/logging.conf")
logger = logging.getLogger('api')

import yaml
import cv2
import numpy as np

from core.model_loader.face_detection.FaceDetModelLoader import FaceDetModelLoader
from core.model_handler.face_detection.FaceDetModelHandler import FaceDetModelHandler
from core.model_loader.face_alignment.FaceAlignModelLoader import FaceAlignModelLoader
from core.model_handler.face_alignment.FaceAlignModelHandler import FaceAlignModelHandler
from core.image_cropper.arcface_cropper.FaceRecImageCropper import FaceRecImageCropper
from core.model_loader.face_recognition.FaceRecModelLoader import FaceRecModelLoader
from core.model_handler.face_recognition.FaceRecModelHandler import FaceRecModelHandler

# Load model configuration
with open('config/model_conf.yaml') as f:
    model_conf = yaml.load(f, Loader=yaml.SafeLoader)

# Initialize models in pipeline
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

        face_align_loader = FaceAlignModelLoader(model_path, 'face_alignment',
                                                 model_conf[scene]['face_alignment'])
        face_align_model, face_align_cfg = face_align_loader.load_model()
        face_align_handler = FaceAlignModelHandler(face_align_model, device, face_align_cfg)

        face_rec_loader = FaceRecModelLoader(model_path, 'face_recognition',
                                             model_conf[scene]['face_recognition'])
        face_rec_model, face_rec_cfg = face_rec_loader.load_model()
        face_rec_handler = FaceRecModelHandler(face_rec_model, device, face_rec_cfg)
    except Exception as e:
        print(f'Error loading models: {e}')
        sys.exit(-1)
    return face_det_handler, face_align_handler, face_rec_handler

# Globally loading models
face_det_handler, face_align_handler, face_rec_handler = load_models()

# Get face feature from image
def extract_face_feature(image, face_det_handler, face_align_handler, face_rec_handler):
    dets = face_det_handler.inference_on_image(image)
    if len(dets) == 0:
        return None
    landmarks = face_align_handler.inference_on_image(image, dets[0])
    face_cropper = FaceRecImageCropper()
    cropped_face = face_cropper.crop_image_by_mat(image, landmarks.flatten().tolist())
    return face_rec_handler.inference_on_image(cropped_face)


# Function to perform white balance correction
def correct_white_balance(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    a_mean, b_mean = cv2.mean(a)[0], cv2.mean(b)[0]
    a = cv2.subtract(a, (a_mean - 128))
    b = cv2.subtract(b, (b_mean - 128))

    lab_corrected = cv2.merge([l, a, b])
    corrected_image = cv2.cvtColor(lab_corrected, cv2.COLOR_LAB2BGR)

    return corrected_image

# Function to equalize hist using CLAHE
def equalize_hist(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    eq_l = clahe.apply(l)
    eq_lab_image = cv2.merge((eq_l, a, b))
    eq_image = cv2.cvtColor(eq_lab_image, cv2.COLOR_LAB2BGR)

    return eq_image

# Recognizing from precomputed features
def recognize(cap):
    with open('config/app_conf.yaml') as f:
        app_conf = yaml.load(f, Loader=yaml.SafeLoader)

    draw_boxes = app_conf['recognition']['draw_boxes']
    box_color = tuple(reversed(app_conf['recognition']['box_color']))
    box_thickness = app_conf['recognition']['box_thickness']
    show_score = app_conf['recognition']['show_score']
    show_best = app_conf['recognition']['show_best']
    font_scale = app_conf['recognition']['font_scale']
    font_color = tuple(reversed(app_conf['recognition']['font_color']))
    color_improvement = app_conf['core']['color_improvement']

    # Load precomputed features
    feature_path = './stored_features.pkl'
    if not os.path.exists(feature_path):
        logger.error("No stored features found. Run feature saving script first.")
        return

    with open(feature_path, 'rb') as f:
        stored_features = pickle.load(f)

    best_overall_match = None
    best_overall_score = -1

    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        if color_improvement:
            frame = correct_white_balance(frame)
            frame = equalize_hist(frame)

        try:
            detections = face_det_handler.inference_on_image(frame)
        except Exception as e:
            logger.error('Face detection failed:', exc_info=True)
            sys.exit(-1)

        face_cropper = FaceRecImageCropper()

        for box in detections:
            x1, y1, x2, y2, conf = list(map(int, box[:4])) + [box[4]]

            try:
                landmarks = face_align_handler.inference_on_image(frame, box)
                cropped_face = face_cropper.crop_image_by_mat(frame, landmarks.flatten().tolist())
                live_feature = face_rec_handler.inference_on_image(cropped_face)
            except Exception as e:
                logger.warning("Skipping face due to alignment or cropping failure.")
                continue

            best_match = None
            best_score = -1
            for name, feature in stored_features.items():
                score = np.dot(live_feature, feature)
                if score > best_score:
                    best_score = score
                    best_match = name

            if best_score > best_overall_score:
                best_overall_score = best_score
                best_overall_match = best_match
                logger.info(f"Updated best face recognition as: \"{best_overall_match}\" with certainty: {best_overall_score:.4f}")

            if draw_boxes:
                cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, box_thickness)

            if show_score and best_match:
                label = f"{best_match} ({best_score:.2f})"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            font_scale, font_color, 1)

        if best_overall_match and show_best:
            best_text = f"Best yet: {best_overall_match} ({best_overall_score:.2f})"
            cv2.putText(frame, best_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        font_scale, font_color, 1)

        cv2.imshow('Rozpoznawanie Twarzy', frame)
        if cv2.waitKey(1) & 0xFF == 13: # enter
            break

    cap.release()
    cv2.destroyAllWindows()

# camera input
def recognize_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Failed to open camera.")
        return
    recognize(cap)

# video input
def recognize_video():
    video_path = filedialog.askopenfilename(title="Wybierz plik wideo.",
                                            filetypes=[("Video Files", "*.mp4;*.avi;*.mkv")])
    if not video_path:
        logger.warning("No video file selected.")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error("Failed to open video file.")
        return
    recognize(cap)
