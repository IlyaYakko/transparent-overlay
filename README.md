# Transparent Overlay

![Hero](https://raw.githubusercontent.com/IlyaYakko/transparent-overlay/main/assets/images/hero_placeholder.png)

[![PyPI version](https://img.shields.io/pypi/v/transparent-overlay.svg)](https://pypi.org/project/transparent-overlay/)
[![Python versions](https://img.shields.io/pypi/pyversions/transparent-overlay.svg)](https://pypi.org/project/transparent-overlay/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![OS: Windows](https://img.shields.io/badge/OS-Windows-0078D6)](#requirements)

High-performance transparent graphics overlay for Windows.  
True per-pixel transparency, double buffering, cached sprites, thread-safe render loop, and **automatic Numba
acceleration** (~10x faster rendering).

## Features

- True desktop transparency using layered windows (`UpdateLayeredWindow`)
- Smooth, flicker-free rendering with double buffering
- Cached sprites: shapes, lines, text, and custom NumPy RGBA arrays
- Thread-safe: separate logic and dedicated render thread
- Built-in diagnostics: FPS counter and per-frame statistics
- **Automatic Numba acceleration** (installed by default, with graceful NumPy fallback)

## Installation

```bash

pip install transparent-overlay

```

This installs the core library with **Numba included** for maximum performance (~10x faster rendering).

## Examples

The library comes with rich educational and practical examples demonstrating all features.

To run them:

```bash

pip install "transparent-overlay[examples]"

git clone https://github.com/IlyaYakko/transparent-overlay.git

cd transparent-overlay/examples && python education/education_01_basic_shapes.py

```

All examples and media assets are available in the [examples/
folder on GitHub](https://github.com/IlyaYakko/transparent-overlay/tree/main/examples).

**Note**: The face detection example automatically downloads the required Haar Cascade file on first run if needed.

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

- Real-time HUD overlays
- On-screen debugging for AI / computer vision applications
- Desktop widgets and transparent UI elements
- Streaming and recording overlays
- Graphics experiments and educational demos

## Documentation

- Full documentation: [DOCUMENTATION.md](https://github.com/IlyaYakko/transparent-overlay/blob/main/DOCUMENTATION.md)
- Examples and demos: [examples/
  folder on GitHub](https://github.com/IlyaYakko/transparent-overlay/tree/main/examples)
- Media assets (screenshots, GIFs, videos): [assets/
  folder on GitHub](https://github.com/IlyaYakko/transparent-overlay/tree/main/assets)

## Performance

The library automatically uses **Numba** for significantly faster pixel operations (up to 10x speedup).  
If Numba is unavailable for any reason, it seamlessly falls back to pure NumPy — functionality remains fully intact.

## Requirements

- **OS**: Windows 7 or later
- **Python**: 3.7 and above
- Hardware must support layered windows (all modern Windows systems do)

> Note: This package is Windows-only. Importing on other platforms will raise an error by design.

## License

[MIT License](LICENSE) — free for commercial and personal use.