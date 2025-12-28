"""
education_02_transparency_layers.py
Transparency and layering order demonstration

Shows:
- How the order of draw calls affects z-order
- Interaction of semi-transparent objects
- Color blending via alpha channel
"""

from transparent_overlay import Overlay


def main():
    with Overlay() as overlay:
        print("Transparency and layering order demo...")

        # === EXAMPLE 1: background < text ===
        overlay.frame_clear()

        # First draw a semi-transparent background
        overlay.draw_rect(100, 100, 250, 150, (0, 0, 255, 100))  # Blue background

        # Then draw text above the background
        overlay.draw_text(150, 150, "Text above background",
                          color=(255, 255, 255, 255), font_size=16, highlight=True)

        overlay.draw_text(150, 180, "Order: background < text",
                          color=(200, 200, 200, 255), font_size=15, highlight=True, bg_color=(0, 0, 0, 255))

        # === EXAMPLE 2: text < background ===

        # First draw text
        overlay.draw_text(450, 150, "Text under background",
                          color=(255, 255, 255, 255), font_size=16, highlight=True)

        # Then cover it with background
        overlay.draw_rect(400, 100, 250, 150, (255, 0, 0, 100))  # Red background

        overlay.draw_text(450, 180, "Order: text < background",
                          color=(200, 200, 200, 255), font_size=15, highlight=True, bg_color=(0, 0, 0, 255))

        # === EXAMPLE 3: Multiple overlays ===

        # Draw in the correct order: from background to foreground
        overlay.draw_rect(100, 300, 300, 200, (0, 0, 0, 200))  # Dark background

        overlay.draw_rect(120, 320, 100, 100, (255, 0, 0, 100))  # Red square
        overlay.draw_rect(180, 350, 100, 100, (0, 255, 0, 100))  # Green square
        overlay.draw_rect(140, 380, 100, 100, (0, 0, 255, 100))  # Blue square

        overlay.draw_text(100, 300, "Color blending via transparency",
                          color=(255, 255, 255, 255), font_size=14, box_size=(300, 200), align='center')

        overlay.signal_render()
        input("Press Enter to exit...")

        print("Demo finished.")


if __name__ == "__main__":
    main()
