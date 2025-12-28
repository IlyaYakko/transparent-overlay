"""
education_05_sprite_management
Short and clear demonstration of sprite management:
- Create several manual sprites (circle, rectangle, text)
- Reuse them via add_sprite_instance()
- Get real sprite size from cache with get_sprite_cache_info()

No console stats and no complex logic.
"""

import time
from transparent_overlay import Overlay
import math


def main():
    with Overlay() as overlay:
        # 1) Create a few sprites once
        circle_red = overlay.create_circle_sprite(24, (255, 80, 80, 200))
        rect_blue = overlay.create_rect_sprite(80, 40, (80, 140, 255, 180))

        t0 = time.time()
        duration = 5  # секунд
        frame = 0

        while time.time() - t0 < duration:
            overlay.frame_clear()

            # 2) Draw a grid of repeated circles (reuse)
            grid_left, grid_top = 60, 80
            cols, rows = 6, 3
            step_x, step_y = 40, 40
            for j in range(rows):
                for i in range(cols):
                    x = grid_left + i * step_x
                    y = grid_top + j * step_y
                    overlay.add_sprite_instance(circle_red, x, y)
            # 3) Dynamic rectangle placement (simple animation)
            base_x, base_y = 340, 140
            dx = int(10 * (1 + ((frame // 10) % 2) * -2))  # простое "туда-сюда"
            overlay.add_sprite_instance(rect_blue, base_x + dx, base_y)

            # 4) Static text sprite (created ONCE) + border with real size
            # Create at first frame and cache size info
            if frame == 0:
                label_text = "Sprite Cache: real size (static label)"
                label_key = overlay.create_text_sprite(
                    label_text,
                    font_size=18,
                    color=(200, 200, 200, 255),
                    highlight=True,
                    bg_color=(0, 0, 0, 120),
                )
                label_info = overlay.get_sprite_cache_info(label_key) or {}
                label_w = label_info.get("width", 0)
                label_h = label_info.get("height", 0)

            label_x, label_y = 500, 30
            pad = 6
            if label_w and label_h:
                overlay.draw_rect(
                    label_x - pad,
                    label_y - pad,
                    label_w + pad * 2,
                    label_h + pad * 2,
                    (120, 255, 120, 200),
                    thickness=2,
                )
            overlay.add_sprite_instance(label_key, label_x, label_y)

            # Labels
            overlay.draw_text(60, 60, "Manual sprites reused as instances",
                              color=(220, 220, 220, 255), font_size=14)
            overlay.draw_text(340, 120, "Animated rect (manual sprite)",
                              color=(220, 220, 220, 255), font_size=14)

            overlay.signal_render()
            frame += 1
            time.sleep(1/60)
        print(f'Objects in cache: {len(overlay.sprite_cache)}')


if __name__ == '__main__':
    main()
