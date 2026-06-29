#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Mux source video, localized audio, and optional subtitle overlay into a publish-ready MP4."
    )
    parser.add_argument("--source-video", required=True)
    parser.add_argument("--localized-audio", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--subtitle-overlay", default=None)
    parser.add_argument("--duration", default=None, help="Optional output duration in seconds")
    parser.add_argument("--crf", default="20")
    parser.add_argument("--preset", default="medium")
    parser.add_argument("--audio-bitrate", default="192k")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = Path(args.source_video).expanduser()
    audio = Path(args.localized_audio).expanduser()
    out = Path(args.out).expanduser()

    cmd = ["ffmpeg", "-y", "-i", str(source), "-i", str(audio)]
    if args.subtitle_overlay:
        overlay = Path(args.subtitle_overlay).expanduser()
        cmd += ["-i", str(overlay)]
        cmd += ["-filter_complex", "[0:v][2:v]overlay=0:0:format=auto[v]", "-map", "[v]"]
    else:
        cmd += ["-map", "0:v:0"]

    cmd += [
        "-map",
        "1:a:0",
        "-c:v",
        "libx264",
        "-preset",
        args.preset,
        "-crf",
        args.crf,
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        args.audio_bitrate,
        "-movflags",
        "+faststart",
    ]
    if args.duration:
        cmd += ["-t", str(args.duration)]
    cmd.append(str(out))

    subprocess.run(cmd, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
