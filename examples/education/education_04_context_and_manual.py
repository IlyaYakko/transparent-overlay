"""
education_04_context_and_manual.py
Two safe ways to manage the overlay layer:

1) Context manager: with Overlay() as overlay:
   - Automatic start and proper resource release even on exceptions.

2) Manual management: overlay = transparent_overlay.Overlay(); overlay.start_layer(); ...; overlay.stop_layer()
   - Full control over the layer lifecycle (important to call stop_layer()).
"""

import time
import transparent_overlay
from transparent_overlay import Overlay


def demo_with_context_manager(duration: float = 2.0) -> None:
    """Shows using the layer as a context manager."""
    with Overlay() as overlay:
        t0 = time.time()
        while time.time() - t0 < duration:
            overlay.frame_clear()
            overlay.draw_rect(250, 200, 260, 40, (0, 0, 0, 120))
            overlay.draw_text(250, 200, box_size=(260, 40), text="Context Manager Demo", color=(255, 255, 255),
                              font_size=20, align='center', valign='middle')
            overlay.draw_line(260, 250, 490, 250, (255, 200, 0, 255), thickness=2)
            overlay.signal_render()
            time.sleep(1 / 60)


def demo_with_manual_start_stop(duration: float = 2.0) -> None:
    """Shows manual start/stop of the layer."""
    overlay = transparent_overlay.Overlay()
    try:
        overlay.start_layer()
        t0 = time.time()
        while time.time() - t0 < duration:
            overlay.frame_clear()
            overlay.draw_rect(450, 200, 300, 50, (0, 0, 0, 120))
            overlay.draw_text(450, 200, box_size=(300, 50), text="Manual start/stop Demo", color=(255, 255, 255),
                              font_size=20, align='center', valign='middle')
            overlay.draw_line(460, 260, 740, 260, (0, 200, 255, 255), thickness=2)
            overlay.signal_render()
            time.sleep(1 / 60)
    finally:
        # Important to properly stop the layer to free OS window/DC resources
        overlay.stop_layer()


def main() -> None:
    demo_with_context_manager(2.5)
    demo_with_manual_start_stop(2.5)


if __name__ == "__main__":
    main()
