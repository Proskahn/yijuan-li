#!/usr/bin/env python3
"""Create gallery data and web images without changing the original artwork.

Run from any directory: python3 scripts/prepare_illustrations.py
Requires Pillow. HEIC/HEIF uses macOS sips, or pillow-heif on other platforms.
Numbered filenames set the order; their text supplies the displayed titles.
Commit the generated _data/illustrations.json and assets/illustrations files.
"""

import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from PIL import Image, ImageCms, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "illustration"
OUTPUT = ROOT / "assets" / "illustrations"
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}


def open_artwork(path, temporary):
    if path.suffix.lower() in {".heic", ".heif"}:
        if shutil.which("sips"):
            converted = Path(temporary) / (path.stem + ".png")
            subprocess.run(
                ["sips", "-s", "format", "png", str(path), "--out", str(converted)],
                check=True, stdout=subprocess.DEVNULL,
            )
            path = converted
        else:
            from pillow_heif import register_heif_opener
            register_heif_opener()
    with Image.open(path) as original:
        artwork = ImageOps.exif_transpose(original)
        profile = original.info.get("icc_profile")
        if profile:
            artwork = ImageCms.profileToProfile(
                artwork, ImageCms.ImageCmsProfile(io.BytesIO(profile)),
                ImageCms.createProfile("sRGB"), outputMode="RGBA",
            )
        artwork = artwork.convert("RGBA")
        # Transparent drawing canvases are displayed on white paper.
        paper = Image.new("RGBA", artwork.size, "white")
        paper.alpha_composite(artwork)
        return paper.convert("RGB")


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    works = []
    with tempfile.TemporaryDirectory() as temporary:
        for path in sorted(SOURCE.iterdir()):
            if path.suffix.lower() not in EXTENSIONS:
                continue
            match = re.match(r"^(\d+)\s+(.+)$", path.stem)
            number, title = match.groups() if match else (f"{len(works) + 1:02}", path.stem)
            slug = re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")
            artwork = open_artwork(path, temporary)
            work = {
                "number": number,
                "title": title,
                "source": path.name,
                "category": "excercises" if title.startswith("Exercise - ") else "illustration",
                "width": artwork.width,
                "height": artwork.height,
            }
            for label, max_width in [("small", 640), ("medium", 1280), ("large", 2200)]:
                image = artwork.copy()
                width = min(max_width, image.width)
                height = round(image.height * width / image.width)
                image = image.resize((width, height), Image.Resampling.LANCZOS)
                destination = OUTPUT / f"{slug}-{label}.webp"
                image.save(destination, "WEBP", quality=88, method=6)
                work[label] = "/" + destination.relative_to(ROOT).as_posix()
                work[f"{label}_width"] = width
            works.append(work)
            print(f"Prepared {number} {title}")
    (ROOT / "_data" / "illustrations.json").write_text(
        json.dumps(works, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    print(f"Prepared {len(works)} works.")


if __name__ == "__main__":
    main()
