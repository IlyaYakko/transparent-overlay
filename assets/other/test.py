from transparent_overlay import Overlay
import time

# ----------------------------------------
# Constants
# ----------------------------------------
ANCHORS = [
    'lt', 'mt', 'rt',
    'lm', 'mm', 'rm',
    'lb', 'mb', 'rb',
]


# Какие спрайты выводить в метадату


# ----------------------------------------
# Helpers
# ----------------------------------------
def mark_point(overlay, x, y, color=(255, 0, 0, 255)):
    overlay.draw_circle(x, y, 1, (255, 255, 255, 255), thickness=0)
    overlay.draw_circle(x, y, 3, color, thickness=2)


# ----------------------------------------
# 1) Anchor grid test
# ----------------------------------------
def draw_anchor_grid(overlay, cx, cy, angle):
    overlay.draw_text(
        cx, cy - 220,
        f"ANCHOR GRID — {angle}°",
        font_size=36,
        anchor="mm",
        color=(255, 255, 255, 255)
    )

    for i, anchor in enumerate(ANCHORS):
        gx = cx + (i % 3) * 240 - 240
        gy = cy + (i // 3) * 160 - 160

        mark_point(overlay, gx, gy, (255, 80, 80, 255))

        overlay.draw_text(
            x=gx,
            y=gy,
            text=f"{anchor}\n{angle}°",
            highlight=True,
            anchor=anchor,
            font_size=28,
            color=(255, 255, 255, 255),
            angle=angle,
            bg_color=(0, 200, 0, 180),
        )


# ----------------------------------------
# 2) Sweep rotation test
# ----------------------------------------
def draw_rotation_sweep(overlay, x0, y0):
    overlay.draw_text(
        x0 + 650,
        y0 - 60,
        "ANGLE SWEEP (0°-360°, step=30°)",
        font_size=32,
        anchor="mm",
        color=(255, 255, 255, 255)
    )

    angles = list(range(0, 360, 30)) + [360]
    overlay.draw_line(x0, y0, x0 + len(angles) * 120, y0, (255, 80, 80, 200))

    for i, a in enumerate(angles):
        x = x0 + i * 120
        mark_point(overlay, x, y0, (255, 150, 0, 255))

        overlay.draw_text(
            x, y0,
            f"{a}°",
            anchor="mm",
            highlight=True,
            bg_color=(50, 50, 50, 180),
            color=(255, 255, 255, 255),
            font_size=26,
            angle=a
        )


# ----------------------------------------
# MASTER
# ----------------------------------------
def run_all_tests():
    with Overlay() as overlay:
        # ------------------------------------
        # SCENE 1 — Anchor Grid (0°)
        # ------------------------------------
        draw_anchor_grid(overlay, 600, 350, 0)

        # ------------------------------------
        # SCENE 2 — Anchor Grid (45°)
        # ------------------------------------
        draw_anchor_grid(overlay, 1500, 350, 45)

        # ------------------------------------
        # SCENE 3 — Angle Sweep
        # ------------------------------------
        draw_rotation_sweep(overlay, 100, 900)

        overlay.signal_render()
        print("Показаны все три сцены сразу.")
        input("Нажми Enter для выхода...")


if __name__ == "__main__":
    run_all_tests()
