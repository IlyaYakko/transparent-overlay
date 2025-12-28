"""
case_07_performance_benchmark.py
Automatic performance benchmark — stress test

Demonstrates:
- Automatically increasing load until FPS drops below a critical threshold
- Comparing generation and render performance
- Real-time stats with plots
- Smooth object addition at adaptive rate
- Determining the system's maximum load
"""

import os
import transparent_overlay
import time
import random
import math
import matplotlib.pyplot as plt
import statistics
import numpy as np


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

        sleep_time = self.next_frame_time - current_time

        if sleep_time > 0.001:
            time.sleep(sleep_time * 0.9)

        self.next_frame_time += self.target_frame_time


def main():
    # Test settings (minimal set of parameters)
    def _get_float(name, default):
        try:
            return float(os.getenv(name, default))
        except Exception:
            return default

    def _get_int(name, default):
        try:
            return int(float(os.getenv(name, default)))
        except Exception:
            return default

    target_fps = _get_float('TARGET_FPS', 60)       # Target FPS for timer
    critical_fps = _get_float('CRITICAL_FPS', 10)   # Critical FPS to stop
    initial_ball_count = _get_int('INITIAL_BALLS', 10)  # Initial balls
    max_duration = _get_float('MAX_DURATION', 60)   # Max test time
    warmup_time = _get_float('WARMUP', 2.0)         # Warmup before adding
    # Enable plots by default; set DISABLE_PLOT to a truthy value to disable
    disable_plot = os.getenv('DISABLE_PLOT', '').strip().lower() in ('1', 'true', 'yes', 'on')
    disable_hud = os.getenv('DISABLE_HUD', '').strip() not in ('', '0', 'false', 'False')

    # Фиксированные параметры (упрощение)
    ball_increment = 1.0
    increment_interval = 0.2
    update_every_n = 1
    precreate_pool_size = 50000
    palette_size = 32

    # Initialization
    overlay = transparent_overlay.Overlay()
    overlay.start_layer()
    screen_width = overlay.width
    screen_height = overlay.height

    # Pre-create object pool
    ball_pool = [Ball(screen_width, screen_height) for _ in range(precreate_pool_size)]
    pool_index = 0

    # Limit radii/colors and pre-create sprites
    random.seed(12345)
    radius_set = [16, 20, 24, 28, 32]
    color_palette = [
        (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(160, 255),
        )
        for _ in range(palette_size)
    ]
    sprite_keys = {}
    for r in radius_set:
        for c in color_palette:
            key = (r, c)
            sprite_keys[key] = overlay.create_circle_sprite(r, c, thickness=0)

    # Assign nearest radius/color to each ball from palette
    for b in ball_pool:
        r = min(radius_set, key=lambda rr: abs(rr - b.radius))
        c = color_palette[random.randrange(palette_size)]
        b.radius = r
        b.color = c
        b._sprite_key = sprite_keys[(r, c)]

    # Initial balls
    init_take = min(initial_ball_count, len(ball_pool) - pool_index)
    pool_index += init_take
    ball_count = init_take

    # Create NumPy arrays
    pool_size = len(ball_pool)
    x = np.array([b.x for b in ball_pool], dtype=np.float64)
    y = np.array([b.y for b in ball_pool], dtype=np.float64)
    vx = np.array([b.vx for b in ball_pool], dtype=np.float64)
    vy = np.array([b.vy for b in ball_pool], dtype=np.float64)
    r = np.array([b.radius for b in ball_pool], dtype=np.int32)
    sprite_key_list = [b._sprite_key for b in ball_pool]

    # Stats
    frame_count = 0
    gen_fps = 0
    fps_update_time = time.time()
    start_time = time.time()
    last_update_time = time.perf_counter()

    # Ball addition control
    accumulated_balls = 0.0
    balls_per_second = ball_increment / increment_interval

    timer = PreciseTimer(target_fps)

    # Stats to output
    max_ball_count = ball_count
    gen_fps_history = []
    rend_fps_history = []
    ball_count_history = []
    times_history = []
    min_gen_fps = float('inf')
    max_gen_fps = 0
    min_rend_fps = float('inf')
    max_rend_fps = 0
    last_stat_time = time.time()
    stat_interval = 1.0

    # Dropped frames counters
    dropped_frames = 0
    total_frames = 0
    # Measurement-only counters (start after warmup)
    measurement_dropped_frames = 0
    measurement_total_frames = 0
    dt_accum = 0.0

    print("Starting FPS test with balls...")
    print(f"Target FPS: {target_fps}, Critical FPS: {critical_fps}")
    print(f"Initial balls: {initial_ball_count}")
    print("=" * 60)

    warmup_complete = False
    warmup_start_time = time.time()

    try:
        while time.time() - start_time < max_duration:
            current_time = time.perf_counter()
            real_dt = current_time - last_update_time
            last_update_time = current_time

            total_frames += 1
            if warmup_complete:
                measurement_total_frames += 1

            # Clear and draw frame
            overlay.frame_clear()

            # Optional centered banner text (e.g., WITH/WITHOUT NUMBA)
            banner_text = os.getenv('BANNER_TEXT', '').strip()
            if banner_text:
                wm, hm = screen_width // 2, screen_height // 2
                bw, bh = 900, 120
                left = max(0, wm - bw // 2)
                top = max(0, hm - bh // 2)
                overlay.draw_rect(left, top, bw, bh, (0, 0, 0, 180))
                overlay.draw_rect(left, top, bw, bh, (100, 100, 200, 220), thickness=2)
                # Large centered label
                try:
                    overlay.draw_text(wm, hm, banner_text, color=(255, 255, 255, 240), font_size=72,
                                      anchor='mm', highlight=True, bg_color=(35, 149, 161, 20))
                except TypeError:
                    # Fallback if anchor/highlight not supported
                    overlay.draw_text(wm - 300, hm - 30, banner_text, color=(255, 255, 255, 240), font_size=72)

            # Accumulate dt and update physics every N frames
            dt_accum += real_dt
            do_update = (total_frames % update_every_n) == 0

            # Векторизованное обновление позиций
            if ball_count > 0:
                idx = slice(0, ball_count)
                if do_update:
                    upd_dt = dt_accum
                    dt_accum = 0.0
                    x[idx] += vx[idx] * upd_dt
                    y[idx] += vy[idx] * upd_dt

                # Wall reflections
                left_mask = x[idx] <= r[idx]
                if left_mask.any():
                    x[idx][left_mask] = r[idx][left_mask]
                    vx[idx][left_mask] = np.abs(vx[idx][left_mask])
                right_mask = x[idx] >= (screen_width - r[idx])
                if right_mask.any():
                    x[idx][right_mask] = (screen_width - r[idx][right_mask])
                    vx[idx][right_mask] = -np.abs(vx[idx][right_mask])

                top_mask = y[idx] <= r[idx]
                if top_mask.any():
                    y[idx][top_mask] = r[idx][top_mask]
                    vy[idx][top_mask] = np.abs(vy[idx][top_mask])
                bottom_mask = y[idx] >= (screen_height - r[idx])
                if bottom_mask.any():
                    y[idx][bottom_mask] = (screen_height - r[idx][bottom_mask])
                    vy[idx][bottom_mask] = -np.abs(vy[idx][bottom_mask])

                # Form instances
                tx = (x[idx] - r[idx]).astype(np.int32)
                ty = (y[idx] - r[idx]).astype(np.int32)
                with overlay.instances_lock:
                    bi = overlay.back_instances
                    bi.extend([(sprite_key_list[i], tx[i], ty[i]) for i in range(ball_count)])

            # Fetch render FPS
            render_fps = overlay.get_render_fps()
            object_count = ball_count
            elapsed = time.time() - start_time

            # Check warmup completion (2-stage: warmup -> running)
            if not warmup_complete and time.time() - warmup_start_time >= warmup_time:
                warmup_complete = True
                # Reset FPS counters/timers so measurement starts clean
                frame_count = 0
                fps_update_time = time.time()
                last_stat_time = fps_update_time
                print(f"Warmup complete. Starting to add balls and collect stats...")

            # Render HUD (simplified using draw_text like case_03)
            if not disable_hud:
                # Panel background and border
                panel_w, panel_h = 300, 230
                overlay.draw_rect(10, 10, panel_w, panel_h, (0, 0, 0, 200))
                overlay.draw_rect(10, 10, panel_w, panel_h, (100, 100, 200, 255), thickness=2)

                # Text lines
                y_text = 20
                overlay.draw_text(20, y_text, f"Stage: {'RUNNING' if warmup_complete else f'WARMUP {max(0.0, warmup_time - (time.time() - warmup_start_time)):.1f}s'}",
                                  color=(230, 230, 255, 255), font_size=20); y_text += 28
                overlay.draw_text(20, y_text, f"Balls: {ball_count}", color=(255, 255, 255, 255), font_size=20); y_text += 28
                overlay.draw_text(20, y_text, f"Gen FPS: {gen_fps}", color=(100, 255, 100, 255), font_size=20); y_text += 28
                overlay.draw_text(20, y_text, f"Rend FPS: {render_fps}", color=(200, 200, 255, 255), font_size=20); y_text += 28
                overlay.draw_text(20, y_text, f"Objects: {object_count}", color=(255, 200, 100, 255), font_size=20); y_text += 28
                overlay.draw_text(20, y_text, f"Time: {elapsed:.1f}s", color=(200, 255, 200, 255), font_size=18); y_text += 26
                overlay.draw_text(20, y_text, f"Speed: {balls_per_second:.1f}/sec", color=(255, 220, 180, 255), font_size=18); y_text += 26
                if warmup_complete:
                    drop_rate = measurement_dropped_frames / max(measurement_total_frames, 1) * 100
                    drop_line = f"Dropped: {measurement_dropped_frames}/{measurement_total_frames} ({drop_rate:.1f}%)"
                else:
                    drop_line = "Dropped: —/— (—%)"
                overlay.draw_text(20, y_text, drop_line, color=(255, 180, 180, 255), font_size=18)

            # Signal render
            render_busy = getattr(overlay, 'render_event', None)
            if render_busy is not None and render_busy.is_set():
                dropped_frames += 1
                if warmup_complete:
                    measurement_dropped_frames += 1

            overlay.signal_render()

            # Wait next frame
            timer.wait_next_frame()

            # Accumulate and add balls
            if warmup_complete:
                accumulated_balls += balls_per_second * real_dt
                if render_fps >= critical_fps:
                    num_to_add = int(accumulated_balls)
                    if num_to_add > 0:
                        can_take = max(0, min(num_to_add, len(ball_pool) - pool_index))
                        if can_take > 0:
                            pool_index += can_take
                            ball_count += can_take
                            max_ball_count = max(max_ball_count, ball_count)
                            accumulated_balls -= can_take
                            ball_increment += 0.1
                            balls_per_second = ball_increment / increment_interval

            # Check stop condition
            if warmup_complete and render_fps < critical_fps and ball_count > initial_ball_count:
                print(f"FPS dropped below {critical_fps}. Stopping test.")
                break

            # Update generation FPS
            frame_count += 1
            current_time_fps = time.time()
            if current_time_fps - fps_update_time >= 1.0:
                gen_fps = frame_count
                frame_count = 0
                fps_update_time = current_time_fps

                # Collect history
                if warmup_complete:
                    gen_fps_history.append(gen_fps)
                    rend_fps_history.append(render_fps)
                    ball_count_history.append(ball_count)
                    times_history.append(elapsed)
                    min_gen_fps = min(min_gen_fps, gen_fps)
                    max_gen_fps = max(max_gen_fps, gen_fps)
                    min_rend_fps = min(min_rend_fps, render_fps)
                    max_rend_fps = max(max_rend_fps, render_fps)

            # Periodic statistics (only after warmup)
            if warmup_complete and current_time_fps - last_stat_time >= stat_interval:
                drop_rate = measurement_dropped_frames / max(measurement_total_frames, 1) * 100
                print(
                    f"Time: {elapsed:5.1f}s | Balls: {ball_count:4d} | Gen FPS: {gen_fps:2d} | Rend FPS: {render_fps:2d} | Drop: {drop_rate:4.1f}%")
                last_stat_time = current_time_fps

    except KeyboardInterrupt:
        print("Test interrupted by user.")
    finally:
        overlay.stop_layer()

        # Final statistics
        total_time = time.time() - start_time

        if gen_fps_history:
            avg_gen_fps = statistics.mean(gen_fps_history)
            median_gen_fps = statistics.median(gen_fps_history)
            stdev_gen_fps = statistics.stdev(gen_fps_history) if len(gen_fps_history) > 1 else 0
        else:
            avg_gen_fps = median_gen_fps = stdev_gen_fps = 0

        if rend_fps_history:
            avg_rend_fps = statistics.mean(rend_fps_history)
            median_rend_fps = statistics.median(rend_fps_history)
            stdev_rend_fps = statistics.stdev(rend_fps_history) if len(rend_fps_history) > 1 else 0
        else:
            avg_rend_fps = median_rend_fps = stdev_rend_fps = 0

        print("\n" + "=" * 60)
        print("FINAL BENCHMARK STATISTICS")
        print("=" * 60)
        print(f"PERFORMANCE:")
        print(f"  🎯 Max load: {max_ball_count:,} objects")
        print(f"  ⏱️  Total test time: {total_time:.1f} s")
        print(f"  🚀 Final rate: {balls_per_second:.0f} objects/sec")

        print(f"\n📊 FPS STATISTICS:")
        print(f"  Generation (Gen FPS):")
        print(f"    - Peak: {max_gen_fps} FPS")
        print(f"    - Minimum: {min_gen_fps} FPS")
        print(f"    - Stability: {stdev_gen_fps:.1f} σ")

        print(f"  Rendering (Rend FPS):")
        print(f"    - Peak: {max_rend_fps:.0f} FPS")
        print(f"    - Minimum: {min_rend_fps:.1f} FPS")
        print(f"    - Stability: {stdev_rend_fps:.1f} σ")

        print(f"\n⚡ RESULT:")
        if max_ball_count >= 5000:
            print(f"  ✅ EXCELLENT — {max_ball_count:,}+ objects with stable rendering!")
        elif max_ball_count >= 2000:
            print(f"  👍 GOOD — {max_ball_count:,} objects — high performance")
        else:
            print(f"  🔄 NORMAL — {max_ball_count:,} objects — standard load")

        if stdev_gen_fps > 0 and stdev_rend_fps > 0:
            stability_diff = stdev_gen_fps - stdev_rend_fps
            print(f"  📈 Rendering is more stable than generation by {stability_diff:.1f} σ")
        print("=" * 60)

        # Построение графиков
        if times_history and not disable_plot:
            plt.figure(figsize=(12, 8))

            ax1 = plt.subplot(2, 1, 1)
            l1, = ax1.plot(times_history, gen_fps_history, label='Gen FPS', color='green', linewidth=2)
            l2, = ax1.plot(times_history, rend_fps_history, label='Rend FPS', color='blue', linewidth=2)
            # Critical FPS markers
            ax1.axhline(y=critical_fps, color='red', linestyle='--', label=f'Critical FPS ({critical_fps})')
            # Subtle shaded band to emphasize under-critical region
            ax1.axhspan(0, critical_fps, color='red', alpha=0.06, zorder=0)
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('FPS')
            ax1.set_title('FPS and Ball count over time')
            ax1.grid(True, alpha=0.3)

            # Secondary y-axis for ball count on the same chart
            ax2 = ax1.twinx()
            l3, = ax2.plot(times_history, ball_count_history, label='Ball count', color='purple', linewidth=2, alpha=0.9)
            ax2.set_ylabel('Ball count', color='purple')
            ax2.tick_params(axis='y', labelcolor='purple')

            # Combined legend
            lines = [l1, l2, l3]
            labels = [ln.get_label() for ln in lines]
            ax1.legend(lines, labels, loc='upper right')

            # Ball count is now plotted on the secondary y-axis of the first subplot

            # Second subplot as a styled summary panel
            ax_text = plt.subplot(2, 1, 2)
            ax_text.axis('off')
            banner = os.getenv('BANNER_TEXT', '').strip()
            # Compute measured drop rate (after warmup)
            if 'measurement_total_frames' in locals() and measurement_total_frames > 0:
                measured_drop_rate = measurement_dropped_frames / measurement_total_frames * 100.0
                drop_line = f"Drop (measured): {measured_drop_rate:.1f}%  ({measurement_dropped_frames}/{measurement_total_frames})"
            else:
                measured_drop_rate = None
                drop_line = "Drop (measured): —"

            # Build multi-line summary
            lines = []
            title = f"{banner} — FINAL SUMMARY" if banner else "FINAL SUMMARY"
            lines.append(title)
            lines.append(f"Duration: {total_time:.1f}s  |  Target FPS: {target_fps:.0f}  |  Critical FPS: {critical_fps:.0f}")
            lines.append(drop_line)
            lines.append("")
            lines.append(f"Gen FPS  — avg: {statistics.mean(gen_fps_history):.1f}  med: {statistics.median(gen_fps_history):.1f} "
                         f"min: {min_gen_fps if min_gen_fps != float('inf') else 0:.0f}  max: {max_gen_fps:.0f}  σ: {stdev_gen_fps:.1f}")
            lines.append(f"Rend FPS — avg: {statistics.mean(rend_fps_history):.1f}  med: {statistics.median(rend_fps_history):.1f}  "
                         f"min: {min_rend_fps if min_rend_fps != float('inf') else 0:.1f}  max: {max_rend_fps:.0f}  σ: {stdev_rend_fps:.1f}")

            # Prominent headline for maximum objects
            headline = f"{max_ball_count:,}+ OBJECTS"
            # Big badge-like text near the top of the panel
            ax_text.text(0.5, 0.78, headline,
                         ha='center', va='center', fontsize=26, fontweight='bold', color='#ffd166',
                         bbox=dict(boxstyle='round,pad=0.6', facecolor=(0.1, 0.1, 0.1, 0.85), edgecolor=(0.7, 0.55, 0.2, 1), linewidth=2))

            text = "\n".join(lines)
            ax_text.text(0.5, 0.36, text,
                         ha='center', va='center', fontsize=13, color='#e6e6ff',
                         bbox=dict(boxstyle='round,pad=0.8', facecolor=(0, 0, 0, 0.6), edgecolor=(0.4, 0.4, 0.8, 1), linewidth=2))

            plt.tight_layout()
            plt.show()


if __name__ == "__main__":
    main()