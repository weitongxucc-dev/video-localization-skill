# Video Localization Skill

一个面向 AI Agent 的视频本地化 Skill：把英文或外语视频处理成适合中文观众观看的发布版视频。

它可以帮助 Codex、Claude Code、OpenClaw、Hermes、OpenCode、Trae、Workbody 等 AI 工具完成一套稳定的视频本地化工作流：保留原视频画幅，移除原声，生成中文配音，压入中文字幕，并在交付前完成音画同步和画面检查。

## 这个 Skill 能做什么

- **保留原视频画幅**：原视频是 `16:9` 横屏，就不会被错误处理成 `9:16` 竖屏。
- **替换英文原声**：最终视频只保留中文配音，不让英文和中文声音混在一起。
- **保持音画同步**：按原视频时间轴逐段合成中文语音，中间停顿保留静音，而不是粗暴拉伸整段音频。
- **生成中文字幕**：自动生成并压入中文字幕，支持小字号、自动换行、完整显示。
- **发布前验收**：检查分辨率、画幅、音轨数量、音视频时长、字幕抽帧效果。
- **跨工具复用**：可给 Codex、Claude Code、OpenClaw、Hermes、OpenCode、Trae、Workbody、Cursor、VS Code Agent 等工具读取。

## 为自媒体解决什么痛点

做 AI、科技、知识解读、课程、海外资讯类自媒体时，很多优质内容来自英文视频。真正耗时的不是“看懂视频”，而是把它变成一个可以发布给中文用户看的版本。

常见痛点包括：

- 下载下来的视频播放器没画面，因为编码不兼容。
- 原本是横屏教程，处理后变成竖屏，画面被裁掉。
- 中文配音生成了，但英文原声还在，听起来很乱。
- 中文配音和画面不同步，越到后面越错位。
- 字幕太大，长句显示不完整。
- 翻译工具名、人名、产品名时出现低级错误。
- 每次处理视频都要重新提醒 AI：不要改比例、不要保留英文、不要音画错位。

这个 Skill 的价值，就是把这些经验固化成一套 AI Agent 可以重复执行的标准流程。

## 商业价值

这个 Skill 适合以下人群和团队：

- **AI 自媒体创作者**：更快把海外工具教程、产品演示、技术趋势转成中文内容。
- **知识付费和课程团队**：把英文课程、直播、访谈、演示视频本地化为中文学习材料。
- **企业培训团队**：把海外供应商培训、产品说明、技术资料转为内部中文培训视频。
- **MCN 和内容工作室**：把视频本地化流程标准化，减少人工反复返工。
- **产品和销售团队**：把英文产品 demo 快速变成中文演示材料。

核心商业价值是：降低视频本地化的时间成本和返工成本，让优质英文内容更快进入中文市场。

## 适合哪些工具

原生或近似支持：

- Codex
- Claude Code
- OpenClaw
- Hermes
- OpenCode

可通过项目规则文件适配：

- Trae
- Workbody
- Cursor
- VS Code Agent
- GitHub Copilot coding agent
- 其他支持读取 `AGENTS.md`、规则文件或自定义系统提示的 AI 工具

详细适配方式见：

[references/cross-tool-adapters.md](references/cross-tool-adapters.md)

## 快速领取

方式一：直接 clone

```bash
git clone https://github.com/weitongxucc-dev/video-localization-skill.git
```

方式二：给 Codex 使用

```bash
git clone https://github.com/weitongxucc-dev/video-localization-skill.git ~/.codex/skills/video-localization-skill
```

方式三：复制到你的项目里

```bash
git clone https://github.com/weitongxucc-dev/video-localization-skill.git
cp -R video-localization-skill /path/to/your-project/
```

然后在你的 AI 工具规则文件里加入：

```markdown
当我要求处理、翻译、配音、字幕化或本地化视频时，请使用 `video-localization-skill/SKILL.md` 中的流程。必须保留原始画幅，移除原声，按时间轴生成中文配音，压入完整中文字幕，并在交付前用 ffprobe 和抽帧检查结果。
```

## 依赖环境

基础依赖：

- Python 3.10+
- ffmpeg
- ffprobe
- Pillow

可选依赖：

- yt-dlp：用于下载用户授权的视频
- Whisper 或其他转写服务：用于生成时间戳转写
- 翻译 API 或本地模型
- 中文 TTS 服务

安装 Python 依赖：

```bash
pip install -r requirements.txt
```

macOS 安装 ffmpeg：

```bash
brew install ffmpeg
```

## 目录结构

```text
video-localization-skill/
├── SKILL.md                         # 给 AI Agent 读取的核心流程
├── README.md                        # 给人看的中文项目说明
├── agents/
│   └── openai.yaml                  # Codex/OpenAI 兼容元信息
├── references/
│   ├── cross-tool-adapters.md       # 不同 AI 工具的适配方式
│   └── quality-checklist.md         # 发布前质检清单
├── scripts/
│   ├── probe_media.py               # 探测媒体结构
│   ├── build_subtitle_overlay.py    # 生成透明中文字幕层
│   ├── mux_localized_video.py       # 合成最终视频
│   └── install.sh                   # 简易安装脚本
└── requirements.txt
```

## 典型工作流

1. 下载或准备源视频。
2. 探测源视频画幅、编码、时长。
3. 转写视频，得到带时间戳的原文。
4. 分段翻译成中文，保留专有名词。
5. 按时间轴逐段生成中文配音。
6. 生成透明中文字幕层。
7. 合成最终视频，只保留中文音轨。
8. 抽帧和探测参数，确认可以发布。

## 脚本示例

探测视频：

```bash
python scripts/probe_media.py source.mp4
```

生成中文字幕透明层：

```bash
python scripts/build_subtitle_overlay.py \
  --segments translations.json \
  --out sub_overlay.mov \
  --width 1280 \
  --height 720 \
  --duration 1753.756 \
  --font-size 19
```

合成最终视频：

```bash
python scripts/mux_localized_video.py \
  --source-video source.mp4 \
  --localized-audio zh_timeline.wav \
  --subtitle-overlay sub_overlay.mov \
  --out localized-zh.mp4
```

## 输入格式示例

`translations.json`：

```json
[
  {
    "start": 0.0,
    "end": 8.4,
    "en": "One of the best things about tools like OpenAI Codex...",
    "zh": "像 OpenAI Codex 这样的工具，最有价值的一点是..."
  }
]
```

## 发布前检查

交付前至少确认：

- 输出视频仍是原始画幅。
- 输出视频只有一条中文音轨。
- 音频和视频时长基本一致。
- 字幕已经压入画面。
- 字幕完整显示，没有被省略。
- 视频可以在普通播放器正常播放。

完整清单见：

[references/quality-checklist.md](references/quality-checklist.md)

## 注意事项

这个项目不鼓励未经授权下载、搬运或发布他人视频。请确保你拥有相应内容的下载、处理、翻译、配音、发布或二次创作权限。

## License

MIT License
