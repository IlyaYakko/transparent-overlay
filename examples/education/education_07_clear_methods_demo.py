"""
education_07_clear_methods_demo.py
Demonstration of buffer and queue clearing methods

Shows:
- Difference between frame_clear(), frame_clear_queue() and frame_clear_buffers()
- Accumulation effects under different clearing strategies
- Visualization of front/back buffer behavior
- Practical usage of each clearing method
 - Two render queues (front_instances/back_instances) and how signal_render() swaps them
"""

import time
import math
from transparent_overlay import Overlay


def main():
    overlay = Overlay(width=800, height=600)
    overlay.start_layer()

    frame_count = 0
    x, y = 100, 100
    speed_x, speed_y = 3, 2

    # Three clearing modes
    clear_modes = [
        ("frame_clear() - full clear", "full"),
        ("frame_clear_queue() - queue only", "queue"),
        ("frame_clear_buffers('both') - both buffers only", "both buffers")
    ]
    current_mode = 0

    try:
        while True:
            frame_count += 1

            # Switch mode every 5 seconds
            if frame_count % 300 == 0:
                current_mode = (current_mode + 1) % len(clear_modes)
                print(f"Switching to: {clear_modes[current_mode][0]}")

            mode_name, mode_type = clear_modes[current_mode]

            # Apply selected clearing method
            if mode_type == "full":
                overlay.frame_clear()  # Full clear
            elif mode_type == "queue":
                overlay.frame_clear_queue()  # Queue only
            elif mode_type == "both buffers":
                overlay.frame_clear_buffers('both')  # Both buffers only

            # === STATIC OBJECTS (background) ===
            # Grid to visualize accumulation
            for i in range(0, 800, 50):
                overlay.draw_line(i, 0, i, 600, (50, 50, 50, 30), thickness=1)
            for i in range(0, 600, 50):
                overlay.draw_line(0, i, 800, i, (50, 50, 50, 30), thickness=1)

            # === INFO PANEL ===
            # Mode title
            overlay.draw_rect(5, 5, 790, 80, (0, 0, 0, 200))
            overlay.draw_text(400, 25, mode_name, (255, 255, 255, 255),
                              font_size=20, anchor='mm', highlight=True, bg_color=(0, 0, 0, 180))

            # Stats
            stats_text = f"Frame: {frame_count} | Objects: {overlay.get_object_count()} | FPS: {overlay.get_render_fps()}"
            overlay.draw_text(400, 55, stats_text, (255, 255, 255, 255),
                              font_size=16, anchor='mm', highlight=True, bg_color=(0, 0, 0, 180))

            # Color indicator for mode
            indicator_color = {
                "full": (0, 255, 0, 255),  # Green - full clear
                "queue": (255, 255, 0, 255),  # Yellow - queue only
                "both buffers": (255, 0, 0, 255)  # Red - both buffers only
            }[mode_type]

            overlay.draw_rect(750, 35, 30, 30, indicator_color)
            overlay.draw_text(765, 50, "●", (255, 255, 255, 255),
                              font_size=20, anchor='mm')

            # === DYNAMIC OBJECTS ===
            # Moving circle with frame number
            x += speed_x
            y += speed_y

            # Bounce off borders
            if x <= 30 or x >= 770:
                speed_x = -speed_x
            if y <= 30 or y >= 570:
                speed_y = -speed_y

            # Main circle
            overlay.draw_circle(x, y, 30, (255, 0, 0, 200))

            # Frame number on the circle
            overlay.draw_text(x, y, f'{frame_count}', (255, 255, 255, 255),
                              font_size=16, anchor='mm')

            # Rotating pointer line
            angle = frame_count * 5
            end_x = x + 40 * math.cos(math.radians(angle))
            end_y = y + 40 * math.sin(math.radians(angle))
            overlay.draw_line(int(x), int(y), int(end_x), int(end_y), (255, 255, 0, 255), thickness=2)

            overlay.signal_render()
            time.sleep(1 / 60)


    except KeyboardInterrupt:

        explanation = """
============================================================
DEMO FINISHED — CLEARING MODES EXPLAINED:
============================================================

1. frame_clear() — FULL CLEAR:
   • Clears the instance queue AND both buffers
   • Each frame is drawn from a clean slate
   • No accumulation, no flicker
   • FPS may be lower — everything is redrawn each frame

2. frame_clear_queue() — QUEUE ONLY:
   • Clears only the instance queue
   • back and front pixel buffers are NOT cleared → previous content accumulates
   • FPS does not drop — new instances are drawn on top of old ones
   • Heavy flicker — because the overlay uses TWO render queues:
     front_instances (rendered this frame) and back_instances (being filled now).
     signal_render() swaps these lists every call. If you do not enqueue new draw_* calls
     before the next signal_render(), the now-active front_instances may be empty, so even/odd
     frames alternate between "content" and "empty", which looks like flicker.

3. frame_clear_buffers('both') — BOTH BUFFERS ONLY:
   • Clears only both buffers
   • Instance queue is NOT cleared → objects duplicate
   • Object count grows → FPS DROPS
   • Possible flicker: alternating even/odd frames are visible for the same reason —
     swapping front/back instance lists without replenishing the queue every frame

Conclusion: Use frame_clear() in most cases.
Other methods are for special optimizations.
============================================================
"""

        print(explanation)

    finally:
        overlay.stop_layer()


if __name__ == "__main__":
    main()
