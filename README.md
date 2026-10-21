# Del Gesto al Movimiento: Prótesis de Mano 3D controlada por Computer Vision

Taller de **UTEC Biomechanics Club (UBC)** en la **Bioweek** (IEEE EMBS UTEC).

Mueve tu mano frente a la cámara y mira cómo una prótesis impresa en 3D la imita
en tiempo real. La cámara de tu laptop ve tu mano, Python calcula cuánto doblas
cada dedo y se lo envía a un Arduino, que mueve 3 servomotores. Cada servo tira de
un hilo de nylon que hace de tendón.

```
 Cámara ──► Python (MediaPipe) ──► USB ──► Arduino ──► 3 servos ──► hilos de nylon ──► dedos
            "¿cuánto se dobla                "0,85,100"
             cada dedo?"
```

La prótesis tiene **3 grados de libertad**:

| Canal | Dedos | Pin del Arduino |
|-------|-------|-----------------|
| Pulgar | pulgar | 9 |
| Índice | índice | 10 |
| Grupo | medio + anular + meñique (se mueven juntos) | 11 |

## Estructura del proyecto

```
├── check_setup.py              PASO 0: verifica que tu laptop tiene todo instalado
├── hand_tracking/
│   ├── test_hand_tracking.py   PASO 1: prueba que la cámara detecta tu mano
│   ├── HandTrackingModule.py   Detector de mano (MediaPipe), lo usan los demás scripts
│   ├── hand_landmarker.task    Modelo de IA que encuentra la mano
│   └── finger_points.png       Mapa de los 21 puntos de la mano
├── arduino/
│   ├── calibrar_servos/        PASO 2: sketch para armar y calibrar los servos
│   └── control_protesis/       PASO 3: sketch que recibe las órdenes de Python
├── control_protesis.py         PASO 3: programa principal (cámara -> Arduino)
├── docs/
│   ├── INSTALACION.md          Qué instalar antes del taller
│   ├── GITHUB.md               Cómo obtener tu propia copia del código
│   └── ARMADO_Y_CONEXIONES.md  Armado de la prótesis, cableado y calibración
└── requirements.txt            Librerías de Python del proyecto
```

## Pasos del taller

**Antes del taller:** sigue [docs/INSTALACION.md](docs/INSTALACION.md).

1. **Obtén tu copia del código:** haz un *fork* y clónalo en VS Code ([docs/GITHUB.md](docs/GITHUB.md)).
2. **Instala las librerías** desde la terminal de VS Code:
   ```
   python -m pip install -r requirements.txt
   ```
3. **Paso 0:** ejecuta `check_setup.py`. Debe terminar en `TODO LISTO`.
4. **Paso 1:** ejecuta `hand_tracking/test_hand_tracking.py` y verifica que se dibujen los 21 puntos de tu mano.
5. **Paso 2:** arma la prótesis y calibra los servos con `arduino/calibrar_servos` ([docs/ARMADO_Y_CONEXIONES.md](docs/ARMADO_Y_CONEXIONES.md)).
6. **Paso 3:** sube `arduino/control_protesis` al Arduino, **cierra el Monitor Serie** y ejecuta `control_protesis.py`.
7. **Guarda tus cambios** en tu GitHub (commit + sync).

Para ejecutar un archivo `.py` en VS Code, ábrelo y presiona el botón ▶ (*Run Python File*)
arriba a la derecha.

## ¿Cómo funciona `control_protesis.py`?

1. **Detectar:** MediaPipe ubica los 21 puntos de la mano (ver `finger_points.png`).
2. **Medir:** para cada dedo calculamos el ángulo en su articulación media. Un dedo
   recto mide ~180° y uno doblado ~60°. Para el grupo usamos el promedio de medio,
   anular y meñique.
3. **Convertir:** con una regla de tres pasamos ese ángulo a un **porcentaje de
   cierre** (0 % = abierto, 100 % = cerrado), según `FINGER_RANGES`.
4. **Suavizar:** promediamos cada valor nuevo con el anterior (`SMOOTHING`) para que
   el servo no tiemble.
5. **Enviar:** mandamos `"pulgar,indice,grupo\n"` al Arduino unas 33 veces por segundo.
6. **Mover:** el Arduino convierte cada porcentaje en un ángulo de servo, entre
   `OPEN_ANGLE` y `CLOSED_ANGLE`.

Si no hay Arduino conectado, el programa corre en **modo simulación**: puedes probar
toda la parte de visión sin la prótesis.

## Ajustes que puedes hacer

| Dónde | Qué | Para qué |
|-------|-----|----------|
| `control_protesis.py` → `FINGER_RANGES` | ángulo abierto/cerrado de tu dedo real | que la prótesis use todo su recorrido con tu mano |
| `control_protesis.py` → `SMOOTHING` | 0 a 1 | más bajo = más suave, más alto = más rápido |
| `control_protesis.py` → `CAM_INDEX` / `SERIAL_PORT` | cámara y puerto | si usas cámara externa o el Arduino no se detecta solo |
| `control_protesis.ino` → `OPEN_ANGLE` / `CLOSED_ANGLE` | ángulos del servo | según el armado de tu prótesis (los obtienes en el Paso 2) |

## Problemas frecuentes

| Problema | Solución |
|----------|----------|
| `No module named cv2` / `mediapipe` | `python -m pip install -r requirements.txt` |
| La cámara no abre | Cierra Zoom/Meet/Teams. Prueba `CAM_INDEX = 1`. Revisa los permisos de cámara de Windows. |
| `MODO SIMULACION` con el Arduino conectado | Cierra el Monitor Serie del Arduino IDE. Si es un clon, instala el driver CH340. O escribe el puerto en `SERIAL_PORT = "COM5"`. |
| El Arduino se reinicia o se desconecta | Un servo está forzando y pide demasiada corriente: ajusta su `OPEN_ANGLE` / `CLOSED_ANGLE` unos grados hacia adentro. Conecta el Arduino directo a la laptop, sin hub USB. |
| Un servo se mueve al azar o no se mueve | Revisa que su cable marrón llegue a GND, el rojo a 5V y el naranja a su pin. |
| Un servo zumba y se calienta | Está forzando: ajusta su `OPEN_ANGLE` / `CLOSED_ANGLE` unos grados hacia adentro. |
| Un dedo no llega a cerrar o abrir del todo | Ajusta `FINGER_RANGES` mirando los grados que aparecen en pantalla. |
| Detecta la mano de otra persona | Solo debe haber una mano frente a la cámara. |

## Créditos

- **Talleristas:** Dominic Sisaya y Rodolfo Yauri, UTEC Biomechanics Club (UBC).
- **Evento:** Bioweek, organizado por IEEE EMBS UTEC.
- El detector de mano está basado en el *HandTrackingModule* de [Computer Vision Zone](https://www.computervision.zone/) y usa [MediaPipe](https://ai.google.dev/edge/mediapipe) de Google.

¿Te gustó? **UBC tiene su convocatoria de miembros abierta.** ¡Únete y sigue construyendo con nosotros!
