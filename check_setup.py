"""
PASO 0 - Verificar la instalacion
=================================

Ejecuta este archivo ANTES del taller. Revisa que tu laptop tenga todo lo
necesario: version de Python, librerias, camara y (opcional) el Arduino.

Al final debe decir "TODO LISTO". Si algo sale con [X], lee el mensaje:
ahi te dice como solucionarlo.
"""

import sys

ok = True


def report(passed, message, fix=""):
    """Imprime el resultado de una prueba y, si fallo, como arreglarla."""
    global ok
    print(f"  [{'OK' if passed else 'X '}] {message}")
    if not passed:
        ok = False
        if fix:
            print(f"       -> {fix}")


print("\nVerificando la instalacion para el taller de UBC...\n")

# 1) Version de Python (MediaPipe no funciona con todas las versiones)
v = sys.version_info
report(v[:2] in [(3, 10), (3, 11), (3, 12)],
       f"Python {v.major}.{v.minor}.{v.micro}",
       "Se recomienda Python 3.11. Revisa docs/INSTALACION.md")

# 2) Librerias de Python
try:
    import cv2
    report(True, f"OpenCV {cv2.__version__}")
except ImportError:
    cv2 = None
    report(False, "OpenCV no esta instalado", "Ejecuta: pip install -r requirements.txt")

try:
    import mediapipe
    report(True, f"MediaPipe {mediapipe.__version__}")
except ImportError:
    report(False, "MediaPipe no esta instalado", "Ejecuta: pip install -r requirements.txt")

try:
    import serial.tools.list_ports
    report(True, "PySerial instalado")
except ImportError:
    serial = None
    report(False, "PySerial no esta instalado", "Ejecuta: pip install -r requirements.txt")

# 3) Detector de mano (carga el modelo de MediaPipe)
try:
    from hand_tracking.HandTrackingModule import HandDetector
    HandDetector()
    report(True, "Detector de mano cargado")
except Exception as e:
    report(False, f"No se pudo cargar el detector de mano: {e}",
           "Ejecuta este archivo desde la carpeta principal del repositorio "
           "y revisa que exista hand_tracking/hand_landmarker.task")

# 4) Camara
if cv2 is not None:
    cap = cv2.VideoCapture(0)
    success, _ = cap.read() if cap.isOpened() else (False, None)
    cap.release()
    report(success, "Camara 0 funcionando",
           "Cierra Zoom/Meet/Teams, revisa los permisos de camara de Windows "
           "o prueba CAM_INDEX = 1")

# 5) Arduino (opcional: solo si ya lo tienes conectado)
if serial is not None:
    ports = list(serial.tools.list_ports.comports())
    arduino = [p for p in ports if any(n in (p.description or "")
               for n in ("Arduino", "CH340", "USB Serial", "USB-SERIAL"))]
    if arduino:
        print(f"  [OK] Arduino encontrado en {arduino[0].device}")
    else:
        print("  [--] Arduino no conectado (normal si aun no lo tienes; "
              "si es un clon, instala el driver CH340)")

print("\n" + ("TODO LISTO! Nos vemos en el taller." if ok
              else "Hay cosas por arreglar. Revisa los [X] de arriba."))
