---
name: video-localization-skill
description: Localize videos into publish-ready Chinese versions with translated narration, burned-in Chinese subtitles, original aspect-ratio preservation, original-audio removal, and audio/video synchronization. Use when asked to download or process a video, translate an English video, replace English speech with Chinese voiceover, create Chinese subtitles, fix subtitle size/completeness, preserve 16:9 horizontal video, or prepare a localized video for publishing in Codex, Claude Code, OpenClaw, Hermes, OpenCode, Trae, Workbody, Cursor, VS Code, or similar AI coding agents.
---

# Video Localization Skill

## Overview

Convert a source video into a localized Chinese video without changing its visual format. Preserve the original video geometry, replace the original audio with Chinese narration, burn complete Chinese subtitles into the video, and verify the output before delivery.

## Non-Negotiable Requirements

- Preserve the source aspect ratio, resolution, frame rate, and orientation unless the user explicitly asks to crop or reframe.
- Remove or ignore the source audio track in the final output. Map only the localized Chinese audio.
- Keep Chinese narration aligned to the source timeline. Build audio on the original segment timeline, inserting silence during gaps. Do not globally stretch a full narration file to fit the video.
- Burn Chinese subtitles into the video when the user asks for visible subtitles. Use soft subtitle tracks only as an explicit fallback.
- Do not truncate subtitle text with ellipses unless the user asks for short captions. Use smaller font size and pixel-width wrapping to show full text.
- Verify the final video with `ffprobe` and visual frame checks before saying the task is complete.
- Preserve intermediate files when useful: source video, segment transcript, translations, synthesized audio, subtitle overlay, final output, and prior-version backups.

## Workflow

1. **Confirm source and rights**
   - If downloading from YouTube or another platform, confirm the user has rights or permission to download/process the video.
   - Prefer a broadly compatible H.264/AAC source when possible. Avoid AV1-only outputs if the user needs easy playback.

2. **Probe the source**
   - Run `ffprobe` or `scripts/probe_media.py` on the source.
   - Record width, height, display aspect ratio, duration, video codec, audio codec, frame rate, and audio track count.
   - Treat the source video stream as the visual master.

3. **Transcribe with timestamps**
   - Produce segment-level timestamps in source-video time.
   - Use the original timeline as the authority. Segments must include `start`, `end`, and source text.
   - Keep segments reasonably short for TTS alignment. Group adjacent segments only when timing remains natural.

4. **Translate for voice and subtitles**
   - Translate per segment or per small group, not as one full-document blob.
   - Preserve product names, tool names, GitHub repo names, people names, and brand terms. Examples: `Codex`, `Claude Code`, `OpenClaw`, `Hermes`, `OpenCode`, `Trae`, `Workbody`, `G-Stack`, `Graphify`, `Remotion`, `Hyperframes`.
   - Make Chinese natural but faithful. Avoid over-literal machine translation if the result will be watched by humans.
   - Store translations as JSON records with at least:

```json
[
  {
    "start": 0.0,
    "end": 8.4,
    "en": "Original text",
    "zh": "中文翻译"
  }
]
```

5. **Synthesize Chinese narration on the timeline**
   - Generate TTS per translated segment or group.
   - Place each generated audio clip at its source `start` time.
   - If a clip is shorter than its segment window, pad the remainder with silence.
   - If a clip is slightly longer, prefer a small local speed adjustment or trim the tail only when acceptable. Do not let one segment push later segments out of sync.
   - Export a single localized audio file with the exact source duration.

6. **Create burned-in subtitles**
   - Prefer a single transparent subtitle overlay video, then overlay it once onto the source video.
   - Avoid a filter graph with hundreds of simultaneous PNG inputs; it is slow and fragile.
   - Use `scripts/build_subtitle_overlay.py` when subtitles come from a JSON file with `start`, `end`, and `zh` or `text`.
   - Default to compact subtitles for long technical videos: around 18-24 px at 1280x720, centered near the bottom, wrapped by pixel width, with no ellipsis.

7. **Mux the final video**
   - Use the original source video stream as input 0, localized audio as input 1, subtitle overlay as input 2.
   - Map only `[localized video]` and localized audio. Do not map the original English audio.
   - Use H.264/AAC for compatibility unless the user requests a different codec.
   - Use `scripts/mux_localized_video.py` when possible.

8. **Verify before delivery**
   - Confirm final aspect ratio and resolution match the source unless intentionally changed.
   - Confirm exactly one final audio track exists and it is the localized audio.
   - Confirm video duration and audio duration are effectively equal.
   - Extract frames from early, middle, and late timestamps; visually inspect subtitle presence, size, wrapping, and non-overlap.
   - If the user complained about missing picture, verify codec compatibility and avoid AV1 if their player does not support it.

## Recommended Commands

Probe media:

```bash
python scripts/probe_media.py input.mp4
```

Build a transparent subtitle overlay:

```bash
python scripts/build_subtitle_overlay.py \
  --segments translations.json \
  --out sub_overlay.mov \
  --width 1280 \
  --height 720 \
  --duration 1753.756 \
  --font-size 19
```

Mux source video, localized audio, and subtitle overlay:

```bash
python scripts/mux_localized_video.py \
  --source-video source.mp4 \
  --localized-audio zh_timeline.wav \
  --subtitle-overlay sub_overlay.mov \
  --out localized-zh.mp4
```

## Cross-Tool Use

For agent tools that do not have a native skill/plugin system, copy this folder into the project and reference `SKILL.md` from the tool's rule file. See `references/cross-tool-adapters.md` for suggested placements for Claude Code, Codex, OpenClaw, Hermes, OpenCode, Trae, Workbody, Cursor, and VS Code-style agents.

## Failure Modes To Avoid

- Do not convert a 16:9 source into a 9:16 vertical video unless the user requests social short formatting.
- Do not keep English audio underneath the Chinese voiceover.
- Do not synthesize one long Chinese file and globally stretch it to match the video; this causes drift.
- Do not burn huge subtitles that cover the subject or force truncation.
- Do not declare completion from command success alone; inspect the actual output.
