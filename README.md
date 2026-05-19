# 🐸 Ranita Saltarina — Tu mascota virtual de escritorio

![GitHub last commit](https://img.shields.io/badge/diversión-100%25-brightgreen)
![macOS](https://img.shields.io/badge/plataforma-macOS-lightgrey)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Estado](https://img.shields.io/badge/estado-saltando-yellow)

**¿Tu escritorio te parece demasiado serio?**  
Dale vida con una rana **traviesa** que salta por la pantalla y, de vez en cuando, atrapa tu cursor con una lengua larguísima… porque sí, porque puede.

---

## 🎯 ¿Qué hace la ranita?

- 🏃 **Salta aleatoriamente** por el escritorio con una animación fluida.
- 👅 **Ataca el cursor** con su lengua roja. Si te alcanza, esconde el cursor durante unos segundos (se lo come, literalmente).
- 🧠 **Inteligencia mínima**: solo piensa en saltar y cazar cursores; no responderá preguntas existenciales.

---

## 🖥️ Requisitos

- **Sistema operativo**: **macOS** (la ranita usa APIs de Quartz para ocultar el cursor; en otros sistemas se quedará sentada sin hacer travesuras).
- **Python 3.8 o superior**
- **Tkinter** (viene incluido en la mayoría de distribuciones de Python para macOS)

### Dependencia opcional (pero muy recomendable)

Para que la lengua haga efecto de verdad (esconder el cursor) necesitas:

pip3 install pyobjc-framework-Quartz
Sin este paquete la rana seguirá saltando y sacando la lengua, pero el cursor permanecerá visible aunque te haya “atrapado”. El programa te avisará en consola si falta.


### 🚀 Instalación
Clona este repositorio:

bash
git clone https://github.com/tuusuario/ranita-saltarina.git
cd ranita-saltarina
(Opcional) Instala la dependencia para la funcionalidad completa:

bash
pip3 install pyobjc-framework-Quartz
Ejecuta el programa:

bash
python3 ranita.py

### 🕹️ Cómo usarlo (y cómo escapar)
Al lanzar ranita.py la rana aparecerá en una posición aleatoria y empezará a saltar.

Para cerrarla tienes dos opciones:

Pulsa la tecla ESC.

O el atajo Cmd + Shift + Q (necesitas que la ventana invisible de la rana tenga el foco; haz clic sobre ella antes si no responde).

### ⚙️ Personalización
Todas las constantes al principio de ranita.py pueden modificarse para ajustar el comportamiento del bicho:

Variable	Descripción	Valor por defecto
JUMP_DELAY	Rango de segundos entre salto y salto.	(0.5, 1.5)
TONGUE_ATTACK_DIST	Distancia máxima (píxeles) a la que la rana lanza la lengua.	200
TONGUE_ATTACK_PROB	Probabilidad (0 a 1) de que decida atacar en cada comprobación.	0.1 (10 %)
EAT_HIDE_DURATION	Tiempo (segundos) que el cursor permanece oculto si es atrapado.	3
Si quieres una rana más agresiva, sube TONGUE_ATTACK_PROB y reduce JUMP_DELAY. Si prefieres una mascota pacífica que solo salte, baja TONGUE_ATTACK_PROB a 0.0.

### 🧪 ¿Cómo funciona por dentro?
Tkinter crea una ventana transparente, sin bordes y siempre encima (overrideredirect, topmost).

Un hilo secundario gestiona los saltos interpolando la posición para que el movimiento sea suave.

Otro hilo vigila constantemente la posición del cursor; si está cerca, puede lanzar la lengua con una animación en varios pasos.

Al “comerse” el cursor usa Quartz para ocultarlo a nivel de sistema (CGDisplayHideCursor), y lo restaura pasado un tiempo.

Toda la interfaz gráfica y la sincronización se mantienen ligeras para que la rana no consuma apenas recursos.

### ⚠️ Avisos importantes
En macOS moderno, el sistema podría pedir permisos de accesibilidad la primera vez que se intenta ocultar el cursor. Concédeselos si quieres la experiencia completa (la ranita te lo agradecerá con un croac).

La rana es inofensiva: no modifica archivos, no instala nada ni sobrevive a un reinicio. Cuando cierras la ventana, desaparece hasta la próxima ejecución.

### 🤝 Contribuciones
Este proyecto es un trabajo universitario, pero si se te ocurre alguna mejora divertida (¿una rana que “croa” con sonidos del sistema?, ¿más animaciones?) las pull requests son bienvenidas. Eso sí, mantén el espíritu gamberro.

### 📜 Licencia
MIT — porque hasta las ranitas traviesas merecen ser libres.

¡Que el croac te acompañe!
