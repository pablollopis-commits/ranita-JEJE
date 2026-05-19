#!/usr/bin/env python3
"""
Ranita Saltarina para macOS – Versión traviesa
- Ataca con la lengua más frecuentemente.
- Al saltar, abre iconos del escritorio con un doble clic.
- Persistencia mediante LaunchAgent.
- Cierra con ESC o Cmd+Shift+Q.
"""

import tkinter as tk
import random
import time
import threading
import os
import sys
import plistlib
import subprocess

# ========== DEPENDENCIAS OPCIONALES ==========
try:
    import Quartz
    HAS_QUARTZ = True
except ImportError:
    HAS_QUARTZ = False
    print("⚠️  Instala 'pyobjc-framework-Quartz' para ocultar el cursor y hacer clics:")
    print("    pip3 install pyobjc-framework-Quartz")
    print("    (el cursor no se ocultará ni hará clics por ahora)")

# ========== CONFIGURACIÓN ==========
FROG_SIZE = 80
JUMP_DELAY = (0.5, 1.5)               # segundos entre saltos normales
TONGUE_ATTACK_DIST = 200              # píxeles de alcance de la lengua
TONGUE_ATTACK_PROB = 0.1              # probabilidad por iteración (10 %)
TONGUE_CHECK_DELAY = 0.1              # segundos entre comprobaciones
TONGUE_STEPS = 15
EAT_HIDE_DURATION = 3                 # segundos sin cursor
CLICK_PROBABILITY = 0.4               # probabilidad de "abrir icono" tras un salto
CLICK_DELAY_MS = 150                  # milisegundos antes de hacer clic

# ========== FUNCIONES DE PERSISTENCIA ==========
def install_persistent():
    script_path = os.path.abspath(sys.argv[0])
    if sys.executable.endswith('.app/Contents/MacOS/python'):
        exec_target = sys.executable
        args = [script_path]
    else:
        exec_target = '/usr/bin/python3'
        args = [script_path]

    plist = {
        'Label': 'com.frogpet.daemon',
        'ProgramArguments': [exec_target] + args,
        'RunAtLoad': True,
        'KeepAlive': False,
        'StandardOutPath': '/tmp/frogpet.log',
        'StandardErrorPath': '/tmp/frogpet.err',
    }

    launch_agents_dir = os.path.expanduser('~/Library/LaunchAgents')
    os.makedirs(launch_agents_dir, exist_ok=True)
    plist_path = os.path.join(launch_agents_dir, 'com.frogpet.plist')

    with open(plist_path, 'wb') as f:
        plistlib.dump(plist, f)

    subprocess.call(['launchctl', 'unload', plist_path], stderr=subprocess.DEVNULL)
    subprocess.call(['launchctl', 'load', plist_path])
    print("✅ Persistencia instalada")

def remove_persistent():
    plist_path = os.path.expanduser('~/Library/LaunchAgents/com.frogpet.plist')
    if os.path.exists(plist_path):
        subprocess.call(['launchctl', 'unload', plist_path])
        os.remove(plist_path)
        print("🗑️  Persistencia eliminada")

# ========== DIBUJO DE LA RANA ==========
def draw_frog(canvas, offset_x, offset_y, tongue_end=None):
    canvas.delete("frog")
    x, y = offset_x, offset_y
    canvas.create_oval(x, y, x+FROG_SIZE, y+FROG_SIZE,
                       fill="#2e7d32", outline="#1b5e20", width=2, tags="frog")
    eye_r = 8
    canvas.create_oval(x+15, y+10, x+15+2*eye_r, y+10+2*eye_r,
                       fill="white", outline="black", tags="frog")
    canvas.create_oval(x+FROG_SIZE-15-2*eye_r, y+10, x+FROG_SIZE-15, y+10+2*eye_r,
                       fill="white", outline="black", tags="frog")
    pupil_r = 4
    canvas.create_oval(x+17, y+13, x+17+2*pupil_r, y+13+2*pupil_r,
                       fill="black", tags="frog")
    canvas.create_oval(x+FROG_SIZE-15-2*eye_r+2, y+13,
                       x+FROG_SIZE-15-2*eye_r+2+2*pupil_r, y+13+2*pupil_r,
                       fill="black", tags="frog")
    canvas.create_line(x+20, y+FROG_SIZE, x+10, y+FROG_SIZE+20,
                       fill="#1b5e20", width=3, tags="frog")
    canvas.create_line(x+FROG_SIZE-20, y+FROG_SIZE, x+FROG_SIZE-10, y+FROG_SIZE+20,
                       fill="#1b5e20", width=3, tags="frog")
    if tongue_end:
        tx, ty = tongue_end
        canvas.create_line(x+FROG_SIZE//2, y+FROG_SIZE, tx, ty,
                           fill="red", width=4, tags="frog")

# ========== CONTROL DEL CURSOR Y CLICS (macOS) ==========
def hide_cursor_mac():
    if HAS_QUARTZ:
        Quartz.CGDisplayHideCursor(Quartz.CGMainDisplayID())

def show_cursor_mac():
    if HAS_QUARTZ:
        Quartz.CGDisplayShowCursor(Quartz.CGMainDisplayID())

def click_at(x, y, double=True):
    """Simula un clic (o doble clic) en las coordenadas absolutas (x,y)."""
    if not HAS_QUARTZ:
        return
    # Mover el cursor (opcional, para que sea más vistoso)
    move = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventMouseMoved, (x, y), 0)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, move)

    # Primer clic
    down = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseDown, (x, y), 0)
    up = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseUp, (x, y), 0)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, down)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, up)

    if double:
        # Pequeña pausa entre clics (necesaria para que sea un doble clic real)
        time.sleep(0.05)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, down)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, up)

# ========== CLASE PRINCIPAL ==========
class FrogPet:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.wm_attributes('-transparent', True)
        self.root.configure(background='systemTransparent')

        self.root.geometry(f"{FROG_SIZE+20}x{FROG_SIZE+30}")
        self.canvas = tk.Canvas(self.root,
                                width=FROG_SIZE+20,
                                height=FROG_SIZE+30,
                                bg='systemTransparent',
                                highlightthickness=0)
        self.canvas.pack()

        self.x = random.randint(0, self.root.winfo_screenwidth()-FROG_SIZE)
        self.y = random.randint(0, self.root.winfo_screenheight()-FROG_SIZE-30)
        self.root.geometry(f"+{self.x}+{self.y}")

        self.tongue_active = False
        self.tongue_target = None
        self.cursor_hidden = False
        self.hide_timer = None
        self.jump_urgent = False      # Para forzar un salto inmediato tras un clic

        draw_frog(self.canvas, 5, 5)

        self.root.bind("<Escape>", lambda e: self.quit())
        self.root.bind("<Command-Shift-Q>", lambda e: self.quit())

        self.running = True
        threading.Thread(target=self.jump_loop, daemon=True).start()
        threading.Thread(target=self.tongue_loop, daemon=True).start()

        install_persistent()

    # ---------- Movimiento (saltos) ----------
    def jump_loop(self):
        while self.running:
            new_x = random.randint(0, self.root.winfo_screenwidth()-FROG_SIZE)
            new_y = random.randint(0, self.root.winfo_screenheight()-FROG_SIZE-30)
            steps = 10
            for i in range(1, steps+1):
                if not self.running: break
                interp_x = self.x + (new_x - self.x)*i/steps
                interp_y = self.y + (new_y - self.y)*i/steps
                self.root.geometry(f"+{int(interp_x)}+{int(interp_y)}")
                time.sleep(0.02)
            self.x, self.y = new_x, new_y

            # Después de aterrizar, ¿hacemos un clic (abrir icono)?
            if not self.tongue_active and random.random() < CLICK_PROBABILITY:
                self.do_icon_click()
                # Forzar un salto casi inmediato (sin la pausa larga)
                continue  # vuelve al inicio del while, elige nueva posición y salta

            # Pausa normal entre saltos (solo si no hubo clic)
            time.sleep(random.uniform(*JUMP_DELAY))

    def do_icon_click(self):
        """Guarda las coordenadas actuales, esconde la rana y programa un doble clic allí."""
        click_x = self.x + FROG_SIZE//2
        click_y = self.y + FROG_SIZE  # boca de la rana

        # Teletransportar la rana fuera de pantalla para no interferir
        self.x, self.y = -200, -200
        self.root.geometry(f"+{self.x}+{self.y}")

        # Programar el doble clic después de CLICK_DELAY_MS ms
        self.root.after(CLICK_DELAY_MS, lambda: click_at(click_x, click_y, double=True))

        # Pequeña pausa para que el clic ocurra antes del próximo salto
        time.sleep(0.25)

    # ---------- Ataque con lengua ----------
    def tongue_loop(self):
        while self.running:
            if not self.tongue_active:
                cursor_x = self.root.winfo_pointerx()
                cursor_y = self.root.winfo_pointery()
                frog_center_x = self.x + FROG_SIZE//2
                frog_center_y = self.y + FROG_SIZE
                dist = ((cursor_x-frog_center_x)**2 + (cursor_y-frog_center_y)**2)**0.5
                if dist < TONGUE_ATTACK_DIST and random.random() < TONGUE_ATTACK_PROB:
                    self.tongue_active = True
                    self.tongue_target = (cursor_x, cursor_y)
                    self.animate_tongue()
            time.sleep(TONGUE_CHECK_DELAY)

    def animate_tongue(self):
        if not self.tongue_active:
            return
        mouth_x = self.x + FROG_SIZE//2
        mouth_y = self.y + FROG_SIZE
        target_x, target_y = self.tongue_target
        # Extender
        for i in range(TONGUE_STEPS):
            if not self.tongue_active: break
            t = i / TONGUE_STEPS
            tx = mouth_x + (target_x - mouth_x) * t
            ty = mouth_y + (target_y - mouth_y) * t
            draw_frog(self.canvas, 5, 5,
                      tongue_end=(tx-self.x+5, ty-self.y+5))
            self.root.update_idletasks()
            time.sleep(0.01)
        # ¿Atrapó?
        cursor_now = (self.root.winfo_pointerx(), self.root.winfo_pointery())
        if abs(cursor_now[0]-target_x) < 15 and abs(cursor_now[1]-target_y) < 15:
            self.eat_cursor()
        # Retraer
        for i in range(TONGUE_STEPS, -1, -1):
            if not self.tongue_active: break
            t = i / TONGUE_STEPS
            tx = mouth_x + (target_x - mouth_x) * t
            ty = mouth_y + (target_y - mouth_y) * t
            draw_frog(self.canvas, 5, 5,
                      tongue_end=(tx-self.x+5, ty-self.y+5))
            self.root.update_idletasks()
            time.sleep(0.01)
        draw_frog(self.canvas, 5, 5)
        self.tongue_active = False

    def eat_cursor(self):
        if not self.cursor_hidden:
            hide_cursor_mac()
            self.cursor_hidden = True
            if self.hide_timer:
                self.root.after_cancel(self.hide_timer)
            self.hide_timer = self.root.after(EAT_HIDE_DURATION*1000, self.restore_cursor)

    def restore_cursor(self):
        if self.cursor_hidden:
            show_cursor_mac()
            self.cursor_hidden = False

    def quit(self):
        self.running = False
        self.restore_cursor()
        self.root.destroy()
        # Opcional: desinstalar persistencia al cerrar
        # remove_persistent()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    pet = FrogPet()
    pet.run()