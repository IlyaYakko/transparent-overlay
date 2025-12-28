"""
education_11_no_numba_fallback.py
Demonstration of running without Numba installed.

- Runs the performance benchmark twice: without Numba and with Numba.
- In the first run, the child process stubs the 'numba' module so fallback is used.
- Prints both results for comparison.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_benchmark_twice():
    """Run the benchmark twice: without Numba (fallback) and with Numba (if available)."""
    # Project root: transparent-overlay/
    root = Path(__file__).resolve().parents[2]
    # NOTE: Adjust the path below to the actual benchmark case if needed
    case_path = root / 'examples' / 'cases' / 'case_07_performance_benchmark.py'

    if not case_path.exists():
        print(f"Error: file not found: {case_path}")
        return

    py = sys.executable

    # Common ENV for both runs
    base_env = os.environ.copy()
    base_env.update({
        'CRITICAL_FPS': '10',
        'TARGET_FPS': '60',
        'INITIAL_BALLS': '10',
        'WARMUP': '2.0',
        'MAX_DURATION': '60',
        'DISABLE_PLOT': '0',  # enable plots to be displayed
        'DISABLE_HUD': '0',
        'HUD_UPDATE_INTERVAL': '0.2',
        'UPDATE_EVERY_N': '1',
        'PRECREATE_POOL': '50000',
        'PALETTE_SIZE': '32',
        'PYTHONIOENCODING': 'utf-8',
        'NO_EMOJI': '1',
    })

    # 1) Without Numba: stub 'numba' module
    print("\n" + "=" * 70)
    print("PERFORMANCE BENCHMARK — WITHOUT NUMBA")
    print("=" * 70)

    code_no_numba = f"""
import sys, types, runpy
# Replace 'numba' with an empty module so core switches to fallback
sys.modules['numba'] = types.ModuleType('numba')

# Small detector
try:
    import transparent_overlay.core as core
    try:
        import numba as _n
        numba_ver = getattr(_n, '__version__', 'stubbed')
    except Exception:
        numba_ver = 'not installed/stubbed'
    print('[DETECTOR] NUMBA_AVAILABLE in core = {{}} | numba = {{}}'.format(getattr(core, 'NUMBA_AVAILABLE', None), numba_ver))
except Exception as e:
    print('[DETECTOR] Failed to import core:', e)

runpy.run_path(r"{case_path}", run_name='__main__')
"""

    try:
        env_no = base_env.copy()
        env_no['BANNER_TEXT'] = 'WITHOUT NUMBA'
        res_no = subprocess.run(
            [py, '-c', code_no_numba],
            env=env_no,
            text=True,
            encoding='utf-8',
            errors='replace',
        )
        if res_no.returncode != 0:
            print("Run without Numba failed (code:", res_no.returncode, ")")
    except Exception as e:
        print("Exception during run without Numba:", e)

    # 2) With Numba (normal environment)
    print("\n" + "=" * 70)
    print("PERFORMANCE BENCHMARK — WITH NUMBA (if available)")
    print("=" * 70)

    code_with_numba = f"""
import runpy
try:
    import transparent_overlay.core as core
    try:
        import numba as _n
        numba_ver = getattr(_n, '__version__', 'unknown')
    except Exception:
        numba_ver = 'not installed'
    print('[DETECTOR] NUMBA_AVAILABLE in core = {{}} | numba = {{}}'.format(getattr(core, 'NUMBA_AVAILABLE', None), numba_ver))
except Exception as e:
    print('[DETECTOR] Failed to import core:', e)

runpy.run_path(r"{case_path}", run_name='__main__')
"""

    try:
        env_yes = base_env.copy()
        env_yes['BANNER_TEXT'] = 'WITH NUMBA'
        res_yes = subprocess.run(
            [py, '-c', code_with_numba],
            env=env_yes,
            text=True,
            encoding='utf-8',
            errors='replace',
        )
        if res_yes.returncode != 0:
            print("Run with Numba failed (code:", res_yes.returncode, ")")
    except Exception as e:
        print("Exception during run with Numba:", e)


if __name__ == "__main__":
    run_benchmark_twice()
