"""
education_06_dynamic_text_sizing.py
Dynamic Text Sizing and Management Demo

Demonstrates:
- Dynamic text rendering with automatic font size adjustment
- Real-time text updates with smooth animations
- Cache management for optimal performance
- Visual feedback for sprite bounds and rendering
- Memory-efficient text handling
"""

import time
import math
from transparent_overlay import Overlay


def main():
    """
    education_06_dynamic_text_sizing
    Demonstrates dynamic text: font size and text change every frame.
    Shows how to avoid cache growth: old sprite is removed via sprite_remove().
    """
    with Overlay() as overlay:
        # Helper from examples/test.py: draw cached sprite bounds at (x,y)
        def draw_bounds(sprite_id, x, y, color=(255, 255, 0, 100)):
            info = overlay.get_sprite_cache_info(sprite_id)
            if info:
                overlay.draw_rect(int(x), int(y), int(info['width']), int(info['height']), color, thickness=1)

        t0 = time.time()
        duration = 100
        frame = 0
        current_label_id = None

        # Prepare demo sprites (created once)
        circle_id = overlay.create_circle_sprite(50, (255, 0, 0, 128))
        rect_id = overlay.create_rect_sprite(100, 50, (0, 255, 0, 255))
        thickness_line = 20
        line_id = overlay.create_line_sprite(0, 0, -100, 500, (0, 0, 255, 255), thickness=thickness_line)
        static_text_id = overlay.create_text_sprite("Hello", font_size=20, color=(255, 255, 255))

        while time.time() - t0 < duration:
            overlay.frame_clear()

            # Dynamic text and font size
            stats_text, _ = overlay.get_render_statistics()
            stats_text += f'\nTotal Sprites: {len(overlay.sprite_cache)}'
            dynamic_font_size = 30 + int(10 * math.sin(frame * 0.05))

            # Remove previous sprite to avoid cache growth
            if current_label_id:
                overlay.sprite_remove(current_label_id)

            # Create a new text sprite
            current_label_id = overlay.create_text_sprite(
                stats_text,
                font_size=dynamic_font_size,
                color=(220, 220, 220, 255),
                highlight=True,
                bg_color=(0, 0, 0, 200),
            )

            # Get real size and draw a border
            info = overlay.get_sprite_cache_info(current_label_id) or {}
            w = info.get("width", 0)
            h = info.get("height", 0)
            x, y = 60, 40
            pad = 6
            if w and h:
                overlay.draw_rect(x - pad, y - pad, w + pad * 2, h + pad * 2,
                                  (120, 255, 120, 200), thickness=2)
                # Add informational text about size
                size_info = f"Sprite size: {w}×{h}px (font: {dynamic_font_size}pt)"
                overlay.draw_text(x-pad, y + h + pad, size_info,
                                  color=(150, 255, 150, 255), font_size=12,
                                  highlight=True, bg_color=(0, 0, 0, 120))

                # Place demo objects at static positions to the RIGHT, starting from x=500
                base_x = 500
                base_y = y

                # Circle (static)
                overlay.add_sprite_instance(circle_id, base_x, base_y)
                draw_bounds(circle_id, base_x, base_y)

                # Rectangle (static)
                rect_x = base_x
                rect_y = base_y + 130
                overlay.add_sprite_instance(rect_id, rect_x, rect_y)
                draw_bounds(rect_id, rect_x, rect_y)

                # Static text label
                text_x = base_x + 100
                text_y = base_y + 100
                overlay.add_sprite_instance(static_text_id, text_x, text_y)
                draw_bounds(static_text_id, text_x, text_y)

                # Line (static) with proper bbox alignment like in examples/test.py
                exp1_x, exp1_y = base_x + 300, base_y + 20
                x1, y1, x2, y2 = 0, 0, -100, 500
                half = thickness_line // 2
                left_bbox = min(x1, x2) - half
                top_bbox = min(y1, y2) - half
                sx = x1 - left_bbox
                sy = y1 - top_bbox
                inst_x = exp1_x - sx
                inst_y = exp1_y - sy
                overlay.add_sprite_instance(line_id, inst_x, inst_y)
                draw_bounds(line_id, inst_x, inst_y)
                # Green dot: expected start of the correctly placed line
                overlay.draw_circle(exp1_x, exp1_y, 3, (0, 255, 0, 255))

                # Second line instance (static) without alignment (intentionally misaligned)
                exp2_x, exp2_y = base_x + 400, base_y + 20
                overlay.add_sprite_instance(line_id, exp2_x, exp2_y)
                draw_bounds(line_id, exp2_x, exp2_y, color=(255, 0, 0, 100))
                # Red dot: where we expect line start (will not match without alignment)
                overlay.draw_circle(exp2_x, exp2_y, 3, (255, 0, 0, 255))

            # Caption and instruction
            overlay.draw_text(60, 12, "Dynamic text with cleanup (no cache growth)",
                              color=(255, 255, 255, 255), font_size=14)

            overlay.add_sprite_instance(current_label_id, x, y)
            overlay.signal_render()
            frame += 1
            time.sleep(1 / 60)


if __name__ == '__main__':
    main()