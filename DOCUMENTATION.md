# Transparent Overlay — Full Documentation

![Hero](https://raw.githubusercontent.com/IlyaYakko/transparent-overlay/main/assets/images/hero_placeholder.png)

### Media demos

All visual demos, screenshots, GIFs, and videos are stored in the repository:

👉 [**assets/** folder on GitHub](https://github.com/IlyaYakko/transparent-overlay/tree/main/assets)

- Screenshots: `assets/images/` (e.g., basic shapes, text rendering, transparency layers)
- Animated demos: `assets/gifs/` (e.g., fast rendering loop)
- Video overview & benchmarks: `assets/videos/` (e.g., performance benchmark)

Feel free to explore the folder for real examples and placeholders used in this documentation.
---

A high-performance library for creating transparent overlays on Windows with hardware-accelerated rendering and
thread-safety.

## 🚀 Features

- 🪟 True transparency — desktop fully visible through the layer
- ⚡ High performance — double buffering and UpdateLayeredWindow
- 🎨 Sprites — caching, instancing, premultiplied alpha
- 🧵 Thread-safe — separate logic and render threads
- 📐 Flexible — circles, rectangles, lines, text, custom NumPy sprites
- 📊 Diagnostics — FPS, statistics, sprite info

## 🛠 Technologies

- Windows API (win32gui, win32con) — layered transparent windows
- Pillow — sprite generation
- NumPy — pixel buffers
- threading + ctypes — low-level access and threading architecture

## 📦 Installation

```bash
pip install transparent-overlay
```

## ⚡ Quick start

```python
from transparent_overlay import Overlay

with Overlay() as overlay:
    overlay.draw_circle(200, 150, 50, (255, 0, 0, 180))
    overlay.draw_rect(350, 100, 120, 80, (0, 0, 255, 160))
    overlay.draw_line(500, 100, 650, 180, (0, 255, 0, 255), thickness=3)
    overlay.draw_text(400, 50, "Basic Shapes", color=(255, 255, 255, 255), font_size=50)

    overlay.signal_render()
    input("Press Enter to exit...")
```

Full example: [examples/education/education_01_basic_shapes.py](https://github.com/IlyaYakko/transparent-overlay/blob/main/examples/education/education_01_basic_shapes.py)

### Manual control

```python
from transparent_overlay import Overlay

overlay = Overlay()
overlay.start_layer()
try:
    overlay.draw_text(100, 100, "Hello from manual control", color=(255, 255, 255))
    overlay.signal_render()
    input("Press Enter to exit...")
finally:
    overlay.stop_layer()
```

More on both
approaches: [examples/education/education_04_context_and_manual.py](https://github.com/IlyaYakko/transparent-overlay/blob/main/examples/education/education_04_context_and_manual.py)

## 🎮 Layer control

### Create and configure

```python
# Fullscreen overlay
overlay = Overlay()

# Overlay in a specific region
overlay = Overlay(x=100, y=100, width=800, height=600)
```

### Start and stop

```python
overlay.start_layer()  # Start render thread
overlay.signal_render()  # Request a frame
overlay.stop_layer()  # Graceful stop
```

### Render control

```python
running = True
while running:
    overlay.frame_clear()  # Clear queue and back buffer
    # ... draw ...
    overlay.signal_render()  # Kick off rendering
    time.sleep(1 / 60)  # FPS control
```

## 🎨 Drawing methods

### draw_circle(x, y, radius, color, thickness)

Draws a circle centered at `(x, y)`.

```python
overlay.draw_circle(200, 200, 50, (255, 0, 0, 128))
overlay.draw_circle(300, 300, 30, (0, 255, 0), thickness=2)
```

### draw_rect(x, y, width, height, color, thickness)

Draws a rectangle with the top-left corner at `(x, y)`.

```python
overlay.draw_rect(100, 100, 200, 100, (255, 255, 0, 200))
overlay.draw_rect(150, 150, 50, 50, (255, 0, 255), thickness=1)
```

### draw_line(x1, y1, x2, y2, color, thickness)

Draws a line.

```python
overlay.draw_line(50, 50, 400, 300, (0, 255, 255, 255), thickness=3)
```

### draw_text(x, y, text, color, font_size, anchor, angle, highlight, bg_color, box_size, fit_text, align, valign)

Draws text with advanced positioning and formatting.

```python
# Simple text
overlay.draw_text(100, 100, "Hello World", color=(255, 255, 255))

# Text with background and centering
overlay.draw_text(
    x=400, y=300,
    text="Centered Text",
    color=(255, 255, 255),
    font_size=24,
    anchor="mm",  # centered on both axes
    highlight=True,  # background
    bg_color=(0, 0, 0, 180),
    box_size=(200, 100),
    align="center",
    valign="middle"
)

# Rotated and fit-to-box text
overlay.draw_text(
    x=500, y=200,
    text="Rotated & Scaled",
    angle=45,
    fit_text=True,
    box_size=(150, 50)
)
```

Full parameters —
see [examples/education/education_03_text_rendering.py](https://github.com/IlyaYakko/transparent-overlay/blob/main/examples/education/education_03_text_rendering.py).

## 🔧 Low-level methods

### Buffer and queue control

```python
overlay.frame_clear()  # Clear queue + back buffer
overlay.frame_clear_queue()  # Queue only
overlay.frame_clear_buffers('back')  # Back buffer only
overlay.frame_clear_buffers('front')  # Front buffer only
overlay.frame_clear_buffers('both')  # Both buffers
```

### Creating and managing sprites

#### Basic sprites

```python
# Create sprites (caching is automatic)
circle_key = overlay.create_circle_sprite(50, (255, 0, 0, 128))
rect_key = overlay.create_rect_sprite(100, 50, (0, 255, 0, 255))
line_key = overlay.create_line_sprite(0, 0, 100, 100, (0, 0, 255), thickness=2)  # returns key only
text_key = overlay.create_text_sprite("Hello", font_size=16, color=(255, 255, 255))

# Add sprite instances
overlay.add_sprite_instance(circle_key, 200, 200)
overlay.add_sprite_instance(rect_key, 300, 300)
overlay.add_sprite_instance(text_key, 400, 400)

# For lines it's simpler to use draw_line().
# If you need an instance, compute the offset (bbox with thickness):
half = 2 // 2
left = min(0, 100) - half
top = min(0, 100) - half
overlay.add_sprite_instance(line_key, left, top)
```

#### Custom sprites from NumPy

```python
import numpy as np

gradient = np.zeros((100, 100, 4), dtype=np.uint8)
for i in range(100):
    gradient[:, i, 0] = int(255 * i / 100)  # R
    gradient[:, i, 3] = 128  # A

gradient_key = ('gradient', 'blue_fade')
overlay.create_sprite_from_numpy(gradient, gradient_key)
overlay.add_sprite_instance(gradient_key, 500, 500)
```

Examples: [examples/education/education_05_sprite_management.py](https://github.com/IlyaYakko/transparent-overlay/blob/main/examples/education/education_05_sprite_management.py), [examples/education/education_08_advanced_sprites.py](https://github.com/IlyaYakko/transparent-overlay/blob/main/examples/education/education_08_advanced_sprites.py), [examples/education/education_09_custom_numpy_sprite.py](https://github.com/IlyaYakko/transparent-overlay/blob/main/examples/education/education_09_custom_numpy_sprite.py).

### Sprite cache management

```python
# Remove a specific sprite
overlay.sprite_remove(circle_key)

# Full cache clear
overlay.sprite_clear_cache()

# Sprite info
info = overlay.get_sprite_cache_info(text_key)
if info:
    print(f"Sprite size: {info['width']}x{info['height']}")
    print(f"Memory usage: {info['memory_bytes']} bytes")
```

### Cache and TTL (auto-cleanup)

The cache stores `np.ndarray` sprites, and last-used timestamps are tracked separately. TTL-based auto-cleanup is
enabled by default and runs automatically in the render loop.

Default settings (can be changed at runtime):

```python
overlay.sprite_ttl_seconds = 5.0  # time-to-live for unused sprites
overlay.ttl_cleanup_period_seconds = 3.0  # cleanup period inside render loop
overlay.enable_auto_ttl_cleanup = True  # enable auto-cleanup
```

Manual cleanup:

```python
removed = overlay.sprite_clear_expired(max_age=10.0)
overlay.sprite_clear_cache()
```

See example: [examples/education/education_10_ttl_cache_demo.py](https://github.com/IlyaYakko/transparent-overlay/blob/main/examples/education/education_10_ttl_cache_demo.py).

⚠ **Note:**
Auto-TTL cleanup runs periodically in the render loop.
It removes sprites that have not been used for a while (based on `sprite_ttl_seconds`).
This usually does not affect high-level drawing methods like `draw_circle`,
`draw_rect`, `draw_line`, or `draw_text`, because they automatically recreate or refresh
the required sprites on each call.

However, if you manually create custom sprites using `create_*_sprite()` or
`create_sprite_from_numpy()` and expect them to persist for long periods
(e.g., during user input pauses or static scenes), they may be removed by TTL.
In such cases, consider increasing `sprite_ttl_seconds` or disabling
`enable_auto_ttl_cleanup`.

## 📊 Diagnostics and statistics

```python
fps = overlay.get_render_fps()
count = overlay.get_object_count()
stats_text, detailed_items = overlay.get_render_statistics()
sprite_info = overlay.get_sprite_cache_info(sprite_key)
```

Usage
example: [examples/education/education_05_sprite_management.py](https://github.com/IlyaYakko/transparent-overlay/blob/main/examples/education/education_05_sprite_management.py).

## 🧾 Logging

The library provides detailed, production-grade logging with appropriate levels. A modular logger with `NullHandler` is
used, so output appears when you configure logging in your application or test runner.

- INFO
    - Lifecycle messages (e.g., repeated `start_layer()` ignored)
    - TTL cleanup summary (how many sprites were removed)
- WARNING (logged once per unique cause)
    - Invalid `box_size` in text rendering (falls back to auto-sized text)
    - Invalid text `anchor` (falls back to `'lt'`)
    - Sprite missing in cache during render (skipped)
    - Sprite fully outside the screen (skipped)
    - Zero-length line (renders as a point)
- DEBUG
    - Color component clamping to 0..255 in `_normalize_color`
    - `signal_render()` called without a running render thread (throttled)
    - `sprite_remove` called for a non-existent key

Enable logs in your app:

```python
import logging

logging.basicConfig(level=logging.INFO)  # or DEBUG for more details
```

Pytest console logging is preconfigured in `pytest.ini`:

```
log_cli = true
log_cli_level = INFO
```

Override from CLI if needed, for example to see DEBUG:

```bash
pytest -q -o log_cli_level=DEBUG
```

Minimal logger
demo: [examples/education/education_12_logger_minimal_demo.py](https://github.com/IlyaYakko/transparent-overlay/blob/main/examples/education/education_12_logger_minimal_demo.py)
It shows lifecycle INFO messages and representative WARNING/DEBUG diagnostics (invalid anchor/box_size, off-screen and
missing sprites, color clamping, safe removal of non-existent sprite).

## ✅ Tests

Robustness and smoke tests cover import, API surface, lifecycle, cache/TTL, text edge cases, and concurrency.

- Test suite: [tests/test_robustness.py](https://github.com/IlyaYakko/transparent-overlay/blob/main/tests/test_robustness.py)
- Run with PowerShell (virtualenv recommended):

```powershell
.\.venv\Scripts\python.exe -m pytest -q
# Verbose logging
.\.venv\Scripts\python.exe -m pytest -q -o log_cli_level=DEBUG
```

Or with system Python:

```powershell
python -m pytest -q
python -m pytest -q -o log_cli_level=DEBUG
```

## 🏗️ Architecture

- **Platform and dependencies**
    - Windows-only (`sys.platform == 'win32'`), otherwise raises `ImportError`.
    - Uses `win32gui`, `win32con`, `ctypes` for window/rendering, `Pillow` for sprite generation, `NumPy` for buffers,
      optionally `Numba` for blit acceleration.

- **Window and layer**
    - Creates an invisible top-most layered window with flags:
      `WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOPMOST | WS_EX_NOACTIVATE`.
    - Rendering happens in memory (Memory DC + DIB sections). Publishing to the window uses `UpdateLayeredWindow` with
      `BLENDFUNCTION` (layer fully opaque, per-pixel alpha).

- **Double-buffered pixels**
    - Two same-sized DIB sections: `bitmap_front` and `bitmap_back`, directly mapped to BGRA `np.ndarray` (8 bits per
      channel).
    - Each frame: draw into `back_buf`, then atomically swap buffers (`front_buf <-> back_buf`) and publish via
      `UpdateLayeredWindow`.
    - Clear flags allow clearing `back`, `front`, or both at frame start: `frame_clear_buffers('back'|'front'|'both')`.

- **Instance queue (frame objects)**
    - Two queues: `back_instances` and `front_instances`. You push into `back_instances`.
    - `signal_render()` atomically swaps the queues and signals the render thread to start a frame.
    - Each queue item is a tuple `(sprite_key, x, y)`.

- **Threads and synchronization**
    - Your thread: calls API (`draw_*`, sprite creation, `signal_render()`, etc.).
    - Render thread: `_render_loop()` in `Thread(daemon=True)`, waits on `render_event`, then renders a frame and
      publishes it.
    - Separate `Lock`s are used for: buffers (`buf_lock`), queues (`instances_lock`), sprite cache (`sprite_lock`),
      FPS/object counters.

- **Sprite cache and TTL**
    - Key → `np.ndarray` (premultiplied BGRA). Last-used time stored separately.
    - TTL auto-cleanup inside the render loop: `sprite_ttl_seconds`, `ttl_cleanup_period_seconds`,
      `enable_auto_ttl_cleanup`.
    - Manual ops: `sprite_remove()`, `sprite_clear_cache()`, `sprite_clear_expired()`.

- **Sprite generation**
    - High-level: `draw_circle`, `draw_rect`, `draw_line`, `draw_text`.
        - Internally create/reuse a sprite (`create_*_sprite`) and enqueue an instance.
        - For lines, the instance offset accounts for thickness.
    - Low-level: `create_circle_sprite`, `create_rect_sprite`, `create_line_sprite`, `create_text_sprite`,
      `create_sprite_from_numpy`.
    - All cached sprites use premultiplied alpha and BGRA channels (compatible with GDI/`UpdateLayeredWindow`).

- **Text and layout**
    - `create_text_sprite()` supports: `font_size`, `angle`, `highlight`, `bg_color`, `box_size`, `fit_text`, `align`,
      `valign`, `font_path`.
    - `draw_text()` applies anchors (`lt, mt, rt, lm, mm, rm, lb, mb, rb`) and enqueues an instance at computed
      coordinates.

- **Blending and blit**
    - Core op: `_blit_sprite_into_buf` — premultiplied alpha compositing (source-over) with clipping.
    - If `Numba` is available, uses JIT-accelerated version; otherwise vectorized `NumPy` fallback.

- **Diagnostics and metrics**
    - Render FPS measured in `_render_loop`, available via `get_render_fps()`.
    - Object count available via `get_object_count()`.
    - `get_render_statistics()` returns a summary and detailed instance bboxes; `get_sprite_cache_info()` returns info
      for a specific sprite.

- **Lifecycle and safety**
    - Methods: `start_layer()`, `stop_layer()`, context manager (`__enter__/__exit__`), safe `close()`, and defensive
      `__del__`.
    - On shutdown: proper GDI resource release (DC, bitmaps), window destroy, and thread stop.

- **Error handling and logging**
    - Modular logger with `NullHandler` — no logs without your configuration.
    - Lack of Numba is non-critical — fallback is used.

### Diagrams

![Overlay Render Pipeline](https://raw.githubusercontent.com/IlyaYakko/transparent-overlay/main/assets/images/overlay_render_pipeline.png)
The overlay render pipeline shows how your thread enqueues draw calls and sprite instances, and how the render thread swaps buffers, composites sprites, updates the layered window, and maintains the sprite cache with TTL cleanup.

## ⚡ Performance

Key optimizations:

- Numba JIT (optional) — speeds up pixel ops
- Sprite caching
- Minimal locking
- Clipping to the visible area

If Numba is not available, a “slow mode” is used with a warning in logs. The library continues to work.

## 🧭 Repository structure

```text
📁 transparent-overlay — project root
├── 📁 assets — media assets for README and demos
│   ├── 📁 gifs
│   ├── 📁 images
│   └── 📁 videos
├── 📁 examples — usage examples
│   ├── 📁 cases — practical cases (mini apps)
│   │   ├── 📄 case_01_mouse_tracker.py
│   │   ├── 📄 case_02_eye_break_timer.py
│   │   ├── 📄 case_03_bouncing_balls.py
│   │   ├── 📄 case_04_performance_monitor.py
│   │   ├── 📄 case_05_magnifier_fisheye.py
│   │   ├── 📄 case_06_cannon_game.py
│   │   ├── 📄 case_07_performance_benchmark.py
│   │   ├── 📄 case_08_brightness_controller.py
│   │   └── 📄 case_09_face_detection_demo.py
│   └── 📁 education — step-by-step educational examples
│       ├── 📄 education_01_basic_shapes.py
│       ├── 📄 education_02_transparency_layers.py
│       ├── 📄 education_03_text_rendering.py
│       ├── 📄 education_04_context_and_manual.py
│       ├── 📄 education_05_sprite_management.py
│       ├── 📄 education_06_dynamic_text_sizing.py
│       ├── 📄 education_07_clear_methods_demo.py
│       ├── 📄 education_08_advanced_sprites.py
│       ├── 📄 education_09_custom_numpy_sprite.py
│       ├── 📄 education_10_ttl_cache_demo.py
│       └── 📄 education_11_no_numba_fallback.py
│       └── 📄 education_12_logger_minimal_demo.py
├── 📁 tests — project tests
│   └── 📄 test_robustness.py — import/smoke + robustness/error handling
├── 📁 transparent_overlay — library source code
│   ├── 📄 core.py — main module: window layer, render loop, buffers, sprites, text
│   └── 📄 __init__.py — public API (exports)
├── 📄 LICENSE — project license (MIT)
├── 📄 MANIFEST.in — package data and non-Python files to include in distribution
├── 📄 pyproject.toml — package metadata, build and dependencies
├── 📄 pytest.ini — pytest configuration
├── 📄 README.md — documentation and examples
├── 📄 requirements.txt — dependencies (dev/examples)
└── 📄 setup.py — package build/install script
```

## 🔧 Requirements

- OS: Windows 7+
- Python: 3.7–3.13
- Dependencies: pywin32, numpy, Pillow
- Optional: numba (blit acceleration); when absent, fallback is used

## 📄 License

MIT License

---
Transparent Overlay is a fast and convenient tool for building overlay applications — from utilities to visualizations.
🚀


