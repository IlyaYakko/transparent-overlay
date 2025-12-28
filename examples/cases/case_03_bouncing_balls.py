"""
06_bouncing_balls.py
Animated bouncing balls — performance test

Demonstrates:
- Particle physics with wall bounces
- Real-time timing for smooth animation
- Monitoring of render FPS and generation FPS
- Scalability with a large number of objects
"""

import transparent_overlay
import time
import random
import math


class Ball:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.radius = random.randint(15, 35)
        self.x = random.randint(self.radius, screen_width - self.radius)
        self.y = random.randint(self.radius, screen_height - self.radius)

        speed = random.uniform(50, 200)
        angle = random.uniform(0, 2 * math.pi)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)

        self.color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(128, 255)
        )

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.x <= self.radius:
            self.x = self.radius
            self.vx = abs(self.vx)
        elif self.x >= self.screen_width - self.radius:
            self.x = self.screen_width - self.radius
            self.vx = -abs(self.vx)

        if self.y <= self.radius:
            self.y = self.radius
            self.vy = abs(self.vy)
        elif self.y >= self.screen_height - self.radius:
            self.y = self.screen_height - self.radius
            self.vy = -abs(self.vy)


class PreciseTimer:
    def __init__(self, target_fps):
        self.target_frame_time = 1.0 / target_fps
        self.next_frame_time = time.perf_counter()

    def wait_next_frame(self):
        current_time = time.perf_counter()

        # Ждем до запланированного времени следующего кадра
        sleep_time = self.next_frame_time - current_time

        if sleep_time > 0.001:
            time.sleep(sleep_time * 0.9)

        # Планируем следующий кадра
        self.next_frame_time += self.target_frame_time


def main():
    # Settings (tweak for performance testing)
    target_fps = 60  # Try 100, 200, 1000!
    ball_count = 500   # Try 100, 200, 5000!
    duration = 10     # Total run time in seconds
    # overlay = transparent_overlay.Overlay(0, 0, 1000, 500)
    overlay = transparent_overlay.Overlay()
    overlay.start_layer()
    screen_width = overlay.width
    screen_height = overlay.height
    balls = [Ball(screen_width, screen_height) for _ in range(ball_count)]
    frame_count = 0
    gen_fps = 0
    fps_update_time = time.time()
    start_time = time.time()
    last_update_time = time.perf_counter()  # Для точного real_dt
    timer = PreciseTimer(target_fps)  # Create frame timer
    print("Starting balls simulation...")
    print(f"Balls: {ball_count}, Target FPS: {target_fps}")
    print("Try changing target_fps and ball_count in code!")
    try:
        while time.time() - start_time < duration:
            current_time = time.perf_counter()
            real_dt = current_time - last_update_time
            last_update_time = current_time

            overlay.frame_clear()

            for i, ball in enumerate(balls):
                ball.update(real_dt)
                overlay.draw_circle(int(ball.x), int(ball.y), int(ball.radius), ball.color)
                # overlay.draw_text(x=ball.x, y=ball.y, text=f'{i}', highlight=True, anchor='mm')
            overlay.draw_rect(10, 10, 200, 140, (0, 0, 0, 180))
            overlay.draw_rect(10, 10, 200, 140, (100, 100, 200, 255), thickness=2)
            overlay.draw_text(20, 20, f"Balls: {ball_count}",
                              color=(255, 255, 255, 255), font_size=14)
            overlay.draw_text(20, 45, f"Gen FPS: {gen_fps}",
                              color=(100, 255, 100, 255), font_size=14)
            render_fps = overlay.get_render_fps()
            object_count = overlay.get_object_count()
            elapsed = time.time() - start_time
            overlay.draw_text(20, 70, f"Rend FPS: {render_fps}",
                              color=(200, 200, 255, 255), font_size=14)
            overlay.draw_text(20, 95, f"Objects: {object_count}",
                              color=(255, 200, 100, 255), font_size=14)
            overlay.draw_text(20, 120, f"Time: {elapsed:.1f}s",
                              color=(200, 255, 200, 255), font_size=12)
            overlay.signal_render()

            # Wait until next planned frame time
            timer.wait_next_frame()

            frame_count += 1
            current_time_fps = time.time()
            if current_time_fps - fps_update_time >= 1.0:
                gen_fps = frame_count
                frame_count = 0
                fps_update_time = current_time_fps

    except KeyboardInterrupt:
        pass
    finally:
        overlay.stop_layer()
        print("Simulation finished")


if __name__ == "__main__":
    main()
