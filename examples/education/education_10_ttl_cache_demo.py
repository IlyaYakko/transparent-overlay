"""
education_10_ttl_cache_demo.py
Demonstration of automatic sprite cache cleanup by TTL and manual cleanup.

Shows:
- Configuring overlay.sprite_ttl_seconds / ttl_cleanup_period_seconds / enable_auto_ttl_cleanup
- Mass creating temporary text sprites
- Automatic removal of unused sprites
"""

import time
import random
import transparent_overlay


def main():
    overlay = transparent_overlay.Overlay()
    overlay.start_layer()

    # TTL configuration for visible accumulation and cleanup cycles
    overlay.sprite_ttl_seconds = 0.2  # keep unused sprites for 0.1 seconds
    overlay.ttl_cleanup_period_seconds = 1.0  # check every 1 second
    overlay.enable_auto_ttl_cleanup = True  # enable auto cleanup

    start_time = time.time()
    frame = 0

    try:
        while time.time() - start_time < 12:
            overlay.frame_clear()

            # Calculate dimensions for the background rectangle
            # Cover all text elements (20 items in 2 rows of 10)
            rect_x = 10
            rect_y = 10
            rect_width = 10 * 120  # 10 columns * 120px width
            rect_height = 2 * 30 + 50  # 2 rows * 30px + 50px for header
            
            # Draw semi-transparent background for all elements
            overlay.draw_rect(rect_x, rect_y, rect_width+20, rect_height, color=(0, 0, 0, 200))  # Dark semi-transparent background
            
            # Draw header text on top of the background
            overlay.draw_text(20, 20, "TTL cache demo", font_size=20, color=(255, 255, 255))
            overlay.draw_text(20, 50,
                            f"ttl={overlay.sprite_ttl_seconds}s, period={overlay.ttl_cleanup_period_seconds}s",
                            font_size=14, color=(200, 200, 255))
            
            # Create a batch of text sprites that expire quickly
            for i in range(20):
                txt = f"temp-{frame}-{i}-{random.randint(0, 999)}"
                key = overlay.create_text_sprite(txt, font_size=14, highlight=True, color=(255, 255, 255))
                overlay.add_sprite_instance(key, 40 + (i % 10) * 120, 60 + (i // 10) * 30)

            # Present frame
            overlay.signal_render()
            time.sleep(0.1)  # Slow down the loop for better visibility
            frame += 1
            # Print cache status every frame for better visibility
            print(f'Frame: {frame:3d} | Sprites in cache: {len(overlay.sprite_cache):3d} | Time: {time.time()-start_time:.1f}s')
            # Run for about 15 seconds to see multiple cycles
            if time.time() - start_time > 15:
                break

        # Final manual cleanup of old sprites (in case of pause)
        overlay.sprite_clear_cache()
        print(f'Sprites in cache after full cleanup: {len(overlay.sprite_cache)}')

    except KeyboardInterrupt:
        pass
    finally:
        overlay.stop_layer()


if __name__ == "__main__":
    main()
