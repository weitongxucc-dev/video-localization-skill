#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: probe_media.py <media-file>", file=sys.stderr)
        return 2

    media = Path(sys.argv[1]).expanduser()
    if not media.exists():
        print(f"File not found: {media}", file=sys.stderr)
        return 1

    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "stream=index,codec_type,codec_name,width,height,display_aspect_ratio,avg_frame_rate,duration:stream_tags=language",
        "-show_entries",
        "format=duration,size,format_name",
        "-of",
        "json",
        str(media),
    ]
    result = subprocess.run(cmd, check=True, text=True, capture_output=True)
    data = json.loads(result.stdout)

    streams = data.get("streams", [])
    video = [s for s in streams if s.get("codec_type") == "video"]
    audio = [s for s in streams if s.get("codec_type") == "audio"]
    summary = {
        "file": str(media),
        "format": data.get("format", {}),
        "video_streams": video,
        "audio_streams": audio,
        "video_count": len(video),
        "audio_count": len(audio),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
