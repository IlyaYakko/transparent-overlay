"""
case_06_cannon_game.py
Automatic cannon — physics and heating effects

Demonstrates:
- Particle system with gravity and bounces
- Dynamic metal heating effects
- Color gradients for temperature visualization
- Complex collision physics
"""

import transparent_overlay
import time
import random
import math
from win32api import GetCursorPos


class Bullet:
    def __init__(
        self,
        screen_width,
        screen_height,
        border_thickness,
        angle_rad: float | None = None,
        spawn_x: float | None = None,
        spawn_y: float | None = None,
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.border_thickness = border_thickness

        self.radius = random.randint(3, 8)
        # Starting position — from muzzle if provided; otherwise bottom center
        self.x = int(spawn_x) if spawn_x is not None else screen_width // 2
        self.y = int(spawn_y) if spawn_y is not None else screen_height - border_thickness - 30

        speed = random.uniform(2500, 3000)
        if angle_rad is None:
            angle_degrees = max(50, min(130, int(random.gauss(90, 10))))
            angle_radians = math.radians(angle_degrees)
        else:
            angle_radians = angle_rad
        self.vx = speed * math.cos(angle_radians)
        self.vy = -speed * math.sin(angle_radians)

        color_intensity = min(speed / 2500, 1.0)
        self.color = (
            int(255 * color_intensity),
            int(255 * (1 - color_intensity)),
            0,
            255
        )

        self.active = True

    def update(self, dt):
        if not self.active:
            return False, None, self.x, self.y

        old_x, old_y = self.x, self.y

        self.x = int(self.x + self.vx * dt)
        self.y = int(self.y + self.vy * dt)
        self.vy += 500 * dt

        collision_occurred = False
        border_side = None

        if self.y <= self.border_thickness + self.radius:
            self.y = self.border_thickness + self.radius
            self.vy = abs(self.vy) * 0.2
            self.vx *= 0.6
            collision_occurred = True
            border_side = 'top'

            if abs(self.vx) < 20 and abs(self.vy) < 20:
                self.active = False

        if (self.x < -100 or self.x > self.screen_width + 100 or
                self.y > self.screen_height + 100):
            self.active = False

        return collision_occurred, border_side, old_x, old_y


class Cannon:
    def __init__(self, screen_width, screen_height, border_thickness):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.border_thickness = border_thickness
        self.x = screen_width // 2
        self.y = screen_height - border_thickness - 20
        self.width = 50
        self.height = 30
        # Barrel tilt constraints (degrees relative to +X)
        # 0° — right, 90° — up. Limit to the upper sector for this cannon.
        self.min_angle_deg = 50
        self.max_angle_deg = 130

    def get_clamped_angle_rad(self, cursor_x: int, cursor_y: int) -> float:
        """Return the barrel angle (radians) towards cursor, clamped by limits."""
        dx = cursor_x - self.x
        dy = self.y - cursor_y  # invert Y
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        clamped_deg = max(self.min_angle_deg, min(self.max_angle_deg, angle_deg))
        return math.radians(clamped_deg)

    def draw(self, overlay, cursor_x: int, cursor_y: int) -> None:
        """Draw the cannon: body and a barrel clamped towards cursor."""
        # Body (static rectangle)
        overlay.draw_rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height,
            (120, 120, 120, 255),
        )

        # Вычисляем ограниченный угол
        clamped_rad = self.get_clamped_angle_rad(cursor_x, cursor_y)

        # Barrel length and rendering at angle
        barrel_length = 40
        end_x = self.x + int(math.cos(clamped_rad) * barrel_length)
        end_y = self.y - int(math.sin(clamped_rad) * barrel_length)
        overlay.draw_line(self.x, self.y, end_x, end_y, (90, 90, 90, 255), 12)


class BorderHeatingSystem:
    def __init__(self, screen_width, screen_height, border_thickness=20):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.border_thickness = border_thickness
        self.top_heating = {}
        self.cooling_rate = 40

    def add_impact(self, bullet, border_side, old_x, old_y):
        if not bullet.active or border_side != 'top':
            return

        speed = math.sqrt(bullet.vx ** 2 + bullet.vy ** 2)
        mass = bullet.radius
        impact_energy = speed * mass / 30

        pos_key = int(bullet.x)
        spread_radius = int(bullet.radius * 4)

        for offset in range(-spread_radius, spread_radius + 1):
            current_pos = pos_key + offset

            if current_pos < 0 or current_pos >= self.screen_width:
                continue

            distance_factor = 1.0 - abs(offset) / (spread_radius + 1)
            heat_to_add = impact_energy * distance_factor

            if current_pos in self.top_heating:
                self.top_heating[current_pos] += heat_to_add
            else:
                self.top_heating[current_pos] = heat_to_add

            if current_pos in self.top_heating:
                self.top_heating[current_pos] = min(self.top_heating[current_pos], 2000)

    def update(self, dt):
        keys_to_remove = []
        for pos, heat in self.top_heating.items():
            new_heat = heat - self.cooling_rate * dt
            if new_heat <= 0:
                keys_to_remove.append(pos)
            else:
                self.top_heating[pos] = new_heat

        for pos in keys_to_remove:
            del self.top_heating[pos]

    def get_heat_color(self, heat_value):
        if heat_value <= 0:
            return (0, 0, 0, 0)

        normalized_heat = min(heat_value / 2000.0, 1.0)

        if normalized_heat < 0.2:
            t = normalized_heat / 0.2
            alpha = int(200 * t)
            return (int(120 * t), 0, 0, alpha)
        elif normalized_heat < 0.4:
            t = (normalized_heat - 0.2) / 0.2
            alpha = int(200 + 55 * t)
            return (int(120 + 135 * t), 0, 0, alpha)
        elif normalized_heat < 0.6:
            t = (normalized_heat - 0.4) / 0.2
            alpha = 255
            return (255, int(80 * t), 0, alpha)
        elif normalized_heat < 0.8:
            t = (normalized_heat - 0.6) / 0.2
            alpha = 255
            return (255, int(80 + 175 * t), 0, alpha)
        else:
            t = (normalized_heat - 0.8) / 0.2
            alpha = 255
            return (255, 255, int(255 * t), alpha)

    def draw_heated_borders(self, overlay):
        for x, heat in self.top_heating.items():
            color = self.get_heat_color(heat)
            if color[3] > 0:
                overlay.draw_line(x, 0, x, self.border_thickness, color, 3)

    def draw_border_outlines(self, overlay):
        border_color = (70, 70, 70, 255)
        overlay.draw_line(0, self.border_thickness // 2,
                        self.screen_width, self.border_thickness // 2,
                        border_color, self.border_thickness)


def main():
    target_fps = 60
    duration = 30

    overlay = transparent_overlay.Overlay()
    overlay.start_layer()

    screen_width = overlay.width
    screen_height = overlay.height
    border_thickness = 25

    cannon = Cannon(screen_width, screen_height, border_thickness)
    bullets = []
    max_bullets = 150
    heating_system = BorderHeatingSystem(screen_width, screen_height, border_thickness)

    last_shot_time = 0
    shot_interval = 0.05

    frame_count = 0
    gen_fps = 0
    fps_update_time = time.time()
    start_time = time.time()
    last_frame_time = time.perf_counter()
    shots_fired = 0

    print("Automatic cannon firing bullets at the wall!")

    try:
        while time.time() - start_time < duration:
            frame_start = time.perf_counter()
            real_dt = frame_start - last_frame_time
            last_frame_time = frame_start

            # Automatic shooting
            current_time = time.time()
            if current_time - last_shot_time > shot_interval and len(bullets) < max_bullets:
                # Get barrel angle and muzzle position as spawn point
                cur_x, cur_y = GetCursorPos()
                base_angle_rad = cannon.get_clamped_angle_rad(cur_x, cur_y)
                # Small gaussian spread (degrees), then clamp
                spread_deg = 2.0
                angle_deg = math.degrees(base_angle_rad) + random.gauss(0.0, spread_deg)
                angle_deg = max(cannon.min_angle_deg, min(cannon.max_angle_deg, angle_deg))
                angle_rad = math.radians(angle_deg)

                barrel_length = 40
                muzzle_x = cannon.x + math.cos(angle_rad) * barrel_length
                muzzle_y = cannon.y - math.sin(angle_rad) * barrel_length

                bullets.append(
                    Bullet(
                        screen_width,
                        screen_height,
                        border_thickness,
                        angle_rad=angle_rad,
                        spawn_x=muzzle_x,
                        spawn_y=muzzle_y,
                    )
                )
                last_shot_time = current_time
                shots_fired += 1

            overlay.frame_clear()

            heating_system.draw_border_outlines(overlay)

            active_bullets = 0
            for bullet in bullets[:]:
                collision_occurred, border_side, old_x, old_y = bullet.update(real_dt)

                if bullet.active:
                    active_bullets += 1
                    overlay.draw_circle(int(bullet.x), int(bullet.y), bullet.radius, bullet.color)

                    if collision_occurred and border_side:
                        heating_system.add_impact(bullet, border_side, old_x, old_y)
                else:
                    bullets.remove(bullet)

            heating_system.update(real_dt)
            heating_system.draw_heated_borders(overlay)

            # Tilt barrel towards cursor (with clamp) and draw visual ray
            cur_x, cur_y = GetCursorPos()
            clamped_angle = cannon.get_clamped_angle_rad(cur_x, cur_y)
            cannon.draw(overlay, cur_x, cur_y)

            # Наклоняем ствол в сторону курсора (с ограничением по углу)
            cur_x, cur_y = GetCursorPos()
            cannon.draw(overlay, cur_x, cur_y)

            # Info panel
            overlay.draw_rect(10, border_thickness + 10, 150, 100, (0, 0, 0, 180))

            overlay.draw_text(20, border_thickness + 15, f"Bullets: {active_bullets}/{max_bullets}",
                            color=(255, 255, 255, 255), font_size=14)
            overlay.draw_text(20, border_thickness + 35, f"Shots: {shots_fired}",
                            color=(255, 255, 255, 255), font_size=14)
            overlay.draw_text(20, border_thickness + 55, f"Gen FPS: {gen_fps}",
                            color=(100, 255, 100, 255), font_size=14)

            render_fps = overlay.get_render_fps()
            overlay.draw_text(20, border_thickness + 75, f"Rend FPS: {render_fps}",
                            color=(200, 200, 255, 255), font_size=14)

            overlay.signal_render()

            # Контроль FPS
            frame_time = time.perf_counter() - frame_start
            sleep_time = (1.0 / target_fps) - frame_time
            if sleep_time > 0:
                time.sleep(sleep_time)

            frame_count += 1
            current_time = time.time()
            if current_time - fps_update_time >= 1.0:
                gen_fps = frame_count
                frame_count = 0
                fps_update_time = current_time

    except KeyboardInterrupt:
        pass
    finally:
        overlay.stop_layer()
        print(f"Simulation finished. Total shots: {shots_fired}")


if __name__ == "__main__":
    main()
