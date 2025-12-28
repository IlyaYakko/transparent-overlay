"""
case_05_magnifier_fisheye.py
Screen magnifier on a transparent overlay with a "fisheye" effect

Demonstrates:
- Separating capture region and display region (no self-capture of the overlay)
- Barrel transform: enlarged center and compressed edges (gamma)
- Smooth following (inertia) and keeping lens within the screen
- Decorative handle that rotates automatically and exits the lens perpendicular to the edge
- Tunable magnification and distortion (gamma)


Controls:
- Move the cursor over the screen — the magnifier shows an enlarged fragment nearby
- Adjust parameters in the Magnifier class: magnification, gamma, lens_radius
"""

import math
import time
import win32api
import numpy as np
from PIL import Image, ImageDraw, ImageGrab
from transparent_overlay import Overlay


class Magnifier:
    def __init__(self):
        self.overlay = Overlay()
        self.magnification = 2.0  # Magnification
        self.gamma = 1.0  # Fisheye
        self.lens_radius = 100  # Lens radius
        self.handle_length = 150  # Handle length
        # Separate capture place and display place
        # Capture — near cursor, Display — with offset to avoid self-capture
        self.capture_offset = (0, 0)  # (dx, dy) относительно курсора
        self.display_offset = (220, 0)  # (dx, dy) lens center relative to cursor

        # Создаем спрайты один раз при инициализации
        self.create_handle_sprite()
        self.create_lens_border_sprite()

    def create_handle_sprite(self):
        """Creates a wooden handle sprite with a highlight"""
        width = 25
        length = self.handle_length

        # Build handle image via numpy for full control
        arr = np.zeros((length, width, 4), dtype=np.uint8)

        # Base wood color
        wood_base = np.array([139, 69, 19, 255], dtype=np.uint8)

        # Заполняем основу
        for y in range(length):
            for x in range(width):
                # Highlight gradient — left side brighter
                if x < width // 3:
                    highlight = min(50, (width // 3 - x) * 15)
                    color = wood_base + [highlight, highlight, highlight, 0]
                    color = np.clip(color, 0, 255)
                else:
                    color = wood_base

                # Darker to the right edge for volume
                if x > width * 2 // 3:
                    shadow = min(30, (x - width * 2 // 3) * 10)
                    color = wood_base - [shadow, shadow, shadow, 0]
                    color = np.clip(color, 0, 255)

                arr[y, x] = color

        # Round the ends (top and bottom)
        for i in range(5):
            # Верхнее закругление
            taper = i
            for x in range(taper, width - taper):
                if i < length:
                    arr[i, x] = wood_base

            # Нижнее закругление
            for x in range(taper, width - taper):
                if length - i - 1 >= 0:
                    arr[length - i - 1, x] = wood_base

        # Store base PIL image for rotation
        self.handle_base_img = Image.fromarray(arr, mode='RGBA')
        # Базовый (неповернутый) спрайт тоже можно создать
        self.overlay.create_sprite_from_numpy(arr, 'handle')

    def create_lens_border_sprite(self):
        """Creates the lens border sprite"""
        size = self.lens_radius * 2 + 10
        arr = np.zeros((size, size, 4), dtype=np.uint8)

        center = size // 2
        outer_radius = self.lens_radius + 4
        inner_radius = self.lens_radius - 2

        # Draw a ring via circle math
        for y in range(size):
            for x in range(size):
                dist = math.sqrt((x - center) ** 2 + (y - center) ** 2)

                # Outer silver ring
                if outer_radius - 2 <= dist <= outer_radius:
                    # Gradient for volume
                    if dist > outer_radius - 1:
                        arr[y, x] = [150, 150, 150, 255]  # Темнее край
                    else:
                        arr[y, x] = [220, 220, 220, 255]  # Светлее внутренняя часть

                # Inner dark ring
                elif inner_radius <= dist <= inner_radius + 2:
                    arr[y, x] = [80, 80, 80, 200]

                # Highlight on the ring (north-west sector)
                elif abs(dist - (outer_radius - 1)) < 0.5:
                    angle = math.atan2(y - center, x - center)
                    if math.pi * 0.7 <= angle <= math.pi * 1.1:  # Верхний левый сектор
                        arr[y, x] = [255, 255, 255, 255]

        self.overlay.create_sprite_from_numpy(arr, 'lens_border')

    def fish_eye_transform(self, x, y, center_x, center_y, radius, gamma: float = 2.0):
        """
        Inverse radial mapping (barrel): center enlarged, edges compressed.
        gamma (>1) increases center magnification.
        Input: target coordinate (x,y). Returns source coordinate.
        """
        dx = x - center_x
        dy = y - center_y
        r = math.hypot(dx, dy)
        if r >= radius or r == 0:
            return x, y
        rn = r / radius
        rn_src = rn ** gamma  # при gamma>1: rn_src < rn, значит берем источник ближе к центру
        scale = (rn_src * radius) / r
        return center_x + dx * scale, center_y + dy * scale

    def capture_and_process_lens(self, center_x, center_y):
        """Capture a region around cursor using ImageGrab"""
        try:
            # Capture area size (larger than lens for magnification)
            capture_size = int(self.lens_radius * 2 / self.magnification)

            # Compute capture region (center_x/center_y include capture_offset)
            left = max(0, int(center_x - capture_size // 2))
            top = max(0, int(center_y - capture_size // 2))
            right = left + capture_size
            bottom = top + capture_size

            # Grab the screen region
            screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
            # Resize (magnify) the image
            new_size = self.lens_radius * 2
            img = screenshot.resize((new_size, new_size), Image.Resampling.LANCZOS)

            # Apply fisheye (bigger center)
            if self.magnification > 1.0:
                img = img.convert('RGB')
                pixels = img.load()

                # Create new result image
                result_img = Image.new('RGB', (new_size, new_size))
                result_pixels = result_img.load()

                center = new_size // 2

                for y in range(new_size):
                    for x in range(new_size):
                        # Inverse map: result -> source
                        src_x, src_y = self.fish_eye_transform(
                            x, y, center, center, self.lens_radius, self.gamma
                        )

                        if 0 <= src_x < new_size and 0 <= src_y < new_size:
                            result_pixels[x, y] = pixels[int(src_x), int(src_y)]
                        else:
                            result_pixels[x, y] = (0, 0, 0)  # Black border

                img = result_img

            # Create a circular mask for the lens
            mask = Image.new('L', (new_size, new_size), 0)
            draw_mask = ImageDraw.Draw(mask)

            # Draw circular mask
            center = new_size // 2
            for y in range(new_size):
                for x in range(new_size):
                    dist = math.sqrt((x - center) ** 2 + (y - center) ** 2)
                    if dist <= self.lens_radius:
                        mask.putpixel((x, y), 255)

            # Apply the mask
            lens_img = Image.new('RGBA', (new_size, new_size), (0, 0, 0, 0))
            lens_img.paste(img, (0, 0), mask)

            return lens_img

        except Exception as e:
            print(f"Screen capture error: {e}")
            # Return a placeholder image on error
            return Image.new('RGBA', (self.lens_radius * 2, self.lens_radius * 2), (0, 0, 0, 128))

    def run(self):
        """Main loop with smooth movement"""
        screen_w = win32api.GetSystemMetrics(0)
        screen_h = win32api.GetSystemMetrics(1)
        screen_cx, screen_cy = screen_w // 2, screen_h // 2

        # Текущее положение центра линзы
        current_dx = 0
        current_dy = 0

        smoothing = 1  # higher -> faster convergence (0.1–0.3 is optimal)
        min_dist = self.lens_radius * 2  # minimum distance from cursor

        with self.overlay:
            print("Magnifier started. Move cursor to magnify a region.")
            print("Press Ctrl+C in console to exit.")

            while True:
                try:
                    cursor_x, cursor_y = win32api.GetCursorPos()
                    self.overlay.frame_clear()

                    # ---- Desired direction: from cursor to screen center ----
                    vec_to_center_x = screen_cx - cursor_x
                    vec_to_center_y = screen_cy - cursor_y
                    length = math.hypot(vec_to_center_x, vec_to_center_y)

                    if length == 0:
                        dir_x, dir_y = 1, 0
                    else:
                        dir_x = vec_to_center_x / length
                        dir_y = vec_to_center_y / length

                    # Base target offset along the line (always from center toward cursor)
                    target_dx = dir_x * min_dist
                    target_dy = dir_y * min_dist

                    # ---- Correction if lens goes out of screen ----
                    lens_diam = self.lens_radius * 2
                    disp_cx = cursor_x + target_dx
                    disp_cy = cursor_y + target_dy

                    if disp_cx - self.lens_radius < 0:
                        target_dx += (self.lens_radius - disp_cx)
                    elif disp_cx + self.lens_radius > screen_w:
                        target_dx -= (disp_cx + self.lens_radius - screen_w)

                    if disp_cy - self.lens_radius < 0:
                        target_dy += (self.lens_radius - disp_cy)
                    elif disp_cy + self.lens_radius > screen_h:
                        target_dy -= (disp_cy + self.lens_radius - screen_h)

                    # ---- Smooth movement (inertia) ----
                    current_dx += (target_dx - current_dx) * smoothing
                    current_dy += (target_dy - current_dy) * smoothing

                    # Итоговая позиция центра лупы
                    disp_cx = cursor_x + current_dx
                    disp_cy = cursor_y + current_dy

                    # ---- Capture and render ----
                    cap_x = cursor_x + self.capture_offset[0]
                    cap_y = cursor_y + self.capture_offset[1]
                    lens_img = self.capture_and_process_lens(cap_x, cap_y)

                    lens_arr = np.array(lens_img, dtype=np.uint8)
                    self.overlay.create_sprite_from_numpy(lens_arr, 'lens_content')

                    lens_x = int(disp_cx - self.lens_radius)
                    lens_y = int(disp_cy - self.lens_radius)

                    self.overlay.add_sprite_instance('lens_content', lens_x, lens_y)
                    self.overlay.add_sprite_instance('lens_border', lens_x - 5, lens_y - 5)

                    # ---- Handle rotation/position: towards screen center ----
                    # Direction from lens center to screen center
                    dir_x = screen_cx - cursor_x
                    dir_y = screen_cy - cursor_y
                    dir_len = math.hypot(dir_x, dir_y) or 1.0
                    ux, uy = dir_x / dir_len, dir_y / dir_len

                    # Rotation angle (degrees). Base handle is along +Y,
                    # so rotate by (-angle + 90°) to align +Y to (ux, uy)
                    angle_deg = math.degrees(math.atan2(uy, ux))
                    rot_img = self.handle_base_img.rotate(-angle_deg + 90, expand=True,
                                                          resample=Image.Resampling.BICUBIC)

                    rot_w, rot_h = rot_img.size

                    # Handle joint point on lens rim
                    base_x = disp_cx + ux * (self.lens_radius - 4)
                    base_y = disp_cy + uy * (self.lens_radius - 4)

                    # Center of rotated sprite should be at half length from joint along direction
                    center_x = base_x + ux * (self.handle_length / 2)
                    center_y = base_y + uy * (self.handle_length / 2)

                    # Top-left of the rotated texture
                    tl_x = int(center_x - rot_w / 2)
                    tl_y = int(center_y - rot_h / 2)

                    # Build a sprite from the rotated image
                    handle_arr = np.array(rot_img, dtype=np.uint8)
                    self.overlay.create_sprite_from_numpy(handle_arr, 'handle_rot')
                    self.overlay.add_sprite_instance('handle_rot', tl_x, tl_y)

                    # ---- FPS ----
                    self.overlay.draw_text(
                        10, 10,
                        f"FPS: {self.overlay.get_render_fps()}",
                        color=(255, 255, 255, 255),
                        font_size=14,
                        highlight=True,
                        bg_color=(0, 0, 0, 128)
                    )

                    self.overlay.signal_render()
                    time.sleep(0.01)

                except KeyboardInterrupt:
                    print("\nExiting magnifier...")
                    break
                except Exception as e:
                    print(f"Error in main loop: {e}")
                    time.sleep(0.1)


# Запуск лупы
if __name__ == "__main__":
    magnifier = Magnifier()
    magnifier.run()
