#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a transparent subtitle overlay video from timed JSON segments."
    )
    parser.add_argument("--segments", required=True, help="JSON list with start, end, and zh/text")
    parser.add_argument("--out", required=True, help="Output .mov overlay with alpha channel")
    parser.add_argument("--workdir", default=None, help="Working directory for generated PNGs")
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--font-path", default="/System/Library/Fonts/STHeiti Medium.ttc")
    parser.add_argument("--font-size", type=int, default=19)
    parser.add_argument("--bottom-margin", type=int, default=34)
    parser.add_argument("--max-width-ratio", type=float, default=0.86)
    parser.add_argument("--box-alpha", type=int, default=150)
    return parser.parse_args()


def quote_path(path: Path) -> str:
    return "'" + str(path).replace("'", "'\\''") + "'"


def measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font, stroke_width=1)
    return box[2] - box[0], box[3] - box[1]


def wrap_by_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    text = text.replace("\n", "").strip()
    lines: list[str] = []
    current = ""
    for ch in text:
        candidate = current + ch
        if current and measure(draw, candidate, font)[0] > max_width:
            lines.append(current)
            current = ch
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines or [""]


def segment_text(segment: dict) -> str:
    return str(segment.get("zh") or segment.get("text") or "").strip()


def make_pngs(args: argparse.Namespace, segments: list[dict], png_dir: Path) -> None:
    png_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype(args.font_path, args.font_size)
    max_text_width = int(args.width * args.max_width_ratio)

    for idx, segment in enumerate(segments, start=1):
        img = Image.new("RGBA", (args.width, args.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        lines = wrap_by_width(draw, segment_text(segment), font, max_text_width)
        line_sizes = [measure(draw, line, font) for line in lines]
        line_gap = max(4, args.font_size // 3)
        text_w = max((w for w, _ in line_sizes), default=0)
        text_h = sum(h for _, h in line_sizes) + max(0, len(lines) - 1) * line_gap

        pad_x = max(18, args.font_size + 5)
        pad_y = max(10, args.font_size // 2 + 5)
        box_w = min(args.width - 80, text_w + pad_x * 2)
        box_h = text_h + pad_y * 2
        box_x = (args.width - box_w) // 2
        box_y = args.height - box_h - args.bottom_margin

        draw.rounded_rectangle(
            (box_x, box_y, box_x + box_w, box_y + box_h),
            radius=max(8, args.font_size // 2),
            fill=(0, 0, 0, args.box_alpha),
        )

        y = box_y + pad_y - 1
        for line, (line_w, line_h) in zip(lines, line_sizes):
            x = (args.width - line_w) // 2
            draw.text(
                (x, y),
                line,
                font=font,
                fill=(255, 255, 255, 255),
                stroke_width=1,
                stroke_fill=(0, 0, 0, 255),
            )
            y += line_h + line_gap

        img.save(png_dir / f"sub_{idx:04d}.png")


def build_concat(args: argparse.Namespace, segments: list[dict], png_dir: Path, workdir: Path) -> Path:
    blank = workdir / "subtitle_blank.png"
    concat = workdir / "subtitle_overlay_concat.txt"
    Image.new("RGBA", (args.width, args.height), (0, 0, 0, 0)).save(blank)

    lines: list[str] = []
    current = 0.0
    last_file = blank

    for idx, segment in enumerate(segments, start=1):
        start = max(0.0, float(segment["start"]))
        end = min(args.duration, float(segment["end"]))
        if end <= start:
            continue
        if start > current + 0.001:
            lines.append(f"file {quote_path(blank)}")
            lines.append(f"duration {start - current:.6f}")
            last_file = blank

        png = png_dir / f"sub_{idx:04d}.png"
        lines.append(f"file {quote_path(png)}")
        lines.append(f"duration {end - start:.6f}")
        last_file = png
        current = max(current, end)

    if args.duration > current + 0.001:
        lines.append(f"file {quote_path(blank)}")
        lines.append(f"duration {args.duration - current:.6f}")
        last_file = blank

    lines.append(f"file {quote_path(last_file)}")
    concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return concat


def main() -> int:
    args = parse_args()
    segments_path = Path(args.segments).expanduser()
    out = Path(args.out).expanduser()
    workdir = Path(args.workdir).expanduser() if args.workdir else out.with_suffix("")
    png_dir = workdir / "subtitle_pngs"
    workdir.mkdir(parents=True, exist_ok=True)

    segments = json.loads(segments_path.read_text(encoding="utf-8"))
    make_pngs(args, segments, png_dir)
    concat = build_concat(args, segments, png_dir, workdir)

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-an",
            "-vsync",
            "vfr",
            "-pix_fmt",
            "argb",
            "-c:v",
            "qtrle",
            str(out),
        ],
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
