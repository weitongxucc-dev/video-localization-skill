# 跨工具适配说明

这个仓库的核心是 `SKILL.md`。它既可以被原生支持 Skill 的 AI Agent 直接读取，也可以作为普通规则文件被其他 AI 编程工具引用。

## 原生或近似原生 Skill 方式

- **Codex**：推荐放到 `~/.codex/skills/video-localization-skill/`，或通过 Codex 的 Skill / Plugin 机制安装。
- **Claude Code**：把本目录放进项目仓库，并在 `CLAUDE.md` 中引用 `SKILL.md`；也可以把核心流程改造成 Claude Code 自定义命令。
- **OpenClaw / Hermes / OpenCode**：如果项目有 agent instructions、skills、plugins、rules 目录，可以把本目录放进去；否则在主规则文件中引用 `SKILL.md`。

## 规则文件方式

如果工具不会自动加载 Skill 目录，可以在项目规则文件里加入下面这段：

```markdown
当我要求处理、翻译、配音、字幕化或本地化视频时，请使用 `video-localization-skill/SKILL.md` 中的流程。必须保留原始画幅，移除原声，按原视频时间轴生成中文配音，压入完整中文字幕，并在交付前用 ffprobe 和抽帧检查结果。
```

## 常见工具放置位置

- **Cursor / VS Code Agent**：`.cursorrules`、`.cursor/rules/video-localization.md`、`.github/copilot-instructions.md` 或 `AGENTS.md`
- **Trae**：项目级 AI Rules、`.trae/rules/` 或 Trae 当前版本支持的自定义规则入口
- **Workbody**：工作区/项目 AI 指令文件、自定义 Agent Prompt、团队模板
- **Claude Code**：`CLAUDE.md` 或自定义 command
- **通用 Agent**：`AGENTS.md`、`AI_RULES.md`、`SYSTEM.md`、项目 memory 文件

## 依赖说明

基础依赖：

- `ffmpeg`
- `ffprobe`
- Python 3
- Pillow

按实际场景选择：

- 视频下载：`yt-dlp` 或平台 API
- 转写：Whisper、本地 ASR、云端 ASR
- 翻译：大模型、翻译 API、本地翻译模型
- 中文配音：本地 TTS、云端 TTS、真人配音

这个 Skill 不强制绑定某一个转写、翻译或配音供应商。执行时应根据用户预算、版权要求、质量要求和本地环境选择合适工具。

## 国产工具适配建议

对 Trae、Workbody 等国产 AI 编程工具，优先采用“项目规则文件 + 本目录脚本”的方式：

1. 把本仓库 clone 到项目中，或放到团队公共工具目录。
2. 在工具的项目规则里引用 `SKILL.md`。
3. 告诉 Agent：遇到视频本地化任务时，先读取 `SKILL.md`，再调用 `scripts/` 下的脚本。
4. 如果工具无法直接执行脚本，让 Agent 输出命令，由用户在终端执行。

重点不是工具名字，而是让 Agent 记住这套约束：保画幅、去原声、按时间轴配音、完整字幕、最终验收。
