from transparent_overlay import Overlay
import numpy as np
from PIL import Image
from pathlib import Path

with Overlay() as overlay:
    w, h = overlay.width, overlay.height
    wm, hm = w // 2, h // 2
    dw, dh = 1500, 400
    left = wm - 800
    top = hm - dh//2
    right = left + dw
    bottom = top + dh
    overlay.draw_rect(x=left, y=top, width=dw, height=dh, color=(0, 0, 0, 170))

    overlay.draw_text(x=wm - 200, y=hm, text="Transparent Overlay", color=(80, 180, 255, 255), font_size=130,
                      anchor='mm', highlight=True, bg_color=(35, 149, 161, 20))

    overlay.draw_circle(wm + 480, hm - 40, 60, (255, 0, 0, 180))
    overlay.draw_rect(wm + 460, hm, 160, 50, (0, 0, 255, 160))
    overlay.draw_line(wm + 410, hm - 80, wm + 470, hm + 50, (0, 255, 0, 180), thickness=5)
    overlay.draw_text(wm + 460, hm, "text", color=(255, 255, 255, 100), font_size=50, box_size=(160, 50),
                      align='center', valign='middle')

    # Resolve logo path relative to project root so it works from any CWD
    project_root = Path(__file__).resolve().parents[2]
    logo_path = project_root / "assets" / "images" / "python-logo.png"
    logo = Image.open(logo_path).convert("RGBA")
    Resampling = getattr(Image, "Resampling", Image)
    logo = logo.rotate(-25, expand=True, resample=Resampling.BICUBIC)
    logo.thumbnail((140, 140), resample=Resampling.LANCZOS)
    arr = np.array(logo, dtype=np.uint8)
    sprite_key = ("img", "python_logo", -25, 140)
    overlay.create_sprite_from_numpy(arr, sprite_key)
    overlay.add_sprite_instance(sprite_key, wm + 510, hm - 110)

    overlay.signal_render()

    # --- Optional: capture the hero area to PNG (commented out) ---
    # def _capture_hero_area(bbox, out_path):
    #     """Capture screen region and save to PNG. Requires Pillow ImageGrab.
    #     bbox: (left, top, right, bottom)
    #     out_path: pathlib.Path
    #     """
    #     import time
    #     from PIL import ImageGrab
    #     time.sleep(1)  # small delay to ensure the overlay is on top
    #     img = ImageGrab.grab(bbox=bbox)
    #     img.save(out_path)
    #
    # _capture_hero_area(
    #     bbox=(left, top, right, bottom),
    #     out_path=project_root / "assets" / "images" / "hero_placeholder.png",
    # )

    input("Press Enter to exit...")
