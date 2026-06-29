---
name: video-localization-skill
description: 将英文或外语视频本地化为可发布的中文视频，包含中文配音、中文字幕压屏、原始画幅保真、原声移除、音画同步和最终验收。Use when asked to localize, translate, dub, subtitle, download/process, or publish-ready convert a video in Codex, Claude Code, OpenClaw, Hermes, OpenCode, Trae, Workbody, Cursor, VS Code, or similar AI coding agents.
---

# Video Localization Skill

## 目标

把一个英文或外语视频处理成适合中文观众观看的发布版视频。执行时必须保留原视频画面形态，只替换为中文声音，并把完整中文字幕压到画面上。

这不是简单的“翻译字幕”流程，而是一套视频本地化交付流程。目标输出应当可以直接用于自媒体、课程、企业培训、产品演示、知识解读等场景。

## 必须遵守的硬约束

- 保持原始画幅、分辨率、方向和帧率。原视频是 `16:9` 横屏，就不要改成 `9:16` 竖屏。
- 最终视频只保留中文音轨。不要把英文原声和中文配音混在一起。
- 中文音频必须跟随原视频时间轴。逐段合成、逐段放回原时间点，段落空白处保留静音。
- 不要把整段中文配音一次性整体拉伸到视频长度，这会导致音画漂移。
- 中文字幕需要直接压入画面，除非用户明确只要软字幕。
- 字幕不能随意省略。长句要缩小字号并按像素宽度换行，不要用省略号掐掉内容。
- 完成前必须验收：`ffprobe` 看参数，抽早中晚三帧看字幕和画幅。
- 如涉及公开视频下载，先确认用户拥有下载、处理或二创授权。

## 输入与输出

常见输入：

- 本地视频文件，例如 `source.mp4`
- 用户授权的视频链接
- 已有字幕或转写 JSON
- 用户指定的中文音色、字幕字号、输出文件名

推荐输出：

- `source.mp4`：原始视频，尽量保留
- `transcript.json`：带时间戳的原文转写
- `translations.json`：带时间戳的中文翻译
- `zh_timeline.wav`：按原视频时间轴排布的中文音频
- `sub_overlay.mov`：透明中文字幕层
- `localized-zh.mp4`：最终中文发布版视频

`translations.json` 推荐结构：

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

## 标准工作流

### 1. 确认授权和视频源

如果用户给的是 YouTube、Bilibili、网页视频或网盘链接，先确认是否有权下载、翻译、配音和发布。

下载时优先选择兼容性好的 H.264 + AAC 格式。如果用户反馈“有声音没画面”，优先检查是否下载成 AV1 或播放器不兼容编码。

### 2. 探测源视频

使用 `ffprobe` 或本仓库脚本：

```bash
python scripts/probe_media.py input.mp4
```

记录：

- 宽高
- 显示比例
- 视频时长
- 视频编码
- 音频编码
- 帧率
- 音轨数量

后续所有处理都以源视频时间轴为准。

### 3. 转写并保留时间戳

转写必须产出分段时间戳，至少包含：

- `start`
- `end`
- 原文文本

可以使用 Whisper、本地模型或第三方 API。不要只拿一整篇无时间戳文本，否则后续配音很容易错位。

### 4. 分段翻译

按段落或小组翻译，不要把全文一次性丢给翻译器。

翻译要求：

- 保留工具名、品牌名、人名、仓库名，例如 `Codex`、`Claude Code`、`OpenClaw`、`Hermes`、`OpenCode`、`Trae`、`Workbody`、`G-Stack`、`Graphify`、`Remotion`、`Hyperframes`
- 面向中文观众自然表达，不要机械直译
- 技术名词前后一致
- 如果用于发布，建议最后做一次专名校对

### 5. 生成中文时间轴音频

逐段生成中文 TTS，然后放回原始时间轴：

- 音频片段从对应 `start` 开始
- 如果片段短于原窗口，后面补静音
- 如果片段略长，优先局部轻微加速或小幅裁尾
- 不允许让前一段挤占后一段时间
- 最终导出音频长度应接近源视频总时长

这个步骤决定音画是否同步，是整个流程的核心。

### 6. 生成中文字幕层

优先生成一条透明字幕视频，再一次性 overlay 到源视频上。不要用几百个 PNG 输入叠加成超长 filter graph，这样很慢也很容易失败。

使用脚本：

```bash
python scripts/build_subtitle_overlay.py \
  --segments translations.json \
  --out sub_overlay.mov \
  --width 1280 \
  --height 720 \
  --duration 1753.756 \
  --font-size 19
```

字幕建议：

- 720p 横屏技术视频：`18-24px`
- 字幕底部居中
- 黑色半透明底
- 按像素宽度换行
- 不要截断句子

### 7. 合成最终视频

使用原视频画面、中文时间轴音频、中文字幕层合成：

```bash
python scripts/mux_localized_video.py \
  --source-video source.mp4 \
  --localized-audio zh_timeline.wav \
  --subtitle-overlay sub_overlay.mov \
  --out localized-zh.mp4
```

最终合成必须只映射中文音轨，不映射原英文音轨。

### 8. 发布前验收

至少检查：

```bash
python scripts/probe_media.py localized-zh.mp4
```

验收标准：

- 输出视频仍是原始画幅，例如 `1280x720`、`16:9`
- 只有一条音轨，且为中文音频
- 视频和音频时长基本一致
- 早、中、晚三张抽帧都有中文字幕
- 字幕没有溢出画面
- 字幕没有遮挡重要人物、产品或 UI
- 播放器中有画面、有声音、能正常拖动播放

## 可使用脚本

- `scripts/probe_media.py`：探测视频/音频结构
- `scripts/build_subtitle_overlay.py`：从时间戳 JSON 生成透明中文字幕层
- `scripts/mux_localized_video.py`：合成最终中文发布版视频

## 适配不同 AI 工具

原生支持 skill/plugin 的工具可以直接读取本目录。没有原生 skill 机制的工具，可以在项目规则文件中引用本 `SKILL.md`。

更多适配方式见：

- `references/cross-tool-adapters.md`
- `references/quality-checklist.md`

## 常见失败模式

- 把横屏视频改成竖屏
- 中文配音和英文原声同时存在
- 中文声音只有 16 分钟，画面却有 27 分钟
- 一整段中文音频被粗暴拉伸，越到后面越不同步
- 字幕太大，导致内容显示不完整
- 自动翻译把产品名、人名、工具名翻错
- 命令执行成功，但没有实际播放和抽帧检查

遇到以上问题，必须回到对应步骤修复，不要直接交付。
