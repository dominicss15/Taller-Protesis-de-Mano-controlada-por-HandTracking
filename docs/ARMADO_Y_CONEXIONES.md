# Armado, conexiones y calibración

## Materiales por grupo

- 1 mano impresa en 3D con 3 cartuchos para servos
- 3 servomotores MG90S
- Hilo de nylon
- 1 Arduino UNO con su cable USB
- 1 protoboard y jumpers

## Conexiones

> ⚠️ **Haz todas las conexiones con el Arduino desconectado del USB.** Revisa el
> cableado antes de conectarlo a la laptop.

Los 3 servos se alimentan del pin **5V** del Arduino, que toma la energía del USB de
tu laptop. Las filas **+** y **−** de la protoboard reparten ese 5V y el GND entre los
3 servos.

```
                                                 ARDUINO UNO
   fila + de la protoboard ────────────────────── 5V
   fila − de la protoboard ────────────────────── GND
     │   │   │       │   │   │
    rojo rojo rojo  marrón marrón marrón
     │   │   │       │   │   │
   [Servo pulgar] [Servo índice] [Servo grupo]
        naranja        naranja       naranja
           │              │             │
         pin 9         pin 10        pin 11  (del Arduino)
```

| Cable del servo | Va a |
|-----------------|------|
| Rojo (+) | fila **+** de la protoboard, que va al pin **5V** del Arduino |
| Marrón (−) | fila **−** de la protoboard, que va al pin **GND** del Arduino |
| Naranja (señal) | Pulgar → pin **9**, Índice → pin **10**, Grupo → pin **11** |

**Si el Arduino se reinicia o se desconecta de la laptop**, algún servo está pidiendo
demasiada corriente, casi siempre porque está forzando contra el dedo (zumba). Ajusta
sus ángulos unos grados hacia adentro y conecta el Arduino directo a la laptop, sin
hub USB.

## Armado y calibración (Paso 2)

1. **Sube el sketch de calibración.** Conecta el Arduino a la laptop con el cable USB,
   abre `arduino/calibrar_servos/calibrar_servos.ino` en el Arduino IDE, elige la placa
   **Arduino Uno** y su puerto (*Herramientas > Placa / Puerto*) y presiona **Subir** (→).
2. **Espera a que termine de subir.** Los 3 servos van, uno por uno, a la posición
   **ABIERTO** (20°).
3. **Fija cada servo** en su cartucho de la mano y coloca su brazo (horn), **sin
   moverlo** de esa posición.
4. **Amarra el hilo de nylon.** Con el dedo de la prótesis **totalmente estirado**,
   amarra el hilo al brazo del servo, **tenso y sin holgura**. Usa doble nudo y
   asegúralo con una gota de pegamento.
5. **Busca los límites.** Abre el **Monitor Serie** (115200 baudios, "Nueva línea") y
   mueve cada servo poco a poco:
   ```
   1 60      (pulgar a 60°)
   1 100
   1 130     ...hasta que el dedo quede cerrado
   ```
   - El ángulo en que el dedo queda totalmente cerrado es su `CLOSED_ANGLE`.
   - Si el servo **zumba y no avanza**, está forzando: retrocede unos grados.
   - Repite con el servo 2 (índice) y el 3 (grupo).
6. **Anota los ángulos** en `arduino/control_protesis/control_protesis.ino`:
   ```cpp
   const int OPEN_ANGLE[3]   = {20, 20, 20};     // pulgar, indice, grupo
   const int CLOSED_ANGLE[3] = {130, 150, 155};  // <- tus valores
   ```

## Control con la mano (Paso 3)

1. Sube `arduino/control_protesis/control_protesis.ino` al Arduino.
2. **Cierra el Monitor Serie.** Solo un programa puede usar el puerto USB.
3. En VS Code ejecuta `control_protesis.py`. Debe decir **"Arduino conectado"**.
4. Abre y cierra tu mano frente a la cámara. ¡La prótesis debe imitarte!
5. **Afina tu mano:** a la derecha de la pantalla se ven los grados de cada dedo.
   Anota los grados con la mano abierta y con el puño cerrado, y ponlos en
   `FINGER_RANGES` de `control_protesis.py`.

Al presionar `q` o cerrar el programa, la prótesis se abre sola. También se abre
si se desconecta el cable, porque el Arduino deja de recibir datos.
