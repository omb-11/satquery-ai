"""
SatQuery AI — Dependency Verification Utility
Performs rapid pre-flight check of Python and Node dependencies.
Exits with 0 if all dependencies are satisfied so run.bat does not
waste time running `pip install` or `npm install` on every startup.
"""
import sys
import importlib
from pathlib import Path

REQUIRED_PYTHON = [
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("numpy", "numpy"),
    ("PIL", "Pillow"),
    ("rasterio", "rasterio"),
    ("cv2", "opencv-python"),
    ("pydantic", "pydantic"),
    ("httpx", "httpx"),
]

OPTIONAL_PYTHON = [
    ("torch", "torch"),
    ("transformers", "transformers"),
    ("google.generativeai", "google-generativeai"),
]

def check_python():
    missing = []
    for mod_name, pkg_name in REQUIRED_PYTHON:
        try:
            importlib.import_module(mod_name)
        except ImportError:
            missing.append(pkg_name)
    return missing

def check_node(root_dir: Path):
    node_modules = root_dir / "frontend" / "node_modules"
    return node_modules.exists() and any(node_modules.iterdir())

def main():
    root = Path(__file__).resolve().parent.parent
    missing_py = check_python()
    node_ok = check_node(root)

    if missing_py:
        print(f"[PREFLIGHT] Missing required Python packages: {', '.join(missing_py)}")
        sys.exit(1)

    if not node_ok:
        print("[PREFLIGHT] Frontend node_modules missing or empty.")
        sys.exit(2)

    print("[PREFLIGHT] All core dependencies satisfied.")
    sys.exit(0)

if __name__ == "__main__":
    main()
