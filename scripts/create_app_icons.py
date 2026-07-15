from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ICONS_DIR = PROJECT_ROOT / "assets" / "icons"

SOURCE_PNG = ICONS_DIR / "sunset.png"
MACOS_ICON = ICONS_DIR / "sunset.icns"
WINDOWS_ICON = ICONS_DIR / "sunset.ico"

CANVAS_SIZE = 1024


def interpolate_channel(start: int, end: int, ratio: float) -> int:
    return round(start + (end - start) * ratio)


def interpolate_color(
    start: tuple[int, int, int],
    end: tuple[int, int, int],
    ratio: float,
) -> tuple[int, int, int]:
    return tuple(
        interpolate_channel(start_channel, end_channel, ratio)
        for start_channel, end_channel in zip(start, end, strict=True)
    )


def draw_vertical_gradient(
    image: Image.Image,
    top: tuple[int, int, int],
    bottom: tuple[int, int, int],
) -> None:
    draw = ImageDraw.Draw(image)

    for y in range(image.height):
        ratio = y / max(image.height - 1, 1)
        color = interpolate_color(top, bottom, ratio)
        draw.line((0, y, image.width, y), fill=color)


def create_source_icon() -> None:
    ICONS_DIR.mkdir(parents=True, exist_ok=True)

    image = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE))
    draw_vertical_gradient(
        image,
        top=(72, 38, 124),
        bottom=(255, 132, 57),
    )

    draw = ImageDraw.Draw(image)

    # Солнце
    sun_box = (332, 250, 692, 610)
    draw.ellipse(sun_box, fill=(255, 222, 116))

    # Дальние горы
    draw.polygon(
        [
            (0, 610),
            (180, 440),
            (335, 585),
            (505, 400),
            (680, 580),
            (840, 445),
            (1024, 610),
            (1024, 760),
            (0, 760),
        ],
        fill=(73, 42, 105),
    )

    # Ближние горы
    draw.polygon(
        [
            (0, 700),
            (190, 555),
            (355, 690),
            (530, 520),
            (730, 700),
            (880, 575),
            (1024, 670),
            (1024, 815),
            (0, 815),
        ],
        fill=(31, 32, 82),
    )

    # Вода
    draw.rectangle(
        (0, 760, CANVAS_SIZE, CANVAS_SIZE),
        fill=(20, 30, 72),
    )

    # Отражение солнца
    reflection_widths = [260, 230, 200, 170, 140, 110, 80]
    reflection_y = 785

    for width in reflection_widths:
        left = (CANVAS_SIZE - width) // 2
        right = left + width

        draw.rounded_rectangle(
            (left, reflection_y, right, reflection_y + 18),
            radius=9,
            fill=(255, 159, 67),
        )
        reflection_y += 35

    # Скруглённая маска, чтобы PNG выглядел как значок приложения.
    mask = Image.new("L", image.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        (30, 30, CANVAS_SIZE - 30, CANVAS_SIZE - 30),
        radius=210,
        fill=255,
    )

    rgba_image = image.convert("RGBA")
    rgba_image.putalpha(mask)
    rgba_image.save(SOURCE_PNG)


def create_windows_icon() -> None:
    source = Image.open(SOURCE_PNG).convert("RGBA")

    source.save(
        WINDOWS_ICON,
        format="ICO",
        sizes=[
            (16, 16),
            (24, 24),
            (32, 32),
            (48, 48),
            (64, 64),
            (128, 128),
            (256, 256),
        ],
    )


def create_macos_icon() -> None:
    if sys.platform != "darwin":
        print("Пропуск .icns: iconutil доступен только на macOS.")
        return

    iconset_dir = ICONS_DIR / "sunset.iconset"

    if iconset_dir.exists():
        shutil.rmtree(iconset_dir)

    iconset_dir.mkdir(parents=True)

    source = Image.open(SOURCE_PNG).convert("RGBA")

    icon_sizes = {
        "icon_16x16.png": 16,
        "icon_16x16@2x.png": 32,
        "icon_32x32.png": 32,
        "icon_32x32@2x.png": 64,
        "icon_128x128.png": 128,
        "icon_128x128@2x.png": 256,
        "icon_256x256.png": 256,
        "icon_256x256@2x.png": 512,
        "icon_512x512.png": 512,
        "icon_512x512@2x.png": 1024,
    }

    for filename, size in icon_sizes.items():
        resized = source.resize(
            (size, size),
            Image.Resampling.LANCZOS,
        )
        resized.save(iconset_dir / filename)

    subprocess.run(
        [
            "iconutil",
            "--convert",
            "icns",
            "--output",
            str(MACOS_ICON),
            str(iconset_dir),
        ],
        check=True,
    )

    shutil.rmtree(iconset_dir)


def main() -> None:
    create_source_icon()
    create_windows_icon()
    create_macos_icon()

    print(f"PNG:  {SOURCE_PNG}")
    print(f"ICO:  {WINDOWS_ICON}")

    if MACOS_ICON.exists():
        print(f"ICNS: {MACOS_ICON}")


if __name__ == "__main__":
    main()
