import os
import sys
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

with open('config/model_conf.yaml') as f:
    model_conf = yaml.load(f, Loader=yaml.SafeLoader)


# initialize models in pipeline
def load_models():
        model_path = 'models'
        scene = 'non-mask'
        try:
                face_det_loader = FaceDetModelLoader(model_path, 'face_detection', model_conf[scene]['face_detection'])
                face_det_model, face_det_cfg = face_det_loader.load_model()
                face_det_handler = FaceDetModelHandler(face_det_model, 'cuda:0', face_det_cfg)

                face_align_loader = FaceAlignModelLoader(model_path, 'face_alignment',
                                                         model_conf[scene]['face_alignment'])
                face_align_model, face_align_cfg = face_align_loader.load_model()
                face_align_handler = FaceAlignModelHandler(face_align_model, 'cuda:0', face_align_cfg)

                face_rec_loader = FaceRecModelLoader(model_path, 'face_recognition',
                                                     model_conf[scene]['face_recognition'])
                face_rec_model, face_rec_cfg = face_rec_loader.load_model()
                face_rec_handler = FaceRecModelHandler(face_rec_model, 'cuda:0', face_rec_cfg)
        except Exception as e:
                print(f'Error loading models: {e}')
                sys.exit(-1)
        return face_det_handler, face_align_handler, face_rec_handler

# get face feature from image
def extract_face_feature(image, face_det_handler, face_align_handler, face_rec_handler):
        dets = face_det_handler.inference_on_image(image)
        if len(dets) == 0:
                return None
        landmarks = face_align_handler.inference_on_image(image, dets[0])
        face_cropper = FaceRecImageCropper()
        cropped_face = face_cropper.crop_image_by_mat(image, landmarks.flatten().tolist())
        return face_rec_handler.inference_on_image(cropped_face)

# recognizing from saved pictures
def recognize(cap):
    face_det_handler, face_align_handler, face_rec_handler = load_models()

    collected_dir = './collected_images'
    stored_images = [os.path.join(collected_dir, f) for f in os.listdir(collected_dir) if f.endswith('.jpg')]
    stored_features = {}

    for img_path in stored_images:
        image = cv2.imread(img_path)
        feature = extract_face_feature(image, face_det_handler, face_align_handler, face_rec_handler)
        if feature is not None:
            stored_features[img_path] = feature

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        try:
            detections = face_det_handler.inference_on_image(frame)
            logger.info('Successful face detection!')
        except Exception as e:
            logger.error('Face detection failed:', exc_info=True)
            sys.exit(-1)

        for box in detections:
            box = list(map(int, box))
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)

        live_feature = extract_face_feature(frame, face_det_handler, face_align_handler, face_rec_handler)
        if live_feature is None:
            cv2.imshow('Rozpoznawanie Twarzy', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        best_match = None
        best_score = -1
        for img_path, feature in stored_features.items():
            score = np.dot(live_feature, feature)
            if score > best_score:
                best_score = score
                best_match = img_path

        if best_match:
            cv2.putText(frame, f'Match: {os.path.basename(best_match)[:-4]} ({best_score:.2f})',
                        (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        cv2.imshow('Rozpoznawanie Twarzy', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# pathway for camera
def recognize_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Failed to open camera.")
        return
    recognize(cap)

# pathway for video
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
