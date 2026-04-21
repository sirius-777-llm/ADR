# ADR — Automated Documentary Rendering

ADR 是一套全自动纪录片短视频生成管线。给一个主题，输出一部带配音、字幕、BGM 的 16:9 横屏或 9:16 竖屏纪录片。

支持两种画幅：
- **HDAR**（默认 `h`）：1280×720 横屏 16:9
- **VDAR**（`v`）：720×1280 竖屏 9:16（自动切女声晓曼，面向中老年视频号）

## 架构（截至本 README 更新日）

```
主题输入
  │
  ├─ Step 1: 剧本 + 考证 + 画面规划
  │    题材基调分析 (GEMINI_3_1_FLASH_LITE) → 紧张/温暖/中性 情绪基调
  │    分镜规划师 (GEMINI_3_1_FLASH_LITE) → 动态决定 N 句分镜（6~22）
  │    斯皮尔伯格 AI (GEMINI_3_1_FLASH_LITE) → 旁白台词 (3 次重试保障)
  │    ★ 历史顾问 (CLAUDE_4_6_OPUS) → 时代视觉考证（服饰/建筑/器物/证据级外观）
  │    姜文 AI (GEMINI_25_FLASH) → 情绪标签 + 历史准确的画面提示词
  │    音频导演 (GEMINI_25_FLASH) → 从中文音色库智选（竖屏强制女声晓曼）
  │
  ├─ Step 2: 配音合成
  │    WeryAI Podcast API → 单次请求生成完整音轨
  │    content_status 轮询 (text-success → audio-success)
  │    text-fail 自动重试 5 次；全失败降级 Edge TTS 兜底
  │
  ├─ Step 3-5: 时间轴对齐
  │    Whisper (base 模型) 字级时间戳
  │    char_time_map 语速曲线 + 二分查找 + 线性插值 → 每句精确起止
  │    影视三层感知节奏：画面 → +0.2s 字幕 → +0.5s 配音（J-Cut）
  │
  ├─ Step 6: 并发媒体生成
  │    20 路线程池: N 张 AI 画作 (GEMINI_3_1_FLASH_IMAGE / Nano Banana 2) + 1 段 BGM
  │    全局 POST 节流锁 (5s 间隔, 防 Redis 限流)
  │    图片重做：同 prompt 最多 3 次 → 超过则 GEMINI_25_FLASH 重写 prompt 最多 2 次
  │    支持图片审批交互（Telegram InlineKeyboard）；`--skip-approval` 跳过
  │
  ├─ Step 6.5: 动态化（★ 新增，可选）
  │    触发：CLI `--with-motion` 或 tool 参数 `with_motion=true`
  │    WERYDANCE_2_0 × N 分镜并发（aspect 跟随 h/v）
  │    GEMINI_25_FLASH 为每分镜生成英文 motion prompt
  │    替换原 seg_N.mp4；per-scene 失败保留静态版，不中断流程
  │    代价：耗时 +5-10 min，费用 +≈$2.5/条
  │
  ├─ Step 7-9: 合成
  │    ffmpeg concat demuxer 拼接视频轨
  │    ASS 硬字幕烧录 (Arial Unicode MS)
  │    -itsoffset J-Cut 音画错位
  │    配音 vol=1.5 + BGM vol=0.25 amix 混音；CRF 20 + medium preset
  │
  └─ Step 10: 推送
       短标题 + 社媒文案 (GEMINI_25_FLASH) → Telegram 一键复制按钮
       ★ 专属封面 (GEMINI_3_1_FLASH_IMAGE) → 中老年视频号红金大字报风，留白叠标题
       成片 mp4 发送 Telegram（requests + curl 兜底 3 次重试）
       全流程耗时统计
```

## 模型分工速查（实测代码，README 跟代码同步后）

| 岗位 | 模型 | 备注 |
|---|---|---|
| 题材基调 / 分镜规划 / 台词生成 | `GEMINI_3_1_FLASH_LITE` | 最便宜，适合大量结构化输出 |
| **历史顾问（视觉考证）** | **`CLAUDE_4_6_OPUS`** | 唯一升级到 Opus 的岗位，防穿帮 |
| 姜文 / 音频导演 / prompt 重写 / 字幕拆句 / 社媒文案 / motion prompt | `GEMINI_25_FLASH` | 通用性价比 |
| 图片生成（分镜图 + 封面） | `GEMINI_3_1_FLASH_IMAGE`（Nano Banana 2） | WeryAI 中转 |
| 图生视频（Step 6.5） | `WERYDANCE_2_0` | 可选，默认关 |
| 配音 | WeryAI Podcast API（晓曼 / 国栋 等）| text-fail 降级 Edge TTS |

## 关键设计决策

- **全部 LLM 调用通过 WeryAI `/chat/completions` 统一中转**（消除多供应商故障点）
- **历史顾问单独用 Claude Opus**：历史穿帮成本最高，用最强模型兜底；其他岗位用 Gemini 省钱
- **Whisper 时间对齐**：从贪心合并改为语速曲线插值，准确度显著提升
- **动态化可选**：WERYDANCE 模型把 PPT 切换感变电影感，成本 10x 速度 2x，默认关
- **专属封面独立生成**：Step 10 里从 9 张分镜里不是随机抽两张，而是专门出一张中老年优化封面

## 快速开始

```bash
# 设置环境变量
export WERYAI_API_KEY="your-key"
export TG_BOT_TOKEN="your-bot-token"
export TG_CHAT_ID="your-chat-id"

# 安装依赖
pip install requests faster-whisper

# 运行
python3 run_adr_v8.py "1924年泰戈尔访华"
```

## 环境变量

WERYAI_API_KEY — 必填, WeryAI API 密钥
TG_BOT_TOKEN — 必填, Telegram Bot Token
TG_CHAT_ID — 必填, Telegram Chat ID (状态推送)
OUTPUT_DIR — 可选, 输出目录, 默认 /tmp/adr_v8_{timestamp}

## 系统依赖

Python 3.10+, ffmpeg/ffprobe, requests, faster-whisper

## 关键技术决策

1. 单次 Podcast 请求: 9 句合并为一次 API 调用, 避免并发限流
2. content_status 轮询: WeryAI Podcast 必须检查 content_status 而非 task_status
3. 语速曲线插值: char_time_map 记录累积字数→时间映射, 二分查找定位每句起止
4. 全局 POST 节流: threading.Lock + 5s 间隔, 防 Redis 限流
5. 影视三层感知: 画面先出 → +0.2s 字幕预读 → +0.5s 配音确认
6. 历史考证注入: 画面提示词受时代视觉约束, 不凭空生成
7. Gemini 统一: 全链路 Gemini 系列, 消除多供应商故障点

## License

Apache 2.0
