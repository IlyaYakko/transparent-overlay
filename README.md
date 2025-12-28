# Transparent Overlay

![Hero](https://raw.githubusercontent.com/IlyaYakko/transparent-overlay/main/assets/images/hero_placeholder.png)

[![PyPI version](https://img.shields.io/pypi/v/transparent-overlay.svg)](https://pypi.org/project/transparent-overlay/)
[![Python versions](https://img.shields.io/pypi/pyversions/transparent-overlay.svg)](https://pypi.org/project/transparent-overlay/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![OS: Windows](https://img.shields.io/badge/OS-Windows-0078D6)](#requirements)

High-performance transparent graphics overlay for Windows.  
True per-pixel transparency, double buffering, cached sprites, thread-safe render loop, and optional Numba acceleration.

## Features

- True desktop transparency using layered windows (UpdateLayeredWindow)
- Smooth, flicker-free rendering with double buffering
- Cached sprites: shapes, lines, text, and custom NumPy RGBA
- Thread-safe: logic thread + dedicated render thread
- Built-in diagnostics: FPS and per-frame statistics
- Optional Numba speedup package

## Installation

Basic:

```bash
pip install transparent-overlay
````

With acceleration:

```bash
pip install "transparent-overlay[speedup]"
```

Examples:

```bash
pip install "transparent-overlay[examples]"
```

## Quick start

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

![Demo](https://raw.githubusercontent.com/IlyaYakko/transparent-overlay/main/assets/gifs/demo_basic_placeholder.gif)

## Use cases

* Real-time HUD overlays
* On-screen debugging for AI / CV applications
* Desktop widgets and transparent UI elements
* Stream/recording overlays
* Graphics experiments and educational demos

## Documentation

* Full documentation: [DOCUMENTATION.md](DOCUMENTATION.md)
* Examples: see the `examples/` folder

## Requirements

* OS: **Windows 7+**
* Python: **3.7–3.13**
* GPU/driver must support layered windows (all modern Windows systems do)

> Note: This package is Windows-only. On other platforms `import transparent_overlay` will fail by design.
