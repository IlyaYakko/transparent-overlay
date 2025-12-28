"""
case_02_eye_break_timer.py
Eye break timer — animated banner

Demonstrates:
- Smooth show/hide animation
- Centered text blocks
- Sound notifications via winsound
- Practical utility example
"""

import transparent_overlay
import time
import winsound


def main():
    overlay = transparent_overlay.Overlay()
    overlay.start_layer()

    try:
        screen_w = overlay.width
        screen_h = overlay.height

        # Plaque parameters
        plaque_width = 350
        plaque_height = 100
        plaque_x = (screen_w - plaque_width) // 2
        plaque_y_start = -plaque_height
        plaque_y_end = 50
        bg_color = (52, 111, 238, 220)
        border_color = (255, 255, 255, 255)
        text_color = (255, 255, 255, 255)
        timer_duration = 15

        # Slide-in animation from the top
        y = plaque_y_start
        step = 5
        while y < plaque_y_end:
            overlay.frame_clear()
            overlay.draw_rect(plaque_x, y, plaque_width, plaque_height, bg_color)
            overlay.draw_rect(plaque_x, y, plaque_width, plaque_height, border_color, thickness=1)

            overlay.draw_text(
                plaque_x + 20, y + 20, "Rest your eyes for a few seconds",
                text_color, box_size=(plaque_width - 40, 40), align="center", valign="middle"
            )
            overlay.draw_text(
                plaque_x + 20, y + 70, f"Timer: {timer_duration} s",
                text_color, font_size=16, box_size=(plaque_width - 40, 30), align="center", valign="middle"
            )

            overlay.signal_render()
            time.sleep(0.02)
            y += step

        # Notification sound
        winsound.MessageBeep(winsound.MB_ICONASTERISK)

        # Rest countdown
        start_time = time.time()
        while time.time() - start_time < timer_duration:
            elapsed = int(time.time() - start_time)
            remaining = timer_duration - elapsed

            overlay.frame_clear()
            overlay.draw_rect(plaque_x, plaque_y_end, plaque_width, plaque_height, bg_color)
            overlay.draw_rect(plaque_x, plaque_y_end, plaque_width, plaque_height, border_color, thickness=1)

            overlay.draw_text(
                plaque_x + 20, plaque_y_end + 20, "Rest your eyes for a few seconds",
                text_color, box_size=(plaque_width - 40, 40), align="center", valign="middle"
            )
            overlay.draw_text(
                plaque_x + 20, plaque_y_end + 70, f"Timer: {remaining} s",
                text_color, font_size=16, box_size=(plaque_width - 40, 30), align="center", valign="middle"
            )

            overlay.signal_render()
            time.sleep(1)

        # Finish sound
        winsound.MessageBeep(winsound.MB_ICONASTERISK)

        # Slide-out animation
        y = plaque_y_end
        while y > plaque_y_start:
            overlay.frame_clear()
            overlay.draw_rect(plaque_x, y, plaque_width, plaque_height, bg_color)
            overlay.draw_rect(plaque_x, y, plaque_width, plaque_height, border_color, thickness=1)

            overlay.draw_text(
                plaque_x + 20, y + 20, "Rest your eyes for a few seconds",
                text_color, box_size=(plaque_width - 40, 40), align="center", valign="middle"
            )
            overlay.draw_text(
                plaque_x + 20, y + 70, "Timer: 0 s",
                text_color, font_size=16, box_size=(plaque_width - 40, 30), align="center", valign="middle"
            )

            overlay.signal_render()
            time.sleep(0.02)
            y -= step

        # Final clear
        overlay.frame_clear()
        overlay.signal_render()

    except KeyboardInterrupt:
        print("Timer interrupted")
    finally:
        overlay.stop_layer()


if __name__ == "__main__":
    main()