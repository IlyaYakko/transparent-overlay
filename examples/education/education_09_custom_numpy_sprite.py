"""
education_09_custom_numpy_sprite.py
Example of creating a custom sprite from a NumPy array and inspecting its properties.
"""

import time
import numpy as np
from transparent_overlay import Overlay


def main():
    with Overlay() as overlay:
        # Create an RGBA gradient (library converts to premultiplied BGRA internally)
        h, w = 120, 240
        arr = np.zeros((h, w, 4), dtype=np.uint8)
        for x in range(w):
            arr[:, x, 0] = int(255 * x / (w - 1))   # R
            arr[:, x, 1] = 64                       # G
            arr[:, x, 2] = 255 - arr[:, x, 0]       # B
            arr[:, x, 3] = 200                      # A

        key = ('custom', 'gradient_demo')
        overlay.create_sprite_from_numpy(arr, key)

        info = overlay.get_sprite_cache_info(key)
        if info:
            print(f"Sprite size: {info['width']}x{info['height']}, memory: {info['memory_bytes']} bytes")

        t0 = time.time()
        while time.time() - t0 < 4:
            overlay.frame_clear()
            overlay.add_sprite_instance(key, 100, 100)
            overlay.draw_text(100, 80, "Custom NumPy Sprite", color=(255, 255, 255), font_size=16)
            overlay.signal_render()
            time.sleep(1/60)


if __name__ == '__main__':
    main()
