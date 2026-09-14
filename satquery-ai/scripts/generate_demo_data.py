"""
SatQuery AI — Demo Data Generator
Generates synthetic but realistic test satellite imagery for CI/demo use.
"""
from __future__ import annotations
import numpy as np
from pathlib import Path
from PIL import Image
import struct

BASE = Path(__file__).parent.parent / "demo_data"


def save_png(arr: np.ndarray, path: Path):
    """Save numpy array as PNG."""
    if arr.dtype != np.uint8:
        arr = ((arr - arr.min()) / (arr.max() - arr.min() + 1e-8) * 255).astype(np.uint8)
    if arr.ndim == 2:
        img = Image.fromarray(arr, mode='L')
    else:
        img = Image.fromarray(arr[:, :, :3], mode='RGB')
    img.save(path)
    print(f"  Saved: {path.name} ({arr.shape})")


def generate_synthetic_optical(size=256, seed=42) -> np.ndarray:
    """Generate synthetic optical satellite image with realistic land cover zones."""
    rng = np.random.default_rng(seed)
    img = np.zeros((size, size, 3), dtype=np.float32)

    # Zone 1: Urban/Built-up (top-right) — bright gray
    urban_mask = np.zeros((size, size), bool)
    urban_mask[10:100, 130:240] = True
    img[urban_mask, 0] = 160 + rng.uniform(-20, 20, urban_mask.sum())
    img[urban_mask, 1] = 155 + rng.uniform(-20, 20, urban_mask.sum())
    img[urban_mask, 2] = 150 + rng.uniform(-20, 20, urban_mask.sum())

    # Zone 2: Vegetation (left) — green
    veg_mask = np.zeros((size, size), bool)
    veg_mask[30:200, 5:120] = True
    img[veg_mask, 0] = 40 + rng.uniform(-10, 20, veg_mask.sum())
    img[veg_mask, 1] = 120 + rng.uniform(-20, 30, veg_mask.sum())
    img[veg_mask, 2] = 35 + rng.uniform(-10, 15, veg_mask.sum())

    # Zone 3: Water body (bottom-center) — dark blue
    water_mask = np.zeros((size, size), bool)
    for y in range(160, 240):
        for x in range(60, 180):
            if (x - 120)**2 / 1800 + (y - 200)**2 / 900 < 1:
                water_mask[y, x] = True
    img[water_mask, 0] = 20 + rng.uniform(-5, 10, water_mask.sum())
    img[water_mask, 1] = 40 + rng.uniform(-5, 15, water_mask.sum())
    img[water_mask, 2] = 90 + rng.uniform(-10, 20, water_mask.sum())

    # Zone 4: Bare soil/agricultural (remaining) — tan
    remaining = ~(urban_mask | veg_mask | water_mask)
    img[remaining, 0] = 140 + rng.uniform(-30, 30, remaining.sum())
    img[remaining, 1] = 120 + rng.uniform(-25, 25, remaining.sum())
    img[remaining, 2] = 90 + rng.uniform(-20, 20, remaining.sum())

    # Add road-like structures
    img[120:124, :, :] = [100, 100, 98]  # horizontal road
    img[:, 125:129, :] = [95, 95, 93]   # vertical road

    return np.clip(img, 0, 255).astype(np.uint8)


def generate_synthetic_sar(size=256, seed=42) -> np.ndarray:
    """Generate synthetic SAR image (single channel, realistic backscatter)."""
    rng = np.random.default_rng(seed + 10)
    img = np.zeros((size, size), dtype=np.float32)

    # Urban = high backscatter (bright)
    img[10:100, 130:240] = 200 + rng.uniform(-30, 30, (90, 110))

    # Vegetation = moderate backscatter
    img[30:200, 5:120] = 100 + rng.uniform(-30, 30, (170, 115))

    # Water = very low backscatter (dark)
    for y in range(160, 240):
        for x in range(60, 180):
            if (x - 120)**2 / 1800 + (y - 200)**2 / 900 < 1:
                img[y, x] = 15 + rng.uniform(-5, 10)

    # Bare soil = medium-low
    base = np.full((size, size), 80.0)
    mask = img == 0
    img[mask] = base[mask] + rng.uniform(-20, 20, mask.sum())

    # SAR speckle noise
    speckle = rng.gamma(shape=4, scale=0.25, size=(size, size))
    img = img * speckle

    return np.clip(img, 0, 255).astype(np.uint8)


def generate_changed_optical(original: np.ndarray, seed=99) -> np.ndarray:
    """Generate T2 image with realistic urban expansion change."""
    rng = np.random.default_rng(seed)
    changed = original.copy().astype(np.float32)

    # Expand urban area — vegetation to built-up
    changed[80:160, 5:80, 0] = 160 + rng.uniform(-20, 20, (80, 75))
    changed[80:160, 5:80, 1] = 155 + rng.uniform(-20, 20, (80, 75))
    changed[80:160, 5:80, 2] = 150 + rng.uniform(-20, 20, (80, 75))

    # New building cluster
    changed[10:60, 245:255, :] = [140, 135, 130]

    # Water recession (partial drying)
    changed[220:240, 100:150, 0] = 130 + rng.uniform(-10, 10, (20, 50))
    changed[220:240, 100:150, 1] = 110 + rng.uniform(-10, 10, (20, 50))
    changed[220:240, 100:150, 2] = 85 + rng.uniform(-10, 10, (20, 50))

    return np.clip(changed, 0, 255).astype(np.uint8)


def create_minimal_geotiff(arr: np.ndarray, path: Path):
    """
    Create a minimal valid GeoTIFF. Handles 2D (H,W) and 3D (H,W,C) arrays.
    Falls back to PIL TIFF if rasterio unavailable.
    """
    try:
        import rasterio
        from rasterio.transform import from_bounds
        from rasterio.crs import CRS
        if arr.ndim == 2:
            h, w = arr.shape
            bands = 1
            write_arr = arr  # 2D for single band write
        else:
            h, w, bands = arr.shape
            write_arr = arr

        transform = from_bounds(77.0, 28.5, 77.1, 28.6, w, h)
        crs = CRS.from_epsg(4326)
        with rasterio.open(
            path, 'w', driver='GTiff',
            height=h, width=w, count=bands,
            dtype=arr.dtype, crs=crs, transform=transform,
        ) as dst:
            if bands == 1:
                if arr.ndim == 2:
                    dst.write(arr, 1)
                else:
                    dst.write(arr[:, :, 0], 1)
            else:
                for b in range(bands):
                    dst.write(write_arr[:, :, b], b + 1)
        print(f"  Saved GeoTIFF: {path.name} (CRS: EPSG:4326, bands={bands})")
    except ImportError:
        if arr.ndim == 2:
            img = Image.fromarray(arr, mode='L')
        else:
            img = Image.fromarray(arr[:, :, :3], mode='RGB')
        img.save(str(path))
        print(f"  Saved TIFF (no CRS): {path.name}")


def main():
    print("SatQuery AI — Generating demo data...")
    BASE.mkdir(parents=True, exist_ok=True)

    # 1. Single optical
    print("\n[1] Single optical image")
    opt = generate_synthetic_optical(256)
    create_minimal_geotiff(opt, BASE / "single_optical" / "scene_optical.tif")
    save_png(opt, BASE / "single_optical" / "scene_optical_preview.png")

    # 2. Single SAR
    print("\n[2] Single SAR image")
    sar = generate_synthetic_sar(256)
    create_minimal_geotiff(sar, BASE / "single_sar" / "scene_sar.tif")
    save_png(sar, BASE / "single_sar" / "scene_sar_preview.png")

    # 3. Optical + SAR pair (co-registered)
    print("\n[3] Optical + SAR co-registered pair")
    opt2 = generate_synthetic_optical(256, seed=77)
    sar2 = generate_synthetic_sar(256, seed=77)
    create_minimal_geotiff(opt2, BASE / "optical_sar" / "optical.tif")
    create_minimal_geotiff(sar2, BASE / "optical_sar" / "sar.tif")
    save_png(opt2, BASE / "optical_sar" / "optical_preview.png")
    save_png(sar2, BASE / "optical_sar" / "sar_preview.png")

    # 4. Bi-temporal pair (T1 + T2 with urban expansion)
    print("\n[4] Bi-temporal pair (T1 + T2)")
    t1 = generate_synthetic_optical(256, seed=5)
    t2 = generate_changed_optical(t1, seed=99)
    create_minimal_geotiff(t1, BASE / "temporal" / "t1_before.tif")
    create_minimal_geotiff(t2, BASE / "temporal" / "t2_after.tif")
    save_png(t1, BASE / "temporal" / "t1_preview.png")
    save_png(t2, BASE / "temporal" / "t2_preview.png")

    print("\nDone! Demo data generation complete!")
    print(f"  Location: {BASE}")
    print("\nFiles created:")
    for f in sorted(BASE.rglob("*")):
        if f.is_file():
            size = f.stat().st_size
            print(f"  {f.relative_to(BASE)} ({size:,} bytes)")


if __name__ == "__main__":
    main()
