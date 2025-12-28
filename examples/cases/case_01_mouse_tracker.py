"""
case_01_mouse_tracker.py
Cursor tracker with a gradient trail

Demonstrates:
- Real-time mouse position tracking
- Gradient color changes of the trail
- Automatic fading of old points
- Mouse click handling without pygame
"""

import transparent_overlay
import time
import math
from win32api import GetCursorPos, GetAsyncKeyState
import winsound


class MouseTracker:
    def __init__(self):
        self.overlay = transparent_overlay.Overlay()
        self.overlay.start_layer()

        self.trail_points = []
        self.max_trail_length = 800
        self.start_time = time.time()
        self.last_mouse_pos = None

    def draw_info_panel(self, point_count, current_color):
        """Draws the information panel"""
        info_x, info_y = 20, 20
        info_width, info_height = 350, 120

        self.overlay.draw_rect(info_x, info_y, info_width, info_height, (20, 20, 40, 200))
        self.overlay.draw_rect(info_x, info_y, info_width, info_height, (80, 80, 120, 255), thickness=2)

        self.overlay.draw_text(info_x + 10, info_y + 15, "Mouse Trail — Demo",
                               color=(255, 255, 255, 255), font_size=16)
        self.overlay.draw_text(info_x + 10, info_y + 40, f"Points in trail: {point_count}",
                               color=(200, 200, 255, 255), font_size=14)
        self.overlay.draw_text(info_x + 10, info_y + 65, f"Current color: RGB{current_color[:3]}",
                               color=current_color, font_size=14)
        self.overlay.draw_text(info_x + 10, info_y + 90, "ESC - exit, RMB - clear",
                               color=(150, 150, 150, 255), font_size=12)

    def is_right_click(self):
        """Checks if the right mouse button is pressed"""
        return GetAsyncKeyState(0x02) != 0

    def is_escape_pressed(self):
        """Checks if the ESC key is pressed"""
        return GetAsyncKeyState(0x1B) != 0

    def get_gradient_color(self, current_time):
        """Generates a color based on time"""
        r = int(127 + 127 * math.sin(current_time * 2))
        g = int(127 + 127 * math.sin(current_time * 3))
        b = int(127 + 127 * math.sin(current_time * 5))
        return (abs(r) % 256, abs(g) % 256, abs(b) % 256, 255)

    def run(self):
        """Main tracker loop"""
        print("Mouse gradient trail demonstration")
        print("The color changes automatically over time")

        try:
            while True:
                current_time = time.time() - self.start_time
                current_mouse_pos = GetCursorPos()
                x, y = current_mouse_pos

                # Exit check
                if self.is_escape_pressed():
                    break

                # Clear trail on right-click
                if self.is_right_click():
                    self.trail_points.clear()
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                    time.sleep(0.3)  # Debounce to avoid multiple triggers

                # Add a new point when the mouse moves
                if self.last_mouse_pos != current_mouse_pos:
                    color = self.get_gradient_color(current_time)
                    self.trail_points.append((x, y, color, current_time))

                    if len(self.trail_points) > self.max_trail_length:
                        self.trail_points.pop(0)

                self.last_mouse_pos = current_mouse_pos

                self.overlay.frame_clear()

                # Draw the trail
                for point_x, point_y, color, add_time in self.trail_points:
                    age = current_time - add_time
                    if age < 10:
                        alpha = max(0, 255 - int(age * 25))
                        fade_color = (color[0], color[1], color[2], alpha)
                        self.overlay.draw_circle(point_x, point_y, 1, fade_color)

                # Information panel
                current_color = self.trail_points[-1][2] if self.trail_points else (255, 255, 255, 255)
                self.draw_info_panel(len(self.trail_points), current_color)

                # Current cursor position
                self.overlay.draw_circle(x, y, 4, (255, 255, 255, 255), thickness=1)
                self.overlay.draw_circle(x, y, 2, current_color)

                self.overlay.signal_render()

        except KeyboardInterrupt:
            print("Tracker stopped")
        finally:
            self.overlay.stop_layer()


def main():
    tracker = MouseTracker()
    tracker.run()


if __name__ == "__main__":
    main()