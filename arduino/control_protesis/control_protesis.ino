/*
 * PASO 3 - Control de la protesis (recibe ordenes de control_protesis.py)
 * =======================================================================
 * Taller "Del Gesto al Movimiento" - UTEC Biomechanics Club (UBC)
 *
 * El programa de Python envia por el cable USB una linea como esta:
 *     "pulgar,indice,grupo\n"      ejemplo: "0,85,100\n"
 * donde cada numero es el porcentaje de cierre del dedo:
 *     0 % = dedo abierto      100 % = dedo cerrado
 *
 * Este programa convierte cada porcentaje en un angulo de servo, usando los
 * angulos OPEN_ANGLE y CLOSED_ANGLE que encontraste con calibrar_servos.ino.
 *
 * Seguridad: si deja de llegar informacion por mas de TIMEOUT_MS (cerraste
 * Python o se desconecto el cable), la protesis se abre sola.
 *
 * IMPORTANTE: cierra el Monitor Serie antes de ejecutar control_protesis.py.
 * Solo un programa a la vez puede usar el puerto USB del Arduino.
 *
 * Conexiones (ver docs/ARMADO_Y_CONEXIONES.md):
 *   Servo pulgar -> pin 9   |  Servo indice -> pin 10  |  Servo grupo -> pin 11
 *   Cable rojo de los servos -> 5V del Arduino (fila + de la protoboard)
 *   Cable marron de los servos -> GND del Arduino (fila - de la protoboard)
 *   Haz las conexiones con el Arduino desconectado del USB.
 */

#include <Servo.h>

// ---------------------- CONFIGURACION (modifica aqui) ----------------------
const uint8_t SERVO_PINS[3] = {9, 10, 11};   // pulgar, indice, grupo

// Copia aqui los angulos que encontraste con calibrar_servos.ino.
// Si en tu protesis el servo gira al reves, basta con que OPEN sea mayor que CLOSED.
const int OPEN_ANGLE[3]   = {20, 20, 20};      // dedo totalmente abierto
const int CLOSED_ANGLE[3] = {160, 160, 160};   // dedo totalmente cerrado

const unsigned long TIMEOUT_MS = 1000;   // tiempo sin datos antes de abrir la mano
// ---------------------------------------------------------------------------

Servo servos[3];
char rxBuffer[24];          // aqui juntamos las letras que llegan hasta el '\n'
uint8_t rxLength = 0;
unsigned long lastMessageMs = 0;

// Mueve el servo i segun un porcentaje de cierre (0 a 100)
void setPercent(uint8_t i, int percent) {
  percent = constrain(percent, 0, 100);
  // map() es una regla de tres: 0 % -> OPEN_ANGLE, 100 % -> CLOSED_ANGLE
  int angle = map(percent, 0, 100, OPEN_ANGLE[i], CLOSED_ANGLE[i]);
  servos[i].write(angle);
}

void openHand() {
  for (uint8_t i = 0; i < 3; i++) setPercent(i, 0);
}

// Separa el texto "0,85,100" en sus 3 numeros y mueve cada servo
void processMessage(char* msg) {
  int values[3];
  uint8_t count = 0;
  char* part = strtok(msg, ",");          // strtok corta el texto en cada coma
  while (part != NULL && count < 3) {
    values[count++] = atoi(part);         // "85" -> 85
    part = strtok(NULL, ",");
  }
  if (count == 3) {                       // solo usamos mensajes completos
    for (uint8_t i = 0; i < 3; i++) setPercent(i, values[i]);
    lastMessageMs = millis();
  }
}

void setup() {
  Serial.begin(115200);   // misma velocidad que BAUD_RATE en control_protesis.py
  // Encendemos los servos de uno en uno: los 3 se alimentan del 5V del Arduino
  // (que viene del USB) y arrancar todos a la vez puede reiniciar el Arduino.
  for (uint8_t i = 0; i < 3; i++) {
    servos[i].write(OPEN_ANGLE[i]);    // fijamos el angulo ANTES de attach para que no salte a 90 grados
    servos[i].attach(SERVO_PINS[i]);
    delay(300);
  }
  openHand();
  lastMessageMs = millis();
}

void loop() {
  // 1) Leer lo que llega por el cable USB, letra por letra
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      rxBuffer[rxLength] = '\0';
      processMessage(rxBuffer);
      rxLength = 0;
    } else if (rxLength < sizeof(rxBuffer) - 1) {
      rxBuffer[rxLength++] = c;
    } else {
      rxLength = 0;   // mensaje demasiado largo (basura): lo descartamos
    }
  }

  // 2) Seguridad: si Python dejo de enviar datos, abrimos la mano
  if (millis() - lastMessageMs > TIMEOUT_MS) {
    openHand();
  }
}
