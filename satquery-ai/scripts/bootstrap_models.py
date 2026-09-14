"""
SatQuery AI — Model Bootstrap Script
Checks available models and downloads what's needed.
"""
from __future__ import annotations
import sys
import json
from pathlib import Path

BASE = Path(__file__).parent.parent
CACHE = BASE / "models" / "cache"
REGISTRY_FILE = BASE / "models" / "registry.json"


MODELS = [
    {
        "id": "blip_captioning",
        "name": "BLIP Image Captioning Base",
        "hf_id": "Salesforce/blip-image-captioning-base",
        "size_mb": 990,
        "task": "captioning/vqa",
        "required": False,
        "notes": "Primary VQA/captioning model. CPU-compatible.",
    },
    {
        "id": "blip_vqa",
        "name": "BLIP VQA Base",
        "hf_id": "Salesforce/blip-vqa-base",
        "size_mb": 990,
        "task": "vqa",
        "required": False,
        "notes": "Specialized VQA model. CPU-compatible.",
    },
]


def check_available():
    """Check which models are already cached."""
    available = {}
    for m in MODELS:
        local_path = CACHE / m["id"]
        if local_path.exists() and any(local_path.iterdir()):
            available[m["id"]] = {"status": "cached", "path": str(local_path)}
        else:
            available[m["id"]] = {"status": "not_cached", "path": None}
    return available


def download_model(model_info: dict, force: bool = False):
    """Download a model from HuggingFace Hub."""
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("  ERROR: huggingface_hub not installed. Run: pip install huggingface-hub")
        return False

    local_path = CACHE / model_info["id"]
    if local_path.exists() and not force:
        print(f"  Already cached: {model_info['name']}")
        return True

    print(f"  Downloading {model_info['name']} (~{model_info['size_mb']}MB)...")
    print(f"  HuggingFace ID: {model_info['hf_id']}")
    try:
        snapshot_download(
            repo_id=model_info["hf_id"],
            local_dir=str(local_path),
            ignore_patterns=["*.msgpack", "flax*", "tf_*"],
        )
        print(f"  ✓ Downloaded to {local_path}")
        return True
    except Exception as e:
        print(f"  ✗ Download failed: {e}")
        return False


def update_registry(available: dict):
    """Update the model registry JSON."""
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    registry = {
        "generated_at": str(Path(__file__).stat().st_mtime),
        "models": {},
    }
    for m in MODELS:
        status = available.get(m["id"], {}).get("status", "not_cached")
        registry["models"][m["id"]] = {
            **m,
            "status": "ready" if status == "cached" else "not_installed",
            "local_path": available.get(m["id"], {}).get("path"),
        }
    REGISTRY_FILE.write_text(json.dumps(registry, indent=2))
    print(f"  Registry updated: {REGISTRY_FILE}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SatQuery AI — Model Bootstrap")
    parser.add_argument("--download", action="store_true", help="Download recommended models")
    parser.add_argument("--model", help="Download specific model ID")
    parser.add_argument("--force", action="store_true", help="Force re-download")
    parser.add_argument("--list", action="store_true", help="List all models and status")
    args = parser.parse_args()

    print("SatQuery AI — Model Bootstrap")
    print("=" * 50)

    CACHE.mkdir(parents=True, exist_ok=True)
    available = check_available()

    if args.list or not (args.download or args.model):
        print("\nAvailable models:\n")
        for m in MODELS:
            status = available.get(m["id"], {}).get("status", "unknown")
            icon = "✓" if status == "cached" else "○"
            req = "[required]" if m["required"] else "[optional]"
            print(f"  {icon} {m['id']:<25} {m['name']:<40} ~{m['size_mb']}MB {req}")
            print(f"      {m['notes']}")
        print()

    if args.model:
        target = next((m for m in MODELS if m["id"] == args.model), None)
        if not target:
            print(f"Unknown model: {args.model}")
            sys.exit(1)
        download_model(target, args.force)

    elif args.download:
        print("\nDownloading recommended models...")
        print("(This may take several minutes depending on connection speed)\n")
        consent = input("Proceed with download? [y/N]: ").strip().lower()
        if consent != 'y':
            print("Cancelled.")
            sys.exit(0)
        for m in MODELS:
            if not m["required"]:
                continue
            download_model(m, args.force)

    available = check_available()
    update_registry(available)

    cached_count = sum(1 for v in available.values() if v["status"] == "cached")
    print(f"\nStatus: {cached_count}/{len(MODELS)} models cached")
    print("\nNote: SatQuery AI runs on CPU with classical analysis even without downloaded models.")
    print("The BLIP models enhance VQA/captioning quality but are not required for core functionality.")


if __name__ == "__main__":
    main()
