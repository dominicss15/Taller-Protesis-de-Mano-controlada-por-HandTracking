# Git y GitHub: tu propia copia del código

- **Git** es un programa que guarda el historial de tu código, como un "Ctrl+Z" infinito.
  Cada punto guardado se llama **commit**.
- **GitHub** es una página web donde se guardan esos proyectos (**repositorios**) en
  la nube, para compartirlos y trabajar en equipo.

En el taller vas a hacer un **fork**: una copia del repositorio original en **tu
propia cuenta**. Puedes modificar tu copia todo lo que quieras sin afectar el
original, y te queda en tu GitHub para siempre.

```
 Repositorio original (UBC)  ──fork──►  Tu repositorio en GitHub  ◄──sync──►  Tu laptop (VS Code)
    (no se modifica)                     (tu copia en la nube)                (donde editas)
```

## 1. Hacer el fork (en el navegador)

1. Inicia sesión en <https://github.com>.
2. Entra al repositorio del taller (el link te lo damos en el taller).
3. Arriba a la derecha presiona **Fork** y luego **Create fork**.
4. Ahora tienes `https://github.com/TU_USUARIO/<nombre-del-repo>`. Esa es tu copia.

## 2. Clonar tu fork en VS Code (descargarlo a tu laptop)

1. Abre VS Code y presiona `Ctrl+Shift+P`.
2. Escribe **Git: Clone** y elige **Clone from GitHub**.
3. Si te lo pide, autoriza a VS Code a usar tu cuenta de GitHub.
4. Elige **tu** repositorio (`TU_USUARIO/...`, no el de UBC).
5. Elige una carpeta, por ejemplo `Documentos`, y presiona **Open** cuando aparezca.

## 3. Guardar tus cambios (commit) y subirlos (sync)

Cuando modifiques algo (por ejemplo `FINGER_RANGES` en `control_protesis.py`):

1. Abre el panel **Source Control** (`Ctrl+Shift+G`, el icono de ramitas). Ahí
   aparecen los archivos que cambiaste.
2. Escribe un mensaje que diga **qué** cambiaste, por ejemplo: `Calibro los rangos de mi mano`.
3. Presiona **Commit**. Si VS Code pregunta por *stage* los cambios, responde **Yes / Always**.
4. Presiona **Sync Changes** para subirlo a tu GitHub.

Recarga tu repositorio en el navegador: verás tu cambio y tu mensaje.

## Resumen

| Acción | Qué hace | Dónde |
|--------|----------|-------|
| **Fork** | Copia el repositorio a tu cuenta | GitHub (navegador) |
| **Clone** | Descarga tu copia a tu laptop | VS Code |
| **Commit** | Guarda un punto en el historial (solo en tu laptop) | VS Code |
| **Sync / Push** | Sube tus commits a GitHub | VS Code |

## Extra

- **¿Se actualizó el original?** En tu fork en GitHub presiona **Sync fork** y luego,
  en VS Code, **Sync Changes** para traer las novedades.
- **¿Quieres proponer tu mejora al repositorio original?** Eso se llama
  **Pull Request** (botón *Contribute* en tu fork). ¡Te animamos a intentarlo!
