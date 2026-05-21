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
| 2026-05-21 | IP 调用统计 + 推荐 (F) | schema v1.2 加 usage_count + 跑后自动 increment + _recommend_related_ips + tools/show_ip_stats.py CLI |
| 2026-05-21 | NO TEXT IN FRAME 补强 | _adsd_almighty_audio_dub_prompt + _adsd_meta_grid_call_prompt 加英文 ABSOLUTELY NO TEXT IN FRAME ban，修易筋经 00:48 内嵌字幕 |
| 2026-05-21 | action_b 题材触发优化 | script-gen prompt 鼓励武侠/对抗题材主动出 ≥1-2 个 action_b（之前易筋经 0 个 action_b 因 LLM 保守）|
| 2026-05-21 | LLM 智能召唤标签 | script-gen LLM 同时推 meta_grid_costume/pose 字段 + scene 注入 IP costume/pose 池，_infer_* 优先读 LLM 标签，规则兜底 |
| 2026-05-21 | AUTO-IP · ADR 主流程自动孵化 | step1 后扫描脚本无 IP speaker → LLM 孵化（含 voice_asset 智能匹配 + 全字段填充 + qa_status=auto_generated_pending_review）·env ADR_AUTO_INCUBATE_IP 控制 · 实测苏东坡 ✓ |
| 2026-05-21 | duration=3 bug fix (P0) | duration 优化下限 3 越过 WERYDANCE 硬限 4，整 run 39min 挂掉；回收下限 → 4 + 双保险 max(4) · 实测笑傲江湖 turn 5/9 status 1002 root cause |
| 2026-05-21 | step7 防御层 | 缺失 seg 时用 img_path 现场补 still seg + 不可恢复时从 script 移除 turn，避免 ffprobe 整 run 挂掉 |
| 2026-05-21 | P0 action_b 标注 bug fix | _infer_turn_type line 451 武戏命中错返 narrated_b → 改 action_b + _is_action_shout 短喊招检测（武侠/体育/战争 全覆盖）+ 兜底收紧 ≤12 字防误标长教学 dialog · 13/13 case 通过 |
| 2026-05-21 | P1 武戏密度 LLM 化 | topic_decomposition 加 action_density_hint (low/medium/high) + recommended_action_b_count + script-gen prompt 按密度给 min/max action_b 硬指标 + 武戏 ≥3 必须连续 2 个组成节拍 · 笑傲江湖实测 high/4 |
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
| ~~AUTO-IP · ADR 主流程自动孵化 IP~~ | ~~1h~~ | ~~★★~~ | ✅ shipped 2026-05-21 | step1 后扫描自动孵化 + qa_status 待审标记 |
| D · 角色弧线版本 | 3h | ★★ | planned | 曹操_青年/中年/晚年 多版本，LLM 看时代自动选 |
| E · 多人物互动 IP | 4h | ★★ | planned | 双人卡 (曹操+刘备) 同框 IP，含对峙/煮酒姿势 |
| ~~F · IP 调用统计 + 推荐~~ | ~~1h~~ | ~~★★~~ | ✅ shipped 2026-05-21 | usage_count + _recommend_related_ips + show_ip_stats.py |
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
| ~~LLM 智能召唤标签~~ | ~~1.5h~~ | ~~★★~~ | ✅ shipped 2026-05-21 | script-gen LLM 同时推 meta_grid_costume/pose 字段 |
| ~~action_b LLM 标注 bug~~ | ~~1h~~ | ~~★★~~ | ✅ shipped 2026-05-21 | _infer_turn_type 修正 + _is_action_shout + density LLM 化 |
| 题材泛化验证 | 30min/题材 | ★ | planned | 跑科比/鲁迅/苏东坡/钱学森等验证 IP+人设符稳定性 |
| resume 工具 e2e test | 1h | ★ | planned | tools/rerun_downstream.py 加自动测试套件 |

### 🐛 2026-05-21 笑傲江湖重跑发现的 bug

| Bug | 严重度 | 工程量 | 状态 | 现象 + 修复方向 |
|-----|--------|--------|------|----------------|
| ~~**B1 音量太低**~~ | ~~★★★ P0~~ | ~~1h~~ | ✅ shipped 2026-05-21 | step9 amix 默认归一化压人声 → normalize=0 + weights 显式权重 + voice 1.0→2.0 + BGM 0.85→0.4，两阶调音通过 |
| ~~**B2 meta_grid 12 宫格漏进**~~ | ~~★★★ P0~~ | ~~1.5h~~ | ✅ shipped 2026-05-21 | step7 防御层缺失 seg 时用 meta_grid 当 still 导致 4×3 grid 漏入画面 → 检测 meta_grid_ 文件名 + 优先用邻 turn 合法图/cover.jpg 兜底 + prompt 强化禁止复刻 grid + negative_prompt 加 grid/split/panel ban |
| ~~**B3 内嵌字幕**~~ | ~~★★★ P0~~ | ~~30min~~ | ✅ shipped 2026-05-21 | meta_grid_call prompt 强化禁止复刻参考图中文标签 + negative_prompt 强化 text ban，重跑笑傲江湖未复现 |
| **B4 武戏无 SFX 配音** | ★★ P1 | 2h | planned | action_b 是 motion-only 无 audio，缺打斗音效（拳风/兵器格挡/落地声）。方案：action_b 走 generate_audio=true 让 WERYDANCE 自配 SFX，或本地 SFX 库 + step9 时间轴叠加 |
| ~~**B5 LLM 把场景描述当 speaker**~~ | ~~★★ P1~~ | ~~1h~~ | ✅ shipped 2026-05-21 | prompt 加 speaker 铁律 + _sweep_speaker_field 后处理 (bad_keywords 检测 + 从 bad speaker 提取已知角色 + role_candidates fallback) · 7/7 case 通过 |
| ~~**B6 短喊招漏关键词**~~ | ~~★ P2~~ | ~~15min~~ | ✅ shipped 2026-05-21 | _is_action_shout 加 再来/换我/还击/反攻/拦住/挡住/拼了/决胜 等 16 个攻势/反击/换场词 · 6/6 case 通过 |

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

**当前 top 3 (2026-05-21 P0/P1 已收尾):**
1. **B4 武戏 SFX** (2h) — action_b 无打斗音效，影响实际观感
2. **PR-A · merged_a 合并跑** (4-5h) — 大杀器，省 8-12min/run
3. **AUTO-IP 待审 IP review** — 令狐冲/苏东坡/风清扬 抽查质量

今日 ship 清单 (10+ 件):
  · AUTO-IP 主流程孵化 + hotfix 占位符过滤
  · LLM 智能召唤标签
  · P0 三连 (B1 音量 / B2 12 宫格 / B3 字幕)
  · P1 两个 (B5 speaker 校验 / B6 喊招扩词)
  · duration=3 bug fix + step7 防御层 + cover.jpg 兜底
  · action_b 标注 bug + 武戏密度 LLM 化

零工 / 已可立刻用：
- 跨题材召唤 (用 IP 即可)
- LLM 智能召唤标签 (现在 B 已 ship，可做)
