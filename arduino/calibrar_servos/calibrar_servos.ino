/*
 * PASO 2 - Calibrar servos (usar DURANTE el armado de la protesis)
 * ================================================================
 * Taller "Del Gesto al Movimiento" - UTEC Biomechanics Club (UBC)
 *
 * Para que sirve:
 *   a) Al subir este programa, los 3 servos se van a la posicion "ABIERTO".
 *      Recien en esa posicion amarra el hilo de nylon al servo, con el dedo
 *      de la protesis completamente estirado y el hilo tenso (sin holgura).
 *   b) Luego, desde el Monitor Serie, mueve cada servo poco a poco para
 *      encontrar el angulo exacto en que su dedo queda ABIERTO y CERRADO.
 *      Anota esos angulos en OPEN_ANGLE y CLOSED_ANGLE de control_protesis.ino.
 *
 * Como usar el Monitor Serie:
 *   Herramientas > Monitor Serie, velocidad 115200, y "Nueva linea" (New Line).
 *   Escribe uno de estos comandos y presiona Enter:
 *     a        -> los 3 servos a ABIERTO
 *     c        -> los 3 servos a CERRADO
 *     1 90     -> servo 1 (pulgar) a 90 grados
 *     2 120    -> servo 2 (indice) a 120 grados
 *     3 45     -> servo 3 (grupo medio+anular+menique) a 45 grados
 *
 * CUIDADO: si el servo zumba y no avanza, esta forzando contra el dedo.
 * Retrocede unos grados: ese es su limite. Forzarlo lo calienta y rompe
 * sus engranajes o el hilo.
 *
 * Conexiones (ver docs/ARMADO_Y_CONEXIONES.md):
 *   Servo pulgar -> pin 9   |  Servo indice -> pin 10  |  Servo grupo -> pin 11
 *   Cable rojo de los servos -> 5V del Arduino (fila + de la protoboard)
 *   Cable marron de los servos -> GND del Arduino (fila - de la protoboard)
 *   Haz las conexiones con el Arduino desconectado del USB.
 */

#include <Servo.h>

const uint8_t SERVO_PINS[3] = {9, 10, 11};   // pulgar, indice, grupo
const char* NAMES[3] = {"pulgar", "indice", "grupo"};

// Angulos iniciales de prueba. Ajustalos con los comandos del Monitor Serie.
const int OPEN_ANGLE[3]   = {20, 20, 20};
const int CLOSED_ANGLE[3] = {160, 160, 160};

Servo servos[3];
char rxBuffer[16];      // aqui juntamos las letras que llegan hasta el Enter
uint8_t rxLength = 0;

void moveServo(uint8_t i, int angle) {
  angle = constrain(angle, 0, 180);   // un servo solo va de 0 a 180 grados
  servos[i].write(angle);
  Serial.print("Servo ");
  Serial.print(i + 1);
  Serial.print(" (");
  Serial.print(NAMES[i]);
  Serial.print(") -> ");
  Serial.println(angle);
}

void runCommand(char* cmd) {
  if (cmd[0] == 'a') {
    for (uint8_t i = 0; i < 3; i++) moveServo(i, OPEN_ANGLE[i]);
  } else if (cmd[0] == 'c') {
    for (uint8_t i = 0; i < 3; i++) moveServo(i, CLOSED_ANGLE[i]);
  } else if (cmd[0] >= '1' && cmd[0] <= '3' && cmd[1] == ' ') {
    uint8_t i = cmd[0] - '1';         // '1' -> 0, '2' -> 1, '3' -> 2
    moveServo(i, atoi(cmd + 2));      // atoi convierte el texto "120" en el numero 120
  } else {
    Serial.println("Comando no valido. Usa: a | c | <servo 1-3> <angulo 0-180>");
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("== Calibracion de servos - UBC ==");
  // Encendemos los servos de uno en uno: los 3 se alimentan del 5V del Arduino
  // (que viene del USB) y arrancar todos a la vez puede reiniciar el Arduino.
  for (uint8_t i = 0; i < 3; i++) {
    servos[i].write(OPEN_ANGLE[i]);    // fijamos el angulo ANTES de attach para que no salte a 90 grados
    servos[i].attach(SERVO_PINS[i]);
    moveServo(i, OPEN_ANGLE[i]);
    delay(300);
  }
  Serial.println("Servos en posicion ABIERTO. Ya puedes amarrar los hilos.");
  Serial.println("Comandos: a | c | <servo 1-3> <angulo 0-180>   ej: 2 120");
}

void loop() {
  // Leemos letra por letra; al llegar el Enter ('\n') ejecutamos el comando
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (rxLength > 0) {
        rxBuffer[rxLength] = '\0';        // marca el final del texto
        runCommand(rxBuffer);
        rxLength = 0;
      }
    } else if (rxLength < sizeof(rxBuffer) - 1) {
      rxBuffer[rxLength++] = c;
    }
  }
}
