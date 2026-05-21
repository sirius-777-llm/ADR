# ADR ROADMAP

> ADR (Automated Documentary Rendering V8) 项目 backlog · 跨 session 持久化
> 任何 Claude session 启动时优先查这个文件 + memory/project_adr_backlog.md

Last updated: 2026-05-21

---

## 🚀 已 Ship (Recent)

| 日期 | PR/改动 | 说明 |
|------|---------|------|
| 2026-05-20 | silent_b PR | a_roll/narrated_b/silent_b 三类 turn 数据模型 + LLM prompt 改造 + step9 BGM 动态浮起 |
| 2026-05-20 | Bug A-E fix | BGM 平衡 / per-part loudnorm / 字幕 ASR 对齐 / BGM aloop / 字幕 SUB_GAP |
| 2026-05-20 | 人设符 PR (character_meta_grid) | 4×3 中文标签 grid 取代切片 panel，召唤式 prompt |
| 2026-05-20 | 4 个减时间方向 + bug fix | skip sidecar QA / character_sheet / storyboard_grid / meta_grid 缓存 |
| 2026-05-21 | Speaker IP Card | speaker 升级为完整角色档案，8 个 seed (曹操/刘备/司马懿/旁白/科比/乔丹/鲁迅/辜鸿铭) |
| 2026-05-21 | Speaker IP A (AI 孵化) | tools/create_speaker_ip.py，给名字+简介自动生成完整 IP + meta_grid，已测杜甫 |
| 2026-05-21 | Speaker IP B (自学习) | usage_history 跑后回写 IP，下次 LLM 注入摘要避免重复 |
| 2026-05-21 | Speaker IP C (关系网络) | IP 加 relationships 字段，5 个种子角色补上 (曹操/刘备/司马懿/科比/乔丹)，script-gen prompt 注入关系上下文 |
| 2026-05-21 | 横屏字幕换行 fix | _wrap_card max_width 14.5 → SUBTITLE_MAX_CHARS+2，避免 LLM 切的 16 字段被强制 \N 换行 |
| 2026-05-21 | BGM vocal 自动检测 + retry | _bgm_contains_vocals whisper ASR 检测，含 lyrics 自动重试 (WERYAI music 偶尔忽略 "no vocals") |
| 2026-05-21 | resume tool --regen-bgm flag | 单独重生成 BGM，其他物料复用，针对 BGM 含 vocal 等场景秒修 |
| 2026-05-21 | Era LLM template (主路径) | _llm_infer_meta_grid_template + _resolve_meta_grid_template，LLM 推断 era + 4 类标签集，写入 IP cache 跨片复用，修「南京银行出古装」bug |
| 2026-05-21 | ERA_TEMPLATES 预设 + 兜底链 | 7 个 era 预设 (historical/contemporary_corporate/modern_athlete/modern_scholar/future_tech/...) + costume/pose 智能匹配 |
| 2026-05-21 | LLM 阶段 1 topic_decomposition | _llm_topic_decomposition + topic_cache，一次 LLM 出 era/bgm_style/role/director/cover/is_action_topic 多字段 |
| 2026-05-21 | LLM 阶段 2 BGM 接入 | generate_bgm 用 LLM 推断 bgm_style + instruments + mood，替换 8 硬关键词分支 |
| 2026-05-21 | LLM 阶段 3 role/director/action 标记 | _adsd_role_candidates / _storyboard_grid_prompt / script-gen 输出 is_action_scene 字段 |
| 2026-05-21 | Spike action 武戏天花板验证 | 4-panel multi-ref + kinetic prompt + 10s 武戏密度明显比 baseline 强（大哥确认）|
| 2026-05-21 | action_b turn_type PR (4b) | 第四类 turn (武戏)：4-panel multi-ref + duration 10s + kinetic prompt + LLM 自动标 |
| 2026-05-21 | 非 ADSD action 强化 (阶段 5) | _motion_action_block 检测 is_action_scene → 注入 kinetic prompt |
| 2026-05-21 | duration 计算优化 | api_dur 下限 5s → 3s + tts_dur+0.3 buffer，短 dialogue 处理时长降 30-40% |
| 2026-05-21 | IP 版本管理 (I) | ADR_IP_SCHEMA_VERSION="1.1" + _migrate_speaker_ip 加载时自动迁移，9 个 IP 已 v1.1 |
| 2026-05-20 | TG deliver 假阴性 fix | status=200 后验证 body {"ok":true,"result":{}} |
| 2026-05-20 | tools/rerun_downstream.py | 跳过 step1-66 跑下游，10x 调试加速 |

---

## ⏳ Planned (按优先级)

### 角色库扩展

| 项目 | 工程量 | ROI | 状态 | 备注 |
|------|--------|-----|------|------|
| ~~A · AI 自动孵化 IP~~ | ~~2h~~ | ~~★★★~~ | ✅ shipped 2026-05-21 | tools/create_speaker_ip.py |
| ~~B · 自学习 usage_history~~ | ~~1.5h~~ | ~~★★★~~ | ✅ shipped 2026-05-21 | _record_speaker_usage_history + prompt 注入 |
| ~~C · 角色关系网络~~ | ~~1h~~ | ~~★★★~~ | ✅ shipped 2026-05-21 | IP relationships + _build_speaker_ip_context_for_script |
| D · 角色弧线版本 | 3h | ★★ | planned | 曹操_青年/中年/晚年 多版本，LLM 看时代自动选 |
| E · 多人物互动 IP | 4h | ★★ | planned | 双人卡 (曹操+刘备) 同框 IP，含对峙/煮酒姿势 |
| F · IP 调用统计 + 推荐 | 1h | ★★ | planned | 跟踪频次，推荐相关 IP |
| G · IP 管理 CLI 工具 | 2h | ★ | planned | tools/ip_manager.py 列出/编辑/创建 IP |
| H · IP 质量评分 | 2h | ★ | planned | LLM 评估视觉/音色/性格契合，写 IP 跟踪 |
| ~~I · IP 版本管理~~ | ~~30min~~ | ~~★~~ | ✅ shipped 2026-05-21 | ADR_IP_SCHEMA_VERSION + _migrate_speaker_ip |

### LLM 化 + 武戏强化 (2026-05-21 议定，5.5-6.5h 总)

| 项目 | 工程量 | ROI | 状态 | 备注 |
|------|--------|-----|------|------|
| ~~阶段 1-5 (LLM 化 + 武戏)~~ | ~~5.5h~~ | ~~★★★~~ | ✅ shipped 2026-05-21 | 全部 6 阶段已 ship |
| ✗ image-to-video 升 almighty | - | - | rejected | 保留作 fallback (endpoint 冗余容灾) |

### 减时间优化

| 项目 | 工程量 | ROI | 状态 | 备注 |
|------|--------|-----|------|------|
| **PR-A · merged_a 合并跑** | 4-5h | ★★★ | planned | 同 speaker 连续 turn 合并 almighty，API 调用 12→6-8 (Spike 2 已验证) |
| meta_grid 缓存预热 | 30min | ★★ | planned | 跑 driver 给常用 speaker 预生成 meta_grid 入缓存 |
| 0.5s submit interval 重测 | 5min | ★★ | planned | 用户之前实测过不行，现在 ref 减少可能能用 |
| ~~duration 计算优化~~ | ~~30min~~ | ~~★★~~ | ✅ shipped 2026-05-21 | api_dur 下限 5s→3s + tts_dur+0.3 |
| voice_asset upload 缓存 | 1h | ★ | planned | 按 sha256 缓存 weryai upload URL |
| WERYDANCE_2_0_FAST 主路径 | 30min+测 | ★ | planned | A/B 验证 FAST 质量是否够，省 30-40% step66 时间 |

### 其他方向

| 项目 | 工程量 | ROI | 状态 | 备注 |
|------|--------|-----|------|------|
| LLM 智能召唤标签 | 1.5h | ★★ | blocked-by-B | 看 IP usage_history 推荐召唤 costume/pose |
| 题材泛化验证 | 30min/题材 | ★ | planned | 跑科比/鲁迅/苏东坡/钱学森等验证 IP+人设符稳定性 |
| resume 工具 e2e test | 1h | ★ | planned | tools/rerun_downstream.py 加自动测试套件 |

---

## ✗ Deprecated (撤回方向)

| 方向 | 撤回原因 | 数据来源 |
|------|----------|----------|
| 12-panel grid micro-storyboard | Spike 3C 输出综合场景非按 panel 顺序 | Spike 3 |
| audio_ref 拼接 (>15s) | API 硬性限制 2-15s | Spike 1 |
| step6/step66 流水线化 | 收益 < 5min 不值得复杂度 | 之前 PM 分析 |
| meta_grid 2K 替代 4K | 质量明显降级 | 经验判断 |
| WERYDANCE 高优先 GPU quota | 需付费，非项目内 | - |

---

## 📌 PM 注释

**Session 重启 protocol:**
1. Claude 启动时先读 `memory/project_adr_backlog.md` 看 top 3 优先级
2. 再读这个 ROADMAP.md 看全量 backlog
3. 跟用户对齐当前方向（不直接跳进未做项）

**优先级判断标准:**
- ★★★ ROI 高 + 工程量 < 3h
- ★★ 中等 ROI 或工程量 3-5h
- ★ 长期价值或工具型

**当前 top 3 (2026-05-21 更新):**
1. PR-A · merged_a 合并跑 (4-5h) — 最大省时间，Spike 2 已验证
2. D · 角色弧线版本 (3h) — 同 speaker 多年龄/阶段
3. E · 多人物互动 IP (4h) — 双人卡同框

零工 / 已可立刻用：
- 跨题材召唤 (用 IP 即可)
- LLM 智能召唤标签 (现在 B 已 ship，可做)
