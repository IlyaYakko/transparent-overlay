"""
case_08_brightness_controller.py
Brightness & Night Light controller — simple screen dimmer

Demonstrates:
- Using a transparent overlay to dim and tint the screen
- Live UI controls with Tkinter (enable, brightness, warmth)
- Update-on-change rendering with ~30 FPS polling
- Clean overlay shutdown on exit
"""

import threading
import tkinter as tk
from tkinter import ttk
from typing import Optional

from transparent_overlay import Overlay


MAX_BRIGHTNESS_PERCENT = 80
BRIGHTNESS_DEFAULT = 0

MAX_WARMTH_PERCENT = 5
WARMTH_DEFAULT = 0


class BrightnessControllerApp:
    def __init__(self) -> None:
        self.overlay: Optional[Overlay] = None
        self.running = False

        # UI
        self.root = tk.Tk()
        self.root.title("Brightness & Night Light")
        self.root.geometry("280x220")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        # Variables
        self.enabled_var = tk.BooleanVar(value=True)
        self.brightness_var = tk.IntVar(value=min(BRIGHTNESS_DEFAULT, MAX_BRIGHTNESS_PERCENT))
        self.warmth_var = tk.IntVar(value=min(WARMTH_DEFAULT, MAX_WARMTH_PERCENT))

        # Build UI
        pad = {"padx": 10, "pady": 6}
        frm = ttk.Frame(self.root)
        frm.pack(fill='both', expand=True)

        ttk.Checkbutton(frm, text="Enable overlay", variable=self.enabled_var).pack(anchor='w', **pad)

        ttk.Label(frm, text=f"Brightness (0-{MAX_BRIGHTNESS_PERCENT}% dim)").pack(anchor="w", **pad)
        ttk.Scale(
            frm,
            from_=0,
            to=MAX_BRIGHTNESS_PERCENT,
            orient='horizontal',
            variable=self.brightness_var,
        ).pack(fill='x', **pad)

        ttk.Label(frm, text=f"Night light (0-{MAX_WARMTH_PERCENT}%)").pack(anchor="w", **pad)
        ttk.Scale(
            frm,
            from_=0,
            to=MAX_WARMTH_PERCENT,
            orient='horizontal',
            variable=self.warmth_var,
        ).pack(fill='x', **pad)

        btn_row = ttk.Frame(frm)
        btn_row.pack(fill='x', **pad)
        ttk.Button(btn_row, text="Minimize", command=self._minimize).pack(side='left')
        ttk.Button(btn_row, text="Exit", command=self._on_close).pack(side='right')

        # Traces (not needed when we render on state change in the tick loop)

        # Overlay
        self.overlay = Overlay()
        self.overlay.start_layer()
        self.running = True

        # Render state
        self._last_state = (-1, -1, None)  # brightness, warmth, enabled

        # Periodic tasks
        self.root.after(200, self._lift_self)
        self.root.after(33, self._tick)  # ~30 FPS check (renders only on change)

        # Close protocol
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # Direct IntVar usage is sufficient for ttk.Scale in supported Tk versions

    def _lift_self(self) -> None:
        # Keep controller above the overlay
        try:
            self.root.lift()
            self.root.attributes("-topmost", True)
        finally:
            if self.running:
                self.root.after(2000, self._lift_self)

    def _minimize(self) -> None:
        self.root.iconify()

    # No explicit dirty flag; state comparison is enough

    def _tick(self) -> None:
        if not self.running:
            return
        try:
            enabled = self.enabled_var.get()
            b = int(self.brightness_var.get())
            w = int(self.warmth_var.get())

            state = (b, w, enabled)
            if state != self._last_state:
                self._render_frame(enabled, b, w)
                self._last_state = state
        finally:
            # Schedule next check
            if self.running:
                self.root.after(33, self._tick)

    def _render_frame(self, enabled: bool, brightness: int, warmth: int) -> None:
        if not self.overlay:
            return

        # Clamp
        brightness = max(0, min(MAX_BRIGHTNESS_PERCENT, brightness))
        warmth = max(0, min(MAX_WARMTH_PERCENT, warmth))

        # Clear frame
        self.overlay.frame_clear()

        if enabled:
            a_dim = int(255 * (brightness / 100.0))
            a_warm = int(255 * (warmth / 100.0))

            if a_dim > 0:
                self.overlay.draw_rect(0, 0, self.overlay.width, self.overlay.height, (0, 0, 0, a_dim))
            if a_warm > 0:
                self.overlay.draw_rect(0, 0, self.overlay.width, self.overlay.height, (255, 120, 0, a_warm))

        # Present
        self.overlay.signal_render()

    def _on_close(self) -> None:
        if not self.running:
            return
        self.running = False

        def shutdown():
            try:
                if self.overlay:
                    # Clear overlay before stopping
                    try:
                        self.overlay.frame_clear()
                        self.overlay.signal_render()
                    except Exception:
                        pass
                    self.overlay.stop_layer()
            finally:
                try:
                    self.root.destroy()
                except Exception:
                    pass

        # Stop overlay on a thread to avoid blocking UI if Windows is slow
        threading.Thread(target=shutdown, daemon=True).start()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = BrightnessControllerApp()
    app.run()


if __name__ == "__main__":
    main()

