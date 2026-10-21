"""
PASO 1 - Prueba de Hand Tracking
================================

Antes de conectar el Arduino, comprueba que tu laptop puede ver y seguir tu mano.

Que deberias ver:
    - Una ventana con la imagen de tu camara (en modo espejo).
    - Los 21 puntos de tu mano unidos por lineas, con su numero al lado.
    - Arriba a la izquierda, los FPS (frames por segundo). Con mas de 15 FPS
      el control de la protesis se sentira fluido.

Teclas:
    n  -> mostrar / ocultar los numeros de los puntos
    q  -> salir

Si la camara no abre, cambia CAM_INDEX a 1 (o 2) y vuelve a ejecutar.
"""

import time

import cv2

from HandTrackingModule import HandDetector

CAM_INDEX = 0   # 0 = camara integrada de la laptop; 1, 2... = camaras USB externas


def main():
    cap = cv2.VideoCapture(CAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    if not cap.isOpened():
        print(f"No se pudo abrir la camara {CAM_INDEX}. Prueba con otro CAM_INDEX.")
        return

    detector = HandDetector(max_hands=1)
    show_numbers = True
    prev_time = time.time()

    while True:
        success, img = cap.read()
        if not success:
            print("No llegan imagenes de la camara.")
            break

        # Volteamos la imagen horizontalmente para que funcione como un espejo
        img = cv2.flip(img, 1)

        hands = detector.find_hands(img)

        if hands:
            hand = hands[0]   # nos quedamos con la primera mano detectada
            detector.draw_hand(img, hand)

            if show_numbers:
                for i, (x, y, _) in enumerate(hand):
                    cv2.putText(img, str(i), (x + 8, y - 8),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            cv2.putText(img, "Mano detectada", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(img, "Muestra tu mano a la camara", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # FPS = cuantas imagenes procesamos por segundo
        now = time.time()
        fps = 1 / max(now - prev_time, 1e-6)
        prev_time = now
        cv2.putText(img, f"FPS: {fps:.0f}", (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

        cv2.imshow("Prueba de Hand Tracking - UBC", img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("n"):
            show_numbers = not show_numbers

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
