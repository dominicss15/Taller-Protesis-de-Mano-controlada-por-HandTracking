# Instalación (hacer ANTES del taller)

Calcula unos 30–40 minutos. Hazlo con tiempo: en el taller no habrá tiempo para
instalar todo desde cero y la red puede estar lenta.

Necesitas una laptop con **webcam** (la integrada sirve) y **cargador**.

## 1. Python 3.11

1. Descárgalo de <https://www.python.org/downloads/> (busca la versión **3.11.x**).
   MediaPipe no funciona con todas las versiones: con 3.13 o superior puede fallar.
2. **Windows:** en la primera pantalla del instalador marca
   **"Add python.exe to PATH"** y luego *Install Now*.
3. Comprueba en una terminal (PowerShell o CMD):
   ```
   python --version
   ```
   Debe decir `Python 3.11.x`.

> **Mac:** usa el instalador de python.org y escribe `python3` donde esta guía dice `python`.

## 2. Visual Studio Code

1. Descárgalo de <https://code.visualstudio.com/>.
2. Ábrelo, ve a **Extensiones** (`Ctrl+Shift+X`) e instala **Python** (de Microsoft).

## 3. Git

1. Descárgalo de <https://git-scm.com/downloads>. Instálalo con las opciones por defecto (todo *Next*).
2. Abre una terminal **nueva** y configura tu nombre y correo (los mismos de GitHub):
   ```
   git config --global user.name "Tu Nombre"
   git config --global user.email "tucorreo@ejemplo.com"
   ```

## 4. Cuenta de GitHub

Créala en <https://github.com/signup> si aún no tienes una.

## 5. Arduino IDE

1. Descarga **Arduino IDE 2** de <https://www.arduino.cc/en/software>.
2. Si tu Arduino es un clon (dice *CH340* en el chip USB), instala también el driver
   CH340: <https://www.wch-ic.com/downloads/CH341SER_EXE.html>.

## 6. Verificación final

Sigue los pasos 1 y 2 de [GITHUB.md](GITHUB.md) (fork y clonar). Luego, en la
terminal de VS Code (`Ctrl+ñ` o *Terminal > New Terminal*):

```
python -m pip install -r requirements.txt
python check_setup.py
```

Si al final aparece **`TODO LISTO`**, ya estás preparado. Si aparece algún `[X]`,
el mismo mensaje te dice cómo arreglarlo. Si no lo logras, escríbenos antes del
taller.
