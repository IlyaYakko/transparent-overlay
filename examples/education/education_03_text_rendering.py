"""
education_03_text_rendering.py
Full text rendering demonstration

Demonstrates:
- All anchor positioning variants (anchor)
- Text rotation (angle)
- Text background/highlight (highlight)
- Auto fitting (fit_text)
- Different fonts (font_path)
"""

import time
import os
import transparent_overlay

# === Overlay setup ===
overlay = transparent_overlay.Overlay()
overlay.start_layer()


# === Helper functions ===
def mark_point(x, y, color=(255, 0, 0, 255)):
    """Draws a small cross at a given point."""
    size = 5
    overlay.draw_line(x - size, y, x + size, y, color, thickness=2)
    overlay.draw_line(x, y - size, x, y + size, color, thickness=2)


def draw_box(box, color=(0, 255, 255, 180)):
    """Outlines a rectangle (box = (x, y, w, h))."""
    x, y, w, h = box
    overlay.draw_rect(x, y, w, h, color, thickness=2)


def draw_test_section(title, x, y, width, height):
    """Draws a test rectangle and adds a title."""
    # Semi-transparent gray rectangle around the test
    overlay.draw_rect(x, y, width, height, (120, 120, 120, 180), thickness=1)

    # Test title
    overlay.draw_text(
        x + width // 2, y - 5,
        title,
        color=(200, 200, 100, 255),
        font_size=20,
        anchor="mb",
        highlight=True,
        bg_color=(0, 0, 0, 160)
    )


def test_header(bx: int, by: int) -> None:
    overlay.draw_text(
        bx, by,
        "Transparent Layer Alpha — Text Rendering Test Suite",
        color=(0, 200, 255, 255),
        font_size=32,
        anchor="mt",
        highlight=True,
        bg_color=(0, 0, 0, 160)
    )


def test_anchor(bx: int, by: int, w: int = 500, h: int = 400) -> None:
    draw_test_section("1. Anchor Positioning Test", bx, by, w, h)
    # grid of points inside the section
    cols = [0.1, 0.5, 0.9]
    rows = [0.125, 0.5, 0.875]
    names = [["lt", "mt", "rt"], ["lm", "mm", "rm"], ["lb", "mb", "rb"]]
    for ri, ry in enumerate(rows):
        for ci, rx in enumerate(cols):
            x = int(bx + rx * w)
            y = int(by + ry * h)
            anchor = names[ri][ci]
            overlay.draw_text(
                x, y,
                f"Anchor: {anchor}",
                color=(255, 255, 255, 255),
                font_size=22,
                anchor=anchor,
                highlight=True,
                bg_color=(0, 0, 0, 180)
            )
            mark_point(x, y)


def test_alpha(bx: int, by: int, w: int = 200, h: int = 340) -> None:
    draw_test_section("2. Alpha Transparency Test", bx, by, w, h)
    # vertical contrast bars
    overlay.draw_rect(bx + w - 140, by + 20, 50, 5 * 60, (255, 255, 255, 255))
    overlay.draw_rect(bx + w - 90, by + 20, 50, 5 * 60, (0, 0, 0, 255))
    for i, alpha in enumerate([10, 64, 128, 192, 255]):
        x = bx + w - 170
        y = by + 50 + i * 60
        mark_point(x, y, (255, 0, 0, 255))
        overlay.draw_text(
            x, y,
            f"Alpha {alpha}",
            color=(0, 255, 0, alpha),
            font_size=30,
            anchor="lm",
            highlight=True,
            bg_color=(0, 0, 0, alpha)
        )


def test_fit_text(bx: int, by: int, w: int = 940, h: int = 190) -> None:
    draw_test_section("3. Text Fitting Test", bx, by, w, h)
    boxes = [
        (bx + 20, by + 20, 250, 40),
        (bx + 320, by + 20, 250, 100),
        (bx + 620, by + 20, 300, 150),
    ]
    for i, box in enumerate(boxes):
        rx, ry, rw, rh = box
        overlay.draw_text(
            x=rx, y=ry,
            anchor='lt',
            text=f"Box {i + 1}",
            box_size=(rw, rh),
            fit_text=True,
            align="center",
            valign="middle",
            color=(255, 255, 0, 255),
            highlight=True,
            bg_color=(0, 0, 0, 180)
        )
        draw_box((rx, ry, rw, rh))
        mark_point(rx, ry)


def test_fonts(bx: int, by: int, w: int = 900) -> None:
    # collect available fonts
    candidate_fonts = [
        ("Arial", r"C:\\Windows\\Fonts\\arial.ttf"),
        ("Segoe UI", r"C:\\Windows\\Fonts\\segoeui.ttf"),
        ("Consolas", r"C:\\Windows\\Fonts\\consola.ttf"),
        ("Impact", r"C:\\Windows\\Fonts\\impact.ttf"),
        ("Comic Sans MS", r"C:\\Windows\\Fonts\\comic.ttf"),
        ("Times New Roman", r"C:\\Windows\\Fonts\\times.ttf"),
        ("Gabriola", r"C:\\Windows\\Fonts\\Gabriola.ttf"),
    ]
    fonts_found = [(name, path) for name, path in candidate_fonts if os.path.exists(path)]
    line_h = 40
    min_section_h = 160
    inner_rows = max(1, len(fonts_found))
    inner_h = inner_rows * line_h + 40
    section_h = max(min_section_h, inner_h)
    # soft adjust by screen height if doesn't fit
    y = min(by, overlay.height - section_h - 20)
    y = max(60, y)
    draw_test_section("4. Different Fonts (font_path)", bx, y, w, section_h)
    fx, fy = bx + 30, y + 40
    if not fonts_found:
        overlay.draw_text(
            fx, fy,
            "Failed to find standard fonts under C:/Windows/Fonts",
            color=(255, 200, 200, 255),
            font_size=22,
            anchor="lt",
            highlight=True,
            bg_color=(60, 0, 0, 160)
        )
    else:
        for i, (name, path) in enumerate(fonts_found):
            overlay.draw_text(
                fx, fy + i * line_h,
                f"{name}: The quick brown fox jumps over the lazy dog 12345",
                color=(255, 255, 255, 255),
                font_size=26,
                anchor="lt",
                highlight=True,
                bg_color=(0, 0, 0, 160),
                font_path=path,
            )


def test_align_valign(bx: int, by: int, w: int = 700, h: int = 500) -> None:
    draw_test_section("5. Align & Valign Combinations", bx, by, w, h)
    # 3x3 grid
    overlay.draw_rect(bx + 50, by + 50, w - 100, h - 100, (80, 80, 80, 100), thickness=3)
    bbw, bbh = (w - 100), (h - 100)
    bbx, bby = bx + 50, by + 50
    cell_w = bbw // 3
    cell_h = bbh // 3
    for row in range(3):
        for col in range(3):
            cell_x = bbx + col * cell_w
            cell_y = bby + row * cell_h
            overlay.draw_rect(cell_x, cell_y, cell_w, cell_h, (120, 120, 120, 80), thickness=1)
            overlay.draw_line(cell_x, cell_y + cell_h // 2, cell_x + cell_w, cell_y + cell_h // 2,
                              (150, 150, 150, 60), thickness=1)
            overlay.draw_line(cell_x + cell_w // 2, cell_y, cell_x + cell_w // 2, cell_y + cell_h,
                              (150, 150, 150, 60), thickness=1)
            align = ["left", "center", "right"][col]
            valign = ["top", "middle", "bottom"][row]
            overlay.draw_text(
                x=cell_x + 5, y=cell_y + 5,
                anchor='lt',
                text=f"{align}\n{valign}",
                box_size=(cell_w - 10, cell_h - 10),
                fit_text=False,
                align=align,
                valign=valign,
                color=(255, 255, 255, 255),
                highlight=True,
                bg_color=(col * 40, row * 40, 100, 180),
                font_size=16
            )


def test_rotation(bx: int, by: int, w: int = 1820, h: int = 160) -> None:
    draw_test_section("6. Text Rotation Test", bx, by, w, h)
    angles = list(range(0, 360, 30)) + [360]
    x0, y0 = bx + 60, by + h // 2
    overlay.draw_line(x0, y0, x0 + (len(angles) - 1) * 140, y0, color=(255, 0, 0, 150))
    for i, a in enumerate(angles):
        x = x0 + i * 140
        y = y0
        overlay.draw_text(
            x, y,
            f"Angle {a}°",
            color=(255, 255, 255, 255),
            font_size=28,
            angle=a,
            anchor="mm",
            highlight=True,
            bg_color=(50, 50, 50, 180)
        )
        mark_point(x, y, (255, 150, 0, 255))


# === Layout: coordinates of all blocks in one place ===
layout = {
    "header": (overlay.width // 2, 20),  # uses anchor="mt"
    "anchor": (50, 80),
    "alpha": (650, 110),
    "fit": (900, 110),
    "fonts": (60, 520),
    "align_valign": (1100, 350),
    "rotation": (50, 870),

}

# Вызовы тестов
test_header(*layout["header"])  # заголовок без рамки
test_anchor(*layout["anchor"], 500, 400)
test_alpha(*layout["alpha"], 200, 340)
test_fit_text(*layout["fit"], 940, 190)
test_fonts(*layout["fonts"], 900)
test_align_valign(*layout["align_valign"], 700, 500)
test_rotation(*layout["rotation"], 1820, 160)

# === Sync and present ===
overlay.signal_render()
# === Viewing ===
try:
    input("Press Enter to exit...")
except KeyboardInterrupt:
    pass
finally:
    overlay.stop_layer()
