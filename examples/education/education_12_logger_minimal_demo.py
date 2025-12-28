"""
education_12_logger_minimal_demo.py
Minimal logger exercise

Shows:
- Enabling logging
- INFO lifecycle messages (start/stop/cleanup)
- WARNING-once diagnostics (invalid anchor, invalid box_size, missing/off-screen sprite, zero-length line)
- DEBUG diagnostics (color clamping, sprite_remove not found)
"""

import logging
import time
from transparent_overlay import Overlay

# Enable detailed logging for the demo
logging.basicConfig(level=logging.DEBUG)

with Overlay() as overlay:
    # INFO lifecycle messages will appear automatically on start/stop/cleanup

    # DEBUG: color components get clamped to 0..255 during normalization
    # Expect: DEBUG about clamping
    overlay.draw_rect(10, 10, 50, 30, color=(300, -20, 1000, 500))

    # WARNING-once: invalid text anchor falls back to 'lt'
    # Expect: WARNING once about invalid anchor
    overlay.draw_text(100, 100, "Invalid anchor example", anchor="bad")

    # WARNING-once: invalid box_size is ignored (fallback to auto-sized text)
    # Expect: WARNING once about invalid box_size
    overlay.draw_text(100, 140, "Invalid box_size example", box_size=(0, 50), fit_text=True)

    # WARNING-once: zero-length line renders as a point
    # Expect: WARNING once about zero-length line
    overlay.draw_line(200, 200, 200, 200, (255, 255, 0, 255), thickness=3)

    # WARNING-once: sprite fully outside the screen is skipped
    # Expect: WARNING once about sprite fully outside the screen
    offscreen_key = overlay.create_rect_sprite(40, 20, (255, 255, 255, 128))
    overlay.add_sprite_instance(offscreen_key, overlay.width + 100, overlay.height + 100)

    # WARNING-once: missing sprite key in cache during render
    # Expect: WARNING once about missing sprite
    overlay.add_sprite_instance(("missing", "sprite", "key"), 50, 50)

    # DEBUG: removing a non-existent sprite key
    # Expect: DEBUG about sprite_remove not found
    overlay.sprite_remove(("no_such", "key"))

    # Render the frame(s)
    overlay.signal_render()

    input("Press Enter to exit...")
