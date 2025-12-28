from transparent_overlay import Overlay
import time
import numpy as np
import math

# Build a small RGBA numpy sprite (soft blob)
def make_blob(size=48, color=(80, 200, 255, 200)):
    h = w = size
    y, x = np.ogrid[:h, :w]
    cy, cx = h / 2, w / 2
    r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    alpha = np.clip(1.0 - (r / (size / 2)), 0.0, 1.0)
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    arr[..., 0] = color[0]
    arr[..., 1] = color[1]
    arr[..., 2] = color[2]
    arr[..., 3] = (alpha * color[3]).astype(np.uint8)
    return arr

with Overlay() as overlay:
    # Create 8 blobs with slight color variations
    sprites = []
    for i in range(8):
        hue_shift = i * 20
        c = ((80 + hue_shift) % 255, (200 + hue_shift * 2) % 255, (255 - hue_shift) % 255, 200)
        key = ('numpy_blob', i)
        overlay.create_sprite_from_numpy(make_blob(48, c), key)
        sprites.append(key)

    t0 = time.time()
    fps = 60
    duration = 10.0
    W, H = overlay.width, overlay.height

    while time.time() - t0 < duration:
        overlay.frame_clear()
        t = time.time() - t0
        for idx, key in enumerate(sprites):
            angle = t * 2 * math.pi * (0.25 + 0.05 * idx)
            radius = 60 + 10 * idx
            cx = int(W * 0.7) + int(radius * math.cos(angle + idx))
            cy = int(H * 0.5) + int(radius * math.sin(angle + 0.5 * idx))
            overlay.add_sprite_instance(key, cx - 24, cy - 24)
        overlay.signal_render()
        time.sleep(1 / fps)
