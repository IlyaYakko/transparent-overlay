"""
education_01_basic_shapes.py
The simplest example — basic shapes

Shows:
- Creating an overlay
- Drawing a circle, rectangle, line and text
- Single render without animation
"""

from transparent_overlay import Overlay

with Overlay() as overlay:

    overlay.draw_circle(200, 150, 50, (255, 0, 0, 180))
    overlay.draw_rect(350, 100, 120, 80, (0, 0, 255, 160))
    overlay.draw_line(500, 100, 650, 180, (0, 255, 0, 255), thickness=3)
    overlay.draw_text(400, 50, "Basic Shapes", color=(255, 255, 255, 255), font_size=50)

    overlay.signal_render()
    input("Press Enter to exit...")
