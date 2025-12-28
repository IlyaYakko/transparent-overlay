"""
test_robustness.py
Robustness and import/smoke tests for transparent_overlay

Shows:
- Import and API surface checks
- Lifecycle and thread-safety scenarios
- Sprite cache and TTL behavior
- Text rendering edge cases (anchors, box_size)
- Off-screen/missing sprite handling and logging
- Concurrency signal/render patterns
- Basic drawing primitives behavior
"""

#!/ PowerShell: run tests locally
#
# Using project virtualenv (recommended):
#   .\.venv\Scripts\python.exe -m pytest -q
#   .\.venv\Scripts\python.exe -m pytest -q -o log_cli_level=DEBUG
#
# Using system Python (if venv is not used):
#   python -m pytest -q
#   python -m pytest -q -o log_cli_level=DEBUG

import sys
import time
import threading
import importlib

import pytest

# Skip all tests in this module on non-Windows platforms
pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Overlay requires Windows (win32)")

from transparent_overlay import Overlay
import numpy as np


# ---- Imported from test_import.py ----
def test_import_and_version():
    mod = importlib.import_module('transparent_overlay')
    assert hasattr(mod, 'Overlay')
    assert hasattr(mod, '__version__')


def test_overlay_smoke_methods():
    # Do not start graphics in tests, only check that public API surface exists
    from transparent_overlay import Overlay as _Overlay
    o = _Overlay  # class reference, do not instantiate for safety
    for name in (
        'draw_circle', 'draw_rect', 'draw_line', 'draw_text',
        'start_layer', 'stop_layer', 'signal_render',
        'create_sprite_from_numpy', 'sprite_clear_cache', 'sprite_clear_expired',
    ):
        assert hasattr(o, name), f"method {name} not found on Overlay class"


def _short_wait_render(ov: Overlay, frames: int = 2, delay: float = 0.02):
    """Helper: poke render loop a few times to flush pending work."""
    for _ in range(frames):
        ov.signal_render()
        time.sleep(delay)


def test_start_stop_idempotent():
    ov = Overlay(width=64, height=64)
    # Multiple starts should not crash
    ov.start_layer()
    ov.start_layer()

    _short_wait_render(ov)

    # Multiple stops should be safe
    ov.stop_layer()
    ov.stop_layer()

    # close() should be safe and idempotent
    ov.close()
    ov.close()

def test_sprite_remove_missing_key_no_crash():
    with Overlay(width=32, height=32) as ov:
        assert ov.sprite_remove(("nonexistent", 123)) is False


def test_get_sprite_cache_info_unknown_key_returns_none():
    with Overlay(width=32, height=32) as ov:
        assert ov.get_sprite_cache_info(("nonexistent", 456)) is None


def test_get_render_statistics_resilient():
    with Overlay(width=64, height=64) as ov:
        # Без объектов
        stats, items = ov.get_render_statistics()
        assert "Total instances" in stats
        assert isinstance(items, list)

        # Добавим объект и проверим
        key = ov.create_rect_sprite(5, 5, (255, 0, 0, 255))
        ov.add_sprite_instance(key, 1, 1)
        # Перед сигналом список ещё в back_instances; статистика смотрит на front_instances
        s2, items2 = ov.get_render_statistics()
        assert isinstance(items2, list)


def test_repeated_frame_clear_usage():
    with Overlay(width=64, height=64) as ov:
        for _ in range(5):
            ov.frame_clear()
            ov.draw_rect(0, 0, 10, 10, (255, 255, 255, 255))
            ov.signal_render()
            time.sleep(0.01)


def test_draw_text_invalid_anchor_no_crash():
    with Overlay(width=128, height=64) as ov:
        ov.draw_text(10, 10, "abc", anchor="bad_anchor_value")
        _short_wait_render(ov)


def test_multiple_signal_without_start_stop():
    ov = Overlay(width=32, height=32)
    for _ in range(10):
        ov.signal_render()
    ov.close()


def test_invalid_constructor_dimensions():
    # Width/height must be positive
    with pytest.raises(ValueError):
        Overlay(width=0, height=10)
    with pytest.raises(ValueError):
        Overlay(width=10, height=0)
    with pytest.raises(ValueError):
        Overlay(width=-1, height=-1)


def test_text_fit_zero_box_no_crash():
    with Overlay(width=128, height=128) as ov:
        # box_size=(0,0) and fit_text=True previously could cause div-by-zero
        key = ov.create_text_sprite(
            text="Hello",
            font_size=16,
            color=(255, 255, 255, 255),
            box_size=(0, 0),
            fit_text=True,
        )
        # Should return a key and allow cache lookup without crashing
        arr = ov._cache_get(key, update_ts=False)
        assert key is not None
        # It may be None if Pillow returns degenerate size; must not crash
        # Ensure render loop survives a frame regardless
        _short_wait_render(ov)


def test_sprite_from_numpy_invalid_shape_logs(caplog):
    caplog.set_level("ERROR")
    with Overlay(width=64, height=64) as ov:
        bad = np.zeros((10, 10, 3), dtype=np.uint8)  # missing alpha channel
        res = ov.create_sprite_from_numpy(bad, ("custom", "bad"))
        assert res is None
        # An error should be logged
        assert any("Error creating sprite from array" in rec.message for rec in caplog.records)


def test_negative_coordinates_no_crash():
    with Overlay(width=128, height=128) as ov:
        ov.frame_clear()  # пользовательская семантика: чистим перед кадром
        ov.draw_rect(-10, -10, 20, 20, (255, 0, 0, 128))
        ov.draw_circle(-5, -5, 10, (0, 255, 0, 128))
        ov.draw_line(-20, -20, 10, 10, (0, 0, 255, 128), thickness=3)
        _short_wait_render(ov)


def test_signal_render_concurrent_no_crash():
    with Overlay(width=128, height=128) as ov:
        stop = threading.Event()

        def producer():
            i = 0
            while not stop.is_set():
                ov.add_sprite_instance(ov.create_rect_sprite(5, 5, (255, 255, 255, 255)), i % 100, i % 100)
                i += 1

        def signaller():
            while not stop.is_set():
                ov.signal_render()
                time.sleep(0.001)

        t1 = threading.Thread(target=producer)
        t2 = threading.Thread(target=signaller)
        t1.start(); t2.start()
        time.sleep(0.1)
        stop.set()
        t1.join(timeout=1)
        t2.join(timeout=1)
        # If we are here, no exceptions were raised and threads exited cleanly


def test_start_signal_stop_wrong_order_no_crash():
    # Call methods in weird order to ensure graceful handling
    ov = Overlay(width=64, height=64)
    # Signal before start
    ov.signal_render()
    # Add sprite before start
    ov.add_sprite_instance(ov.create_rect_sprite(4, 4, (255, 255, 255, 255)), 0, 0)
    # Now start
    ov.start_layer()
    _short_wait_render(ov)
    # Stop and signal again
    ov.stop_layer()
    ov.signal_render()
    # Close multiple times
    ov.close()
    ov.close()
