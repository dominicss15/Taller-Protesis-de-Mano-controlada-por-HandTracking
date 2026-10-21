"""
PASO 3 - Control de la protesis de mano con Hand Tracking
=========================================================
Taller "Del Gesto al Movimiento" - UTEC Biomechanics Club (UBC) - Bioweek

Que hace este programa, paso a paso:
    1. La camara captura tu mano y MediaPipe ubica sus 21 puntos.
    2. Con esos puntos calculamos el ANGULO de flexion de cada dedo.
    3. Convertimos ese angulo en un PORCENTAJE de cierre:
           0 %  = dedo totalmente estirado
           100 % = dedo totalmente doblado
    4. Enviamos 3 porcentajes al Arduino por el cable USB (puerto serial):
           pulgar, indice y grupo (medio + anular + menique, que se mueven juntos)
    5. El Arduino convierte cada porcentaje en un angulo de servo y este tira
       del hilo de nylon que dobla el dedo de la protesis.

Mensaje que viaja por el cable USB (una linea por envio):
    "pulgar,indice,grupo\n"      ejemplo:  "0,85,100\n"

Si no hay un Arduino conectado, el programa funciona igual en MODO SIMULACION
(solo muestra los valores en pantalla), asi puedes probar la parte de vision.

Teclas:  q -> salir (la protesis vuelve a abrirse)
"""

import math
import time

import cv2
import serial
import serial.tools.list_ports

from hand_tracking.HandTrackingModule import HandDetector

# ===========================================================================
# CONFIGURACION - estos son los valores que puedes modificar
# ===========================================================================
CAM_INDEX = 0          # 0 = camara de la laptop; 1, 2... = camaras USB externas
SERIAL_PORT = None     # None = buscar el Arduino automaticamente. O escribelo: "COM5"
BAUD_RATE = 115200     # velocidad de comunicacion; debe ser igual a la del Arduino

# Angulos de tu dedo real (en grados) que corresponden a "abierto" y "cerrado".
# Mira el angulo que aparece en pantalla con la mano abierta y luego con el puno
# cerrado, y anota esos numeros aqui para que la protesis use todo su recorrido.
FINGER_RANGES = {
    #           abierto  cerrado
    "pulgar": (165,     120),
    "indice": (170,      60),
    "grupo":  (170,      60),
}

SMOOTHING = 0.4        # 0 a 1. Mas bajo = movimiento mas suave pero con mas retraso
SEND_INTERVAL_S = 0.03 # cada cuanto enviamos datos al Arduino (0.03 s = ~33 veces/seg)
RELAX_AFTER_S = 2.0    # si no se ve la mano por este tiempo, la protesis se abre
                       # (evita que los servos se queden forzando)

# ===========================================================================
# Puntos de la mano que usamos para medir cada dedo (ver finger_points.png)
# Para cada dedo medimos el angulo en la articulacion del medio ("pip"),
# formado por la base del dedo ("mcp"), la articulacion y la punta ("tip").
# ===========================================================================
FINGER_JOINTS = {
    #          mcp  pip  tip
    "pulgar":  (2,   3,   4),
    "indice":  (5,   6,   8),
    "medio":   (9,  10,  12),
    "anular":  (13, 14,  16),
    "menique": (17, 18,  20),
}

# Que puntos de la mano pertenecen a cada canal (para colorearlos en pantalla)
CHANNEL_POINTS = {
    "pulgar": [1, 2, 3, 4],
    "indice": [5, 6, 7, 8],
    "grupo":  [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
}

# Colores en formato BGR (azul, verde, rojo), que es el que usa OpenCV
BLUE = (255, 0, 0)
MAGENTA = (255, 0, 255)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
GRAY = (80, 80, 80)


# ---------------------------------------------------------------------------
# Geometria: de puntos de la mano a porcentaje de cierre
# ---------------------------------------------------------------------------
def angle_at(p_a, p_joint, p_b):
    """
    Angulo (en grados) que se forma en p_joint entre las rectas que van
    hacia p_a y hacia p_b. Usa x, y, z, asi funciona aunque la mano este
    un poco girada respecto a la camara.
        180 grados = dedo recto      ~60 grados = dedo muy doblado
    """
    v1 = [a - j for a, j in zip(p_a, p_joint)]
    v2 = [b - j for b, j in zip(p_b, p_joint)]
    len1 = math.sqrt(sum(c * c for c in v1))
    len2 = math.sqrt(sum(c * c for c in v2))
    if len1 == 0 or len2 == 0:
        return 180.0
    # Producto punto: cos(angulo) = (v1 . v2) / (|v1| * |v2|)
    cos_angle = sum(c1 * c2 for c1, c2 in zip(v1, v2)) / (len1 * len2)
    cos_angle = max(-1.0, min(1.0, cos_angle))   # evita errores por redondeo
    return math.degrees(math.acos(cos_angle))


def finger_angle(hand, finger):
    mcp, pip, tip = FINGER_JOINTS[finger]
    return angle_at(hand[mcp], hand[pip], hand[tip])


def angle_to_percent(angle, open_angle, closed_angle):
    """Regla de tres: convierte el angulo del dedo en 0-100 % de cierre."""
    percent = (open_angle - angle) / (open_angle - closed_angle) * 100
    return max(0.0, min(100.0, percent))   # lo limitamos entre 0 y 100


def blend_color(color_a, color_b, t):
    """Mezcla dos colores: t=0 -> color_a, t=1 -> color_b."""
    return tuple(int(a + (b - a) * t) for a, b in zip(color_a, color_b))


# ---------------------------------------------------------------------------
# Comunicacion con el Arduino
# ---------------------------------------------------------------------------
def find_arduino_port():
    """Busca entre los puertos USB uno que parezca un Arduino (original o clon)."""
    for port in serial.tools.list_ports.comports():
        desc = port.description or ""
        if any(name in desc for name in ("Arduino", "CH340", "USB Serial", "USB-SERIAL")):
            return port.device
    return None


def connect_arduino():
    port = SERIAL_PORT or find_arduino_port()
    if not port:
        print("No se encontro el Arduino -> MODO SIMULACION (solo pantalla).")
        return None
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=0)
        time.sleep(2)   # al abrir el puerto el Arduino se reinicia; esperamos a que arranque
        print(f"Conectado al Arduino en {port}")
        return ser
    except serial.SerialException as e:
        print(f"No se pudo abrir {port}: {e}")
        print("Tip: cierra el Monitor Serie del Arduino IDE, solo un programa puede usar el puerto.")
        print("-> MODO SIMULACION (solo pantalla).")
        return None


# ---------------------------------------------------------------------------
# Dibujo en pantalla
# ---------------------------------------------------------------------------
def draw_bars(img, percents, angles):
    """Dibuja una barra por canal con su porcentaje de cierre y el angulo medido."""
    x0 = img.shape[1] - 260
    for row, channel in enumerate(("pulgar", "indice", "grupo")):
        y = 40 + row * 50
        percent = percents[channel]
        cv2.putText(img, channel.upper(), (x0, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 2)
        cv2.rectangle(img, (x0, y + 8), (x0 + 200, y + 28), GRAY, cv2.FILLED)
        cv2.rectangle(img, (x0, y + 8), (x0 + int(2 * percent), y + 28),
                      blend_color(BLUE, MAGENTA, percent / 100), cv2.FILLED)
        cv2.putText(img, f"{percent:3.0f}%  ({angles[channel]:.0f} grados)",
                    (x0 + 90, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, WHITE, 1)


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
def main():
    ser = connect_arduino()

    cap = cv2.VideoCapture(CAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    if not cap.isOpened():
        print(f"No se pudo abrir la camara {CAM_INDEX}. Prueba con otro CAM_INDEX.")
        return

    detector = HandDetector(max_hands=1)

    # Porcentaje actual (ya suavizado) de cada canal; empezamos con la mano abierta
    percents = {"pulgar": 0.0, "indice": 0.0, "grupo": 0.0}
    angles = {"pulgar": 0.0, "indice": 0.0, "grupo": 0.0}
    last_hand_time = time.time()
    last_send_time = 0.0

    try:
        while True:
            success, img = cap.read()
            if not success:
                print("No llegan imagenes de la camara.")
                break
            img = cv2.flip(img, 1)   # modo espejo

            hands = detector.find_hands(img)

            if hands:
                hand = hands[0]
                last_hand_time = time.time()

                # 1) Angulo de cada canal. El "grupo" es el promedio de 3 dedos.
                angles["pulgar"] = finger_angle(hand, "pulgar")
                angles["indice"] = finger_angle(hand, "indice")
                angles["grupo"] = (finger_angle(hand, "medio")
                                   + finger_angle(hand, "anular")
                                   + finger_angle(hand, "menique")) / 3

                # 2) Angulo -> porcentaje, y suavizado para que el servo no tiemble.
                #    Suavizado exponencial: nuevo = viejo + SMOOTHING * (medido - viejo)
                for channel, (open_angle, closed_angle) in FINGER_RANGES.items():
                    measured = angle_to_percent(angles[channel], open_angle, closed_angle)
                    percents[channel] += SMOOTHING * (measured - percents[channel])

                # 3) Colorear cada dedo segun cuanto esta cerrado (azul -> magenta)
                point_colors = [GREEN] * 21   # la muneca (punto 0) queda en verde
                for channel, points in CHANNEL_POINTS.items():
                    color = blend_color(BLUE, MAGENTA, percents[channel] / 100)
                    for p in points:
                        point_colors[p] = color
                detector.draw_hand(img, hand, point_colors)

            elif time.time() - last_hand_time > RELAX_AFTER_S:
                # No vemos la mano hace rato: abrimos la protesis poco a poco
                for channel in percents:
                    percents[channel] *= 0.9

            # 4) Enviar los 3 porcentajes al Arduino, unas 33 veces por segundo
            command = f"{percents['pulgar']:.0f},{percents['indice']:.0f},{percents['grupo']:.0f}\n"
            if time.time() - last_send_time >= SEND_INTERVAL_S:
                if ser is not None:
                    ser.write(command.encode())
                last_send_time = time.time()

            draw_bars(img, percents, angles)
            status = "Arduino conectado" if ser is not None else "MODO SIMULACION"
            cv2.putText(img, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        GREEN if ser is not None else (0, 165, 255), 2)
            cv2.putText(img, f"Enviando: {command.strip()}", (10, img.shape[0] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 2)

            cv2.imshow("Control de Protesis - UBC", img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        # Pase lo que pase (salir con q, error, etc.) dejamos la protesis abierta
        if ser is not None:
            ser.write(b"0,0,0\n")
            ser.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
