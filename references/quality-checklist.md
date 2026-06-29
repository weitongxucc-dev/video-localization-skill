# Quality Checklist

Run this checklist before delivering a localized video.

## Media Structure

- Source and output have the intended aspect ratio.
- Source and output have the intended resolution.
- Output video codec is compatible with the user's playback target, usually H.264.
- Output has exactly one intended audio track unless the user asked for multiple tracks.
- Original English audio is not mapped into the final output.

## Timing

- Output audio duration is effectively equal to output container duration.
- Narration starts and stops at the correct visual moments.
- Long source silences remain silent unless the user asks for continuous narration.
- No global stretching of one full TTS file was used to fake synchronization.

## Subtitles

- Subtitles are visible on early, middle, and late sample frames.
- Font size is small enough for long lines but readable.
- Text wraps by pixel width and remains inside the frame.
- No ellipsis/truncation exists unless explicitly requested.
- Subtitles do not cover important faces, UI, or product details.

## Language

- Proper names and tool names are preserved.
- Chinese wording sounds watchable, not just literal.
- Technical terms are translated consistently.
- If automatic translation produced awkward names, flag that a human terminology pass is recommended.
