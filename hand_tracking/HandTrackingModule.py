"""
HandTrackingModule - Detector de mano con MediaPipe
====================================================

Este modulo "envuelve" a MediaPipe para que detectar una mano sea tan facil como:

    detector = HandDetector()
    hands = detector.find_hands(img)       # lista de manos encontradas
    detector.draw_hand(img, hands[0])      # dibuja el esqueleto de la mano

Cada mano es una lista de 21 puntos (landmarks). Cada punto es (x, y, z):
    - x, y : posicion en pixeles dentro de la imagen
    - z    : profundidad aproximada (negativo = mas cerca de la camara),
             en la misma escala que x para poder calcular angulos en 3D

Numeracion de los 21 puntos (ver finger_points.png):
    0          = muneca
    1, 2, 3, 4 = pulgar   (4 es la punta)
    5, 6, 7, 8 = indice   (8 es la punta)
    9 ... 12   = medio
    13 ... 16  = anular
    17 ... 20  = menique

Basado en el HandTrackingModule de Computer Vision Zone (cvzone),
adaptado a la API nueva de MediaPipe (Tasks) para el taller de UBC.
"""

import os
import time
import urllib.request

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

# Pares de puntos que se unen con una linea para dibujar el "esqueleto" de la mano
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),            # pulgar
    (0, 5), (5, 6), (6, 7), (7, 8),            # indice
    (5, 9), (9, 10), (10, 11), (11, 12),       # medio
    (9, 13), (13, 14), (14, 15), (15, 16),     # anular
    (13, 17), (17, 18), (18, 19), (19, 20),    # menique
    (0, 17),                                   # base de la palma
]

# Modelo de inteligencia artificial que usa MediaPipe para encontrar la mano.
# Ya viene incluido en esta carpeta; si se borra, se descarga solo (necesita internet).
MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
             "hand_landmarker/float16/1/hand_landmarker.task")
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task")


class HandDetector:

    def __init__(self, max_hands=1, detection_con=0.7, tracking_con=0.7):
        """
        max_hands     : cuantas manos buscar como maximo en la imagen.
        detection_con : confianza minima (0 a 1) para decir "aqui hay una mano".
        tracking_con  : confianza minima (0 a 1) para seguir a la mano entre frames.
                        Valores mas altos = menos detecciones falsas, pero
                        puede "perder" la mano mas facil.
        """
        if not os.path.exists(MODEL_PATH):
            print("Descargando el modelo de MediaPipe (solo la primera vez)...")
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            print("Descarga completa.")

        # Leemos el modelo nosotros mismos y se lo pasamos a MediaPipe como bytes,
        # porque MediaPipe falla si la ruta tiene tildes o enes (ej: C:\Users\José)
        with open(MODEL_PATH, "rb") as f:
            model_bytes = f.read()

        options = vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_buffer=model_bytes),
            running_mode=vision.RunningMode.VIDEO,   # modo video: aprovecha el frame anterior
            num_hands=max_hands,
            min_hand_detection_confidence=detection_con,
            min_hand_presence_confidence=tracking_con,
            min_tracking_confidence=tracking_con,
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.last_timestamp_ms = -1

    def find_hands(self, img):
        """
        Busca manos en la imagen (formato BGR de OpenCV).
        Devuelve una lista de manos; cada mano es una lista de 21 puntos (x, y, z).
        Si no hay manos, devuelve una lista vacia [].
        """
        # OpenCV guarda los colores como BGR, pero MediaPipe los espera como RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)

        # En modo video, MediaPipe necesita saber en que instante (ms) se tomo
        # cada frame, y ese valor siempre debe ir aumentando
        timestamp_ms = max(int(time.monotonic() * 1000), self.last_timestamp_ms + 1)
        self.last_timestamp_ms = timestamp_ms
        result = self.detector.detect_for_video(mp_image, timestamp_ms)

        # MediaPipe entrega coordenadas normalizadas (0 a 1); las pasamos a pixeles
        h, w, _ = img.shape
        hands = []
        for hand_landmarks in result.hand_landmarks:
            points = [(int(lm.x * w), int(lm.y * h), lm.z * w) for lm in hand_landmarks]
            hands.append(points)
        return hands

    def draw_hand(self, img, hand, point_colors=None,
                  line_color=(255, 255, 255), default_point_color=(255, 0, 0)):
        """
        Dibuja el esqueleto de una mano sobre la imagen.
        point_colors (opcional): lista de 21 colores BGR, uno por punto, para
        pintar cada punto de un color distinto (por ejemplo segun cuanto se dobla
        el dedo). Si no se pasa, todos los puntos usan default_point_color.
        """
        for p1, p2 in HAND_CONNECTIONS:
            cv2.line(img, hand[p1][:2], hand[p2][:2], line_color, 3)

        for i, (x, y, _) in enumerate(hand):
            color = point_colors[i] if point_colors else default_point_color
            cv2.circle(img, (x, y), 7, color, cv2.FILLED)
