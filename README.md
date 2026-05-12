# ADR — Automated Documentary Rendering

ADR 是一套自动纪录片生成管线。输入一个主题或带时间戳的台词，输出带画面、配音、字幕、BGM 的横屏或竖屏视频，并把过程状态和成片推送到 Telegram。

本 README 是 ADR 的产品契约：模式名、默认行为、质量兜底和禁止误触发规则必须和代码保持一致。每次改动 `run_adr_v8.py` 或 Telegram 启动器时，都要同步更新这里。

## 当前模式

| 模式 | 画幅 | 触发 | 含义 |
|---|---:|---|---|
| `HDAR` | 16:9 | `h` | 横屏纪录片，默认模式 |
| `VDAR` | 9:16 | `v` | 竖屏纪录片，偏短视频发布 |
| `HADS` | 16:9 | `h --with-motion` | 横屏动态纪录片，WeryDance 逐分镜动态化 |
| `VADS` | 9:16 | `v --with-motion` | 竖屏动态纪录片，WeryDance 逐分镜动态化 |
| `HADSD` | 16:9 | `h --ads-dialogue` | 横屏多角色对话纪录片 |
| `VADSD` | 9:16 | `v --ads-dialogue` | 竖屏多角色对话纪录片 |

重要边界：

- `HADS/VADS` 只表示“动态纪录片”，不等于现场记者。
- 只有显式传 `--ads-reporter`，或用户明确说“拟现场记者 / 战地记者 / dispatch / 第一人称记者 / POV 记者”，才进入记者 POV。
- `--ads-reporter` 会自动开启 `--with-motion`，但 `--with-motion` 不会反向开启记者。
- `--ads-dialogue` 和 `--ads-reporter` 互斥；多角色对话优先。

## 默认策略

| 能力 | 默认 | 说明 |
|---|---:|---|
| GPT Image 2 故事板 | 开 | 主线分镜优先生成故事板和网格故事板 |
| Storyboard reference motion | 开 | WeryDance 动态化优先吃 clean keyframe / storyboard 参考 |
| Motion action storyboard | 开 | 每个分镜生成动作起点、过程、终点，避免人物发呆 |
| Motion bridge refs | 开 | 为关键镜头补终点参考图，提升动作幅度 |
| WeryDance 字幕 | 开 | 默认交给 WeryDance 生成字幕，ASS 硬字幕作为兜底 |
| 音色资产库 | 开 | 男声默认罗翔，女声默认 BY2，可用环境变量覆盖 |
| 严格音色锁定 | 开 | Motion prompt 会显式锁定声音资产和人物性别 |
| Telegram 进度 | dashboard | TG 只保留一条可编辑进度面板，显示进度条、当前阶段和最近日志 |
| BGM-only | 关 | `--bgm-only` 跳过 TTS，只保留画面、字幕、BGM |

## 架构

```text
主题 / 台词输入
  |
  |-- Step 1: 剧本、考证、分镜
  |   |-- 题材分析：文化、地域、年代、服饰、负面禁令
  |   |-- 台词生成或外部台词解析：支持带时间戳文本
  |   |-- 历史顾问：校准时代视觉，避免文化和年代穿帮
  |   |-- 分镜提示词：画面、角色、镜头、情绪、动作
  |
  |-- Step 2: 配音 / 音色
  |   |-- 普通 ADR：Podcast/TTS 生成整段音轨
  |   |-- ADSD：逐 turn 配音，支持口型同步
  |   |-- WeryDance audio-dub：可用音色资产参考音频完成视频内配音
  |
  |-- Step 3: 时间轴
  |   |-- Whisper 字级时间戳
  |   |-- 外部带时间戳台词优先
  |   |-- 字幕、画面、音频按分镜对齐
  |
  |-- Step 4: 故事板
  |   |-- GPT Image 2 单镜故事板
  |   |-- 4K storyboard grid / 多 storyboard fallback
  |   |-- crop QA，避免切到相邻格
  |
  |-- Step 5: 静态画面和封面
  |   |-- 分镜图并发生成
  |   |-- 失败重试，必要时重写 prompt
  |   |-- Telegram 图片审批可选
  |
  |-- Step 6.5: WeryDance 动态化
  |   |-- clean keyframe 优先，其次 annotated storyboard 实验模式
  |   |-- 每镜头 motion prompt + 动作计划 + 可选终点参考
  |   |-- 失败镜头保留静态兜底，不中断整片
  |
  |-- Step 7: 合成
  |   |-- ffmpeg 拼接视频
  |   |-- WeryDance 字幕优先，ASS 字幕兜底
  |   |-- 配音、BGM 混音
  |
  `-- Step 8: QA 和交付
      |-- motion_qa.json
      |-- storyboard / crop / caption / voice QA
      |-- Telegram 推送成片和文案
```

## 快速开始

```bash
export WERYAI_API_KEY="your-key"
export TG_BOT_TOKEN="your-bot-token"
export TG_CHAT_ID="your-chat-id"

python3 run_adr_v8.py "1924年泰戈尔访华" h
python3 run_adr_v8.py "黄仁勋CMU毕业演讲核心内容" h --with-motion
python3 run_adr_v8.py "1915年二十一条最后通牒" v --ads-reporter
python3 run_adr_v8.py "AI时代就业市场访谈" h --ads-dialogue
python3 run_adr_v8.py "江南春日风物" v --bgm-only --with-motion
```

## 常用参数

| 参数 | 用途 |
|---|---|
| `h` / `v` | 横屏 16:9 / 竖屏 9:16 |
| `--with-motion` | 开启 WeryDance 动态化 |
| `--ads-reporter` | 开启第一人称现场记者 POV |
| `--no-ads-reporter` | 强制禁止 reporter |
| `--ads-dialogue` | 开启多角色对话纪录片 |
| `--adsd-lip-sync` | ADSD 口型同步实验 |
| `--bgm-only` | 无旁白，仅画面、字幕、BGM |
| `--skip-approval` | 跳过 Telegram 图片审批 |
| `--speaker <id:name>` | 指定 Podcast 音色 |

## 关键环境变量

| 变量 | 默认 | 用途 |
|---|---:|---|
| `ADR_GPT_IMAGE2_STORYBOARD` | `1` | 开关故事板 |
| `ADR_DEFAULT_STORYBOARD_GRID` | `1` | 开关默认 storyboard grid |
| `ADR_STORYBOARD_REFERENCE_MOTION` | `1` | 动态化使用故事板参考 |
| `ADR_STORYBOARD_ANNOTATED_MOTION` | `0` | 使用 annotated storyboard 喂 WeryDance |
| `ADR_MOTION_ACTION_STORYBOARD` | `1` | 动作计划故事板 |
| `ADR_MOTION_BRIDGE_REFS` | `1` | 终点关键帧参考 |
| `ADR_WERYDANCE_CAPTIONS` | `1` | WeryDance 字幕优先 |
| `ADR_DEFAULT_MALE_VOICE_ASSET` | `external_luo_xiang_xyma_001` | 默认男声音色资产 |
| `ADR_DEFAULT_FEMALE_VOICE_ASSET` | `external_by2_e7gn_001` | 默认女声音色资产 |
| `ADR_DEFAULT_VOICE_ASSET` | 空 | 全局强制默认音色资产 |
| `ADR_MOTION_VOICE_STRICT_LOCK` | `1` | 严格锁定音色和人物性别 |
| `ADR_ADS_REPORTER_ALLOW_ENV` | 空 | 允许环境变量触发 reporter，默认不允许 |
| `ADR_ADS_REPORTER` | 空 | reporter 环境开关，需配合上一项 |
| `ADR_TG_PROGRESS_MODE` | `dashboard` | TG 推送模式：`dashboard` / `compact` / `verbose` / `silent` |
| `ADR_TG_DIGEST_INTERVAL_SEC` | `120` | compact 模式下过程摘要最小间隔 |
| `ADR_TG_DASHBOARD_EDIT_INTERVAL_SEC` | `8` | dashboard 模式下进度面板最小编辑间隔 |
| `ADR_GPT_IMAGE2_STORYBOARD_GRID_SUBMIT_STAGGER` | `12` | storyboard grid 任务错峰提交间隔，避免同时请求 |
| `ADR_GPT_IMAGE2_STORYBOARD_GRID_POLL_WORKERS` | `20` | storyboard grid 提交后并发轮询/下载/裁剪 worker 数 |
| `ADR_GPT_IMAGE2_STORYBOARD_SUBMIT_STAGGER` | `12` | 单图 storyboard fallback 错峰提交间隔 |
| `ADR_GPT_IMAGE2_STORYBOARD_POLL_WORKERS` | `20` | 单图 storyboard fallback 并发轮询/下载 worker 数 |
| `ADR_MOTION_BRIDGE_REFS_SUBMIT_STAGGER` | `12` | motion bridge end keyframe 错峰提交间隔 |
| `ADR_MOTION_BRIDGE_REFS_POLL_WORKERS` | `20` | motion bridge end keyframe 并发轮询/下载 worker 数 |

## Telegram 进度策略

默认 `dashboard` 模式下，ADR 只发一条可编辑进度面板，后续用 Telegram `editMessageText` 原地更新，类似软件安装进度：

- 面板内容：主题、阶段、百分比、进度条、当前状态、最近日志、更新时间。
- 强制刷新：启动、剧本、主音轨、故事板、动态化、合成、发布门禁、成片、耗时统计、告警和错误。
- 限频刷新：普通过程日志最多每 8 秒编辑一次，避免 Telegram API 限流。
- 最终视频、封面、社媒文案、复制按钮仍单独发送，因为这些是交付物，不应该被进度面板覆盖。

`compact` 模式保留为备用，会把过程信息分为三层：

- 立即发送：启动、剧本完成、主音轨完成、故事板完成、动态化启动/完成、视频拼接、发布门禁、最终成片、耗时统计、所有告警和错误。
- 合并摘要：单张图完成、单个分镜动态化成功、Podcast task_id、轮询类信息、重复审批进度。
- 本地日志：所有细节仍写入 stdout/log，调试时可设 `ADR_TG_PROGRESS_MODE=verbose` 恢复全量推送。

目标是让 TG 对话框里能直接看到“现在跑到哪、有没有风险、最终文件在哪里”，不需要在几十条过程消息里捞结果。

## 音色资产库

音色资产配置位于 `voice_assets/voice_assets.json`。当前库中包含候选资产：

- `external_luo_xiang_xyma_001`：罗翔，默认男声。
- `external_by2_e7gn_001`：BY2，默认女声。
- `external_xu_zhiyuan_xyma_001`：许知远，访谈/文化类备选。
- `external_huang_renxun_fzh_001`：黄仁勋，英文科技领袖演讲备选。

外部人物声音默认只允许内部测试和分析；公开发布、商业用途、拟真冒充必须另行做权利审查。

## QA 检查点

每次改管线后至少验证：

- `python3 -m py_compile run_adr_v8.py`
- HADS 不带 `--ads-reporter` 时，日志必须显示 `HDAR/VDAR`，不能出现“拟现场记者”。
- `motion_qa.json` 里应记录参考图数量、字幕策略、音色策略。
- storyboard crop QA 不能把两个分镜切在同一张输出里。
- WeryDance 字幕失败时，ASS 兜底必须仍能合成。
- 自定义音色任务要检查声音性别、画面人物性别、台词内容三者一致。

## README 更新规则

README 只写已经落地并通过基础 QA 的能力，不写愿景。每次新增默认开关或改变模式含义时，要同步更新四处：

- `当前模式`
- `默认策略`
- `常用参数` 或 `关键环境变量`
- `QA 检查点`

任何会影响 TG bot 调用判断的规则，也要同步更新 `/Users/wekoidubai/telegram-claude-bot/tools/registry.py`。

## License

Apache 2.0
