"""
education_08_advanced_sprites.py
Advanced sprite techniques — new capabilities

Demonstrates:
- Creating sprites from NumPy arrays
- Screenshots as dynamic sprites
- Managing sprite cache
- Gradients and custom textures
- Sprite cache diagnostics
"""

import transparent_overlay
import numpy as np
import time
import math

try:
    import pyautogui

    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False
    print("pyautogui is not installed. Screenshots are unavailable.")


def create_gradient_sprite(overlay, width, height, color1, color2, direction='horizontal', alpha=255):
    """Creates a gradient sprite."""
    # Нормализуем цвета с учетом alpha
    color1 = (*color1[:3], alpha) if len(color1) == 3 else (*color1[:3], alpha)
    color2 = (*color2[:3], alpha) if len(color2) == 3 else (*color2[:3], alpha)

    gradient = np.zeros((height, width, 4), dtype=np.uint8)

    if direction == 'horizontal':
        for x in range(width):
            ratio = x / (width - 1) if width > 1 else 0
            gradient[:, x, 0] = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            gradient[:, x, 1] = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            gradient[:, x, 2] = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            gradient[:, x, 3] = int(color1[3] * (1 - ratio) + color2[3] * ratio)
    else:  # vertical
        for y in range(height):
            ratio = y / (height - 1) if height > 1 else 0
            gradient[y, :, 0] = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            gradient[y, :, 1] = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            gradient[y, :, 2] = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            gradient[y, :, 3] = int(color1[3] * (1 - ratio) + color2[3] * ratio)

    sprite_key = ('gradient', width, height, color1, color2, direction, alpha)
    return overlay.create_sprite_from_numpy(gradient, sprite_key)


def create_checkerboard_sprite(overlay, size, square_size, color1, color2, alpha=255):
    """Creates a checkerboard sprite."""
    # Нормализуем цвета с учетом alpha
    color1 = (*color1[:3], alpha) if len(color1) == 3 else (*color1[:3], alpha)
    color2 = (*color2[:3], alpha) if len(color2) == 3 else (*color2[:3], alpha)

    checkerboard = np.zeros((size, size, 4), dtype=np.uint8)

    for y in range(size):
        for x in range(size):
            if (x // square_size + y // square_size) % 2 == 0:
                checkerboard[y, x] = color1
            else:
                checkerboard[y, x] = color2

    sprite_key = ('checkerboard', size, square_size, color1, color2, alpha)
    return overlay.create_sprite_from_numpy(checkerboard, sprite_key)


def create_animated_texture_sprite(overlay, size, frame, alpha=255):
    """Creates an animated texture."""
    texture = np.zeros((size, size, 4), dtype=np.uint8)

    for y in range(size):
        for x in range(size):
            # Animated pattern
            value = math.sin(x * 0.1 + frame * 0.2) * math.cos(y * 0.1 + frame * 0.1)
            r = int(128 + 127 * math.sin(value + frame * 0.05))
            g = int(128 + 127 * math.cos(value + frame * 0.1))
            b = int(128 + 127 * math.sin(value * 2 + frame * 0.15))

            texture[y, x, 0] = r
            texture[y, x, 1] = g
            texture[y, x, 2] = b
            texture[y, x, 3] = alpha  # Теперь параметр!

    sprite_key = ('animated_texture', size, frame, alpha)
    return overlay.create_sprite_from_numpy(texture, sprite_key)


def create_screenshot_sprite(overlay, region, frame, alpha=255):
    """Creates a sprite from a screenshot of a screen region."""
    if not HAS_PYAUTOGUI:
        return None

    try:
        # Make a screenshot of the region
        screenshot = pyautogui.screenshot(region=region)

        # Convert to numpy array
        screenshot_array = np.array(screenshot)

        # Add alpha channel if needed
        if screenshot_array.shape[2] == 3:
            rgba_array = np.zeros((screenshot_array.shape[0], screenshot_array.shape[1], 4), dtype=np.uint8)
            rgba_array[:, :, :3] = screenshot_array
            rgba_array[:, :, 3] = alpha  # Now parameterized!
        else:
            rgba_array = screenshot_array
            rgba_array[:, :, 3] = alpha  # Set desired transparency

        sprite_key = ('screenshot', region, frame, alpha)
        return overlay.create_sprite_from_numpy(rgba_array, sprite_key)

    except Exception as e:
        print(f"Screenshot creation error: {e}")
        return None


class SpriteManager:
    def __init__(self, overlay):
        self.overlay = overlay
        self.created_sprites = []
        self.current_animated_sprite = None
        self.current_screenshot_sprite = None
        self.current_stats_sprite = None
        self.current_pulse_sprite = None
        self.dynamic_text_sprites = {}

    def create_demo_sprites(self):
        """Creates demo sprites with different transparency."""
        # Gradients with different transparency
        gradient_h = create_gradient_sprite(
            self.overlay, 200, 100,
            (255, 0, 0), (0, 0, 255), 'horizontal', alpha=180  # Полупрозрачный
        )
        gradient_v = create_gradient_sprite(
            self.overlay, 200, 100,
            (0, 255, 0), (255, 255, 0), 'vertical', alpha=150  # Более прозрачный
        )

        # Checkerboard
        checkerboard = create_checkerboard_sprite(
            self.overlay, 150, 15,
            (255, 255, 255), (100, 100, 100), alpha=220
        )

        self.created_sprites.extend([gradient_h, gradient_v, checkerboard])
        return gradient_h, gradient_v, checkerboard

    def update_animated_sprite(self, frame, alpha=200):
        """Updates the animated sprite with given transparency."""
        if self.current_animated_sprite:
            self.overlay.sprite_remove(self.current_animated_sprite)

        self.current_animated_sprite = create_animated_texture_sprite(
            self.overlay, 150, frame, alpha=alpha
        )
        return self.current_animated_sprite

    def update_screenshot_sprite(self, frame, alpha=255):
        """Updates the screenshot with given transparency."""
        if not HAS_PYAUTOGUI:
            return None

        if self.current_screenshot_sprite:
            self.overlay.sprite_remove(self.current_screenshot_sprite)

        try:
            x, y = pyautogui.position()
            region = (max(0, x - 100), max(0, y - 75), 200, 150)
            self.overlay.draw_rect(*region, color=(100, 100, 100, 255), thickness=2)
            self.current_screenshot_sprite = create_screenshot_sprite(
                self.overlay, region, frame, alpha=alpha
            )
            return self.current_screenshot_sprite, region
        except Exception as e:
            print(f"Screenshot update error: {e}")
            return None, None

    def update_pulse_sprite(self, pulse_size, alpha=180):
        """Updates the pulsing circle with given transparency."""
        if self.current_pulse_sprite:
            self.overlay.sprite_remove(self.current_pulse_sprite)

        self.current_pulse_sprite = self.overlay.create_circle_sprite(
            pulse_size, (255, 255, 0, alpha)  # Теперь с alpha
        )
        return self.current_pulse_sprite

    def update_stats_sprite(self, stats_text):
        """Updates the stats sprite, clearing the previous one."""
        # Remove the previous stats sprite
        if self.current_stats_sprite:
            self.overlay.sprite_remove(self.current_stats_sprite)

        # Create a new one
        self.current_stats_sprite = self.overlay.create_text_sprite(
            stats_text,
            font_size=15,
            color=(200, 200, 200, 255),
            highlight=True,
            bg_color=(0, 0, 0, 200)
        )
        return self.current_stats_sprite

    def update_dynamic_text(self, text_id, text, x, y, **kwargs):
        """Updates a dynamic text sprite, clearing the previous one."""
        # Удаляем предыдущий спрайт для этого текста
        if text_id in self.dynamic_text_sprites:
            old_sprite = self.dynamic_text_sprites[text_id]
            if old_sprite:
                self.overlay.sprite_remove(old_sprite)

        # Создаем новый спрайт
        new_sprite = self.overlay.create_text_sprite(text, **kwargs)
        self.dynamic_text_sprites[text_id] = new_sprite

        # Добавляем инстанс
        self.overlay.add_sprite_instance(new_sprite, x, y)
        return new_sprite

    def cleanup(self):
        """Cleans up all created sprites."""
        # Очищаем динамические спрайты
        dynamic_sprites = [
            self.current_animated_sprite,
            self.current_screenshot_sprite,
            self.current_stats_sprite,
            self.current_pulse_sprite
        ]

        for sprite in dynamic_sprites:
            if sprite:
                self.overlay.sprite_remove(sprite)

        # Очищаем динамические текстовые спрайты
        for sprite_key in self.dynamic_text_sprites.values():
            if sprite_key:
                self.overlay.sprite_remove(sprite_key)
        self.dynamic_text_sprites.clear()

        # Очищаем статические спрайты
        for sprite_key in self.created_sprites:
            self.overlay.sprite_remove(sprite_key)
        self.created_sprites.clear()


def main():
    overlay = transparent_overlay.Overlay()
    overlay.start_layer()

    sprite_manager = SpriteManager(overlay)

    print("Demonstration of advanced sprite features")
    print("Creating custom sprites from NumPy arrays")
    if HAS_PYAUTOGUI:
        print("Screenshots are available — will update in real-time")
    else:
        print("Screenshots are unavailable — install pyautogui")

    # Создаем демонстрационные спрайты
    gradient_h, gradient_v, checkerboard = sprite_manager.create_demo_sprites()

    try:
        frame = 0
        start_time = time.time()
        last_cache_size = len(overlay.sprite_cache)
        stable_frames = 0

        while time.time() - start_time < 20:  # seconds
            overlay.frame_clear()

            # === 1. STATIC CUSTOM SPRITES ===

            # Gradients
            overlay.add_sprite_instance(gradient_h, 50, 50)
            overlay.add_sprite_instance(gradient_v, 300, 50)

            # Checkerboard
            overlay.add_sprite_instance(checkerboard, 550, 50)

            # === 2. DYNAMIC ANIMATED SPRITES ===

            animated_sprite = sprite_manager.update_animated_sprite(frame)
            if animated_sprite:
                overlay.add_sprite_instance(animated_sprite, 50, 200)
                # Static text — via draw_text
                overlay.draw_rect(50, 200, 150, 150, (255, 255, 255, 255), thickness=1)
                overlay.draw_text(50, 200, "Animated texture",
                                  color=(255, 255, 255, 255), font_size=10,
                                  highlight=True, bg_color=(0, 0, 0, 150))

            # === 3. DYNAMIC SCREENSHOTS ===

            if HAS_PYAUTOGUI:
                # Update screenshot (old one automatically removed)
                screenshot_sprite, region = sprite_manager.update_screenshot_sprite(frame)
                if screenshot_sprite and region:
                    overlay.add_sprite_instance(screenshot_sprite, 250, 200)
                    # Outline for the screenshot
                    overlay.draw_rect(250, 200, 200, 150, (255, 0, 0, 255), thickness=2)
                    # Static text
                    overlay.draw_text(250, 200, "Region screenshot",
                                      color=(255, 255, 255, 255), font_size=10,
                                      highlight=True, bg_color=(0, 0, 0, 150))

            # === 4. ADDITIONAL DEMO SPRITES ===

            # Pulsing circle (with cleanup)
            pulse_size = 50 + int(20 * math.sin(frame * 0.1))
            pulse_sprite = sprite_manager.update_pulse_sprite(pulse_size)
            overlay.add_sprite_instance(pulse_sprite, 500 - pulse_size, 200 - pulse_size)
            # Static text
            overlay.draw_text(500, 200 + pulse_size - 20, "Pulsing circle",
                              color=(255, 255, 255, 255), font_size=12, anchor="mm",
                              highlight=True, bg_color=(0, 0, 0, 150))

            # === 5. INFORMATION PANEL ===

            # Main info — static background
            overlay.draw_rect(50, 400, 400, 200, (0, 0, 0, 180))
            overlay.draw_rect(50, 400, 400, 200, (100, 100, 200, 255), thickness=2)

            # Static title
            overlay.draw_text(70, 420, "Sprite cache management — Demo",
                              color=(255, 255, 255, 255), font_size=18)

            # Dynamic texts via SpriteManager (with cleanup)
            cache_size = len(overlay.sprite_cache)
            render_fps = overlay.get_render_fps()
            object_count = overlay.get_object_count()

            sprite_manager.update_dynamic_text(
                "cache_size", f"Cache size: {cache_size} sprites",
                70, 460, font_size=14, color=(200, 200, 255, 255),
                highlight=True, bg_color=(0, 0, 0, 120)
            )

            sprite_manager.update_dynamic_text(
                "object_count", f"Objects in frame: {object_count}",
                70, 490, font_size=14, color=(200, 255, 200, 255),
                highlight=True, bg_color=(0, 0, 0, 120)
            )

            sprite_manager.update_dynamic_text(
                "fps", f"Render FPS: {render_fps}",
                70, 520, font_size=14, color=(255, 200, 200, 255),
                highlight=True, bg_color=(0, 0, 0, 120)
            )

            sprite_manager.update_dynamic_text(
                "frame", f"Frame: {frame}",
                70, 550, font_size=14, color=(255, 255, 200, 255),
                highlight=True, bg_color=(0, 0, 0, 120)
            )

            # === 6. DIAGNOSTICS AND STATS ===

            stats_text, _ = overlay.get_render_statistics()

            # Update stats sprite (old one automatically removed)
            stats_sprite_key = sprite_manager.update_stats_sprite(stats_text)

            # Demo: reading sprite dimensions
            stats_sprite = overlay.sprite_cache.get(stats_sprite_key)
            if stats_sprite is not None:
                h, w = stats_sprite.shape[:2]

                # Outline with real dimensions
                padding = 5
                overlay.draw_rect(
                    50 - padding,
                    620 - padding,
                    w + padding * 2,
                    h + padding * 2,
                    (80, 80, 120, 255),
                    thickness=2
                )

            # Draw statistics
            overlay.add_sprite_instance(stats_sprite_key, 50, 620)

            # === 7. LEAK MONITORING ===

            current_cache_size = len(overlay.sprite_cache)
            if current_cache_size == last_cache_size:
                stable_frames += 1
            else:
                print(f"Frame {frame}: cache size changed {last_cache_size} -> {current_cache_size}")
                last_cache_size = current_cache_size
                stable_frames = 0

            # If cache is stable for 60 frames — print a message
            if stable_frames == 60:
                print(f"Frame {frame}: cache is stable ({current_cache_size} sprites)")
                stable_frames = 0

            overlay.signal_render()
            frame += 1
            time.sleep(1 / 60)

    except KeyboardInterrupt:
        print("Demo interrupted")
    finally:
        # Final statistics
        final_cache_size = len(overlay.sprite_cache)
        stats_text, _ = overlay.get_render_statistics()

        print("\n" + "=" * 60)
        print("FINAL CACHE STATISTICS")
        print("=" * 60)
        print(f"Cache size: {final_cache_size} sprites")
        print(f"Demo sprites created: {len(sprite_manager.created_sprites)}")
        print("\nRender statistics:")
        print(stats_text)

        # Cleanup
        sprite_manager.cleanup()
        overlay.sprite_clear_cache()
        final_after_cleanup = len(overlay.sprite_cache)
        overlay.stop_layer()

        print(f"\nAfter cleanup: {final_after_cleanup} sprites in cache")
        print("\n" + "=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✓ Creating sprites from NumPy arrays")
        print("✓ Dynamic updates with memory cleanup")
        print("✓ Sprite cache management")
        print("✓ Gradients and custom textures")
        print("✓ Diagnostics and leak monitoring")


if __name__ == "__main__":
    main()
