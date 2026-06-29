# Cross-Tool Adapters

Use this skill as a portable instruction folder. The core artifact is `SKILL.md`; scripts are optional helpers.

## Native or Near-Native Skill Layout

- **Codex**: place the folder under `~/.codex/skills/video-localization-skill/` or install it through your Codex skill/plugin mechanism.
- **Claude Code**: place the folder in a repo and reference it from `CLAUDE.md`, or copy the key workflow into a Claude Code custom command. If Claude Code supports skill folders in your setup, keep the folder structure unchanged.
- **OpenClaw / Hermes / OpenCode**: place this folder under the project's agent instructions directory if one exists, or reference `SKILL.md` from the project's main agent rule file.

## Rule-File Based Tools

For tools that do not automatically load skill folders, add a short pointer to the tool's instruction file:

```markdown
When asked to localize, translate, dub, subtitle, or publish-process a video, use the workflow in `video-localization-skill/SKILL.md`. Preserve aspect ratio, remove original audio, align Chinese narration to the source timeline, burn complete Chinese subtitles, and verify with ffprobe plus frame checks.
```

Suggested locations:

- **Cursor / VS Code agent setups**: `.cursorrules`, `.cursor/rules/video-localization.md`, `.github/copilot-instructions.md`, or `AGENTS.md`.
- **Trae**: project-level AI rules or `.trae/rules/` if supported by the installed version.
- **Workbody**: workspace/project AI instruction file or custom agent prompt template.
- **Generic agents**: `AGENTS.md`, `AI_RULES.md`, `SYSTEM.md`, or the tool's project memory file.

## Dependency Notes

The workflow expects:

- `ffmpeg` and `ffprobe`
- Python 3
- Pillow for PNG subtitle rendering
- A transcription engine, such as Whisper or a provider API
- A translation method
- A Chinese TTS provider

The skill does not mandate a specific transcription, translation, or TTS provider. Choose based on the user's environment, budget, rights, and quality requirements.
